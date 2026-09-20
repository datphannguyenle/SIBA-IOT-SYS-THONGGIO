"""Offline safeguards for the bounded VENT-008 updater; no network calls."""
import copy
import json
import pathlib
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "deploy/thingsboard"))
import update_vent_demo as update


class UpdateSafetyTest(unittest.TestCase):
    def test_target_ids_are_existing_demo_only(self):
        self.assertEqual(update.TARGETS, (
            ("widget", "/api/widgetType", "b9fa9280-b26a-11f1-83ad-9912edc644d2"),
            ("dashboard", "/api/dashboard", "b9ff4d70-b26a-11f1-83ad-9912edc644d2")))

    def test_payload_preserves_identity_version_and_ownership(self):
        live = {"id": {"id": update.DASHBOARD_ID}, "version": 1, "tenantId": {"id": "tenant"},
                "title": update.DASHBOARD_TITLE, "configuration": {"old": True}, "metadata": "keep"}
        original = copy.deepcopy(live)
        intended = {"configuration": {"states": ["a", "b"]}, "title": "must not replace"}
        actual = update.update_body("dashboard", live, intended)
        self.assertEqual(live, original)
        self.assertEqual(actual["configuration"], intended["configuration"])
        for key in ("id", "version", "tenantId", "title", "metadata"):
            self.assertEqual(actual[key], live[key])

    def test_fingerprint_detects_concurrent_metadata_change(self):
        obj = {"id": "a", "version": 2, "description": "original"}
        changed = dict(obj, description="new")
        self.assertNotEqual(update.fingerprint(obj), update.fingerprint(changed))
        self.assertNotEqual(update.fingerprint(obj), update.fingerprint(dict(obj, version=3)))

    def test_widget_default_config_normalization_is_semantic(self):
        obj = {"descriptor": {"defaultConfig": '{"a": 1, "b": 2}'}}
        intended = {"descriptor": {"defaultConfig": '{"b":2,"a":1}'}}
        self.assertTrue(update.content_matches("widget", obj, intended))
        intended["descriptor"]["defaultConfig"] = '{"b":2,"a":0}'
        self.assertFalse(update.content_matches("widget", obj, intended))

    @patch.object(update, "write_json")
    def test_timeout_records_intent_and_never_retries(self, write):
        class Writer:
            calls = 0

            def request(self, *args):
                self.calls += 1
                self_test.assertTrue(write.called, "intent must precede network request")
                raise TimeoutError("sensitive response must not appear")

        self_test = self
        writer = Writer()
        record, entry = {"mutations": []}, {"kind": "widget"}
        with self.assertRaisesRegex(RuntimeError, "indeterminate") as error:
            update.checked_write(writer, "/api/widgetType", {}, entry, record)
        self.assertNotIn("sensitive", str(error.exception))
        self.assertEqual(writer.calls, 1)
        self.assertEqual(len(record["mutations"]), 1)
        self.assertIn("do not retry", entry["status"])

    @patch.object(update, "write_json")
    def test_http_failure_does_not_print_response_or_retry(self, write):
        class Writer:
            calls = 0

            def request(self, *args):
                self.calls += 1
                return 409, "response body must remain private"

        writer = Writer()
        with self.assertRaisesRegex(RuntimeError, "HTTP 409") as error:
            update.checked_write(writer, "/api/dashboard", {}, {}, {"mutations": []})
        self.assertNotIn("private", str(error.exception))
        self.assertEqual(writer.calls, 1)

    def rollback_case(self, concurrent_edit=False):
        old = {
            "widget": {"id": {"id": update.WIDGET_ID}, "descriptor": {"defaultConfig": "{}"},
                       "name": "old", "description": "old", "deprecated": False, "scada": False},
            "dashboard": {"id": {"id": update.DASHBOARD_ID}, "configuration": {"version": "old"}},
        }
        current = copy.deepcopy(old)
        current["widget"]["name"] = "new"
        current["dashboard"]["configuration"] = {"version": "new"}
        record = {"written_fingerprints": {k: update.fingerprint(v) for k, v in current.items()}, "mutations": []}
        if concurrent_edit:
            current["dashboard"]["configuration"] = {"version": "another-owner"}
        sent, written = [], []

        class FakeTB:
            def __init__(self, **kwargs):
                self.token = "offline-test-only"

            def get_ok(self, path):
                return copy.deepcopy(current["widget" if "/widgetType/" in path else "dashboard"])

            def request(self, path, method, body):
                kind = "widget" if path == "/api/widgetType" else "dashboard"
                sent.append((path, method))
                current[kind] = copy.deepcopy(body)
                return 200, copy.deepcopy(body)

        backup = {"objects": old, "protected": {}}
        with patch.object(update, "GuardedTB", FakeTB), patch.object(update, "identity"), \
                patch.object(update, "snapshot", return_value={}), \
                patch.object(update, "BACKUP", SimpleNamespace(read_text=lambda **kw: json.dumps(backup))), \
                patch.object(update, "RECORD", SimpleNamespace(read_text=lambda **kw: json.dumps(record))), \
                patch.object(update, "write_json", side_effect=lambda path, value: written.append(copy.deepcopy(value))), \
                patch("builtins.print"):
            if concurrent_edit:
                with self.assertRaisesRegex(RuntimeError, "changed since this run"):
                    update.rollback()
            else:
                update.rollback()
        return old, current, sent, written

    def test_rollback_restores_in_reverse_order_without_deletes(self):
        old, current, sent, written = self.rollback_case()
        self.assertEqual(sent, [("/api/dashboard", "POST"), ("/api/widgetType", "POST")])
        self.assertEqual(current, old)
        self.assertTrue(written[-1]["rollback_protected_unchanged"])
        self.assertEqual(written[-1]["written_fingerprints"], {})

    def test_rollback_refuses_concurrent_edit_before_any_write(self):
        old, current, sent, written = self.rollback_case(concurrent_edit=True)
        self.assertEqual(sent, [])
        self.assertEqual(current["dashboard"]["configuration"], {"version": "another-owner"})


if __name__ == "__main__":
    unittest.main()
