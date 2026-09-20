"""Offline safeguards for the bounded VENT-008 updater; no network calls."""
import copy
import pathlib
import sys
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


if __name__ == "__main__":
    unittest.main()
