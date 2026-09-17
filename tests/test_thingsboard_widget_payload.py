"""VENT-006/007: kiểm payload widget/dashboard dựng cục bộ (không gọi mạng TB, không deploy)."""
import json
import pathlib
import re
import subprocess
import sys
import unittest

from webdriver_support import ROOT, Browser, StaticServer, geckodriver_path

BUILD = ROOT / "deploy/thingsboard/build"
sys.path.insert(0, str(ROOT / "deploy/thingsboard"))
import build_vent_demo  # noqa: E402
import vent_demo_common  # noqa: E402

NAMESPACE = "tb-widget-ns-test"


def namespace_css(css):
    """Mô phỏng cssParser của TB: thêm tiền tố namespace cho từng selector, kể cả trong @media."""
    def scope(block):
        out = []
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", block):
            parts = ",".join(".%s %s" % (NAMESPACE, s.strip()) for s in selector.split(","))
            out.append("%s{%s}" % (parts, body))
        return "".join(out)
    result = []
    for media, inner, plain in re.findall(r"(@media[^{]+)\{((?:[^{}]*\{[^{}]*\})*)\s*\}|([^@{}]+\{[^{}]*\})", css):
        result.append("%s{%s}" % (media, scope(inner)) if media else scope(plain))
    return "\n".join(result)


class PayloadStaticTest(unittest.TestCase):
    def setUp(self):
        self.widget = json.loads((BUILD / "widget_type.json").read_text())
        self.dashboard = json.loads((BUILD / "dashboard.json").read_text())

    def test_build_is_up_to_date_and_valid(self):
        subprocess.run([sys.executable, "build_vent_demo.py", "--check"], cwd=ROOT / "deploy/thingsboard", check=True,
                       capture_output=True)
        self.assertEqual(build_vent_demo.validate(self.widget, self.dashboard), [])

    def test_identity_and_isolation(self):
        self.assertEqual(self.widget["fqn"], "siba_vent_demo.vent_demo_view")
        self.assertNotIn("id", self.widget)
        self.assertEqual(self.widget["descriptor"]["type"], "static")
        self.assertEqual(self.dashboard["title"], "DB-30-VEN-DETAIL-V1-DEMO")
        self.assertNotIn("id", self.dashboard)
        c = self.dashboard["configuration"]
        self.assertEqual(list(c["states"]), vent_demo_common.STATES)
        self.assertTrue(c["states"]["default"]["root"])
        self.assertEqual(c["entityAliases"], {})
        self.assertEqual(c["settings"]["stateControllerId"], "default")
        for w in c["widgets"].values():
            self.assertEqual(w["typeFullFqn"], "tenant.siba_vent_demo.vent_demo_view")
            self.assertEqual(w["config"]["datasources"], [])
        text = json.dumps([self.widget, self.dashboard], ensure_ascii=False)
        for forbidden in ("siba_custom_ui", "entityAliasId", "assignedCustomers", "sendOneWayRpc", "sendTwoWayRpc",
                          "/api/plugins", "/api/rpc", "X-Authorization", "password", "refreshToken"):
            self.assertNotIn(forbidden, text)
        self.assertIn("DEMO DATA", text)

    def test_guard_blocks_everything_but_authorized_calls(self):
        tb = vent_demo_common.GuardedTB()
        for method, path, body in [("POST", "/api/widgetType", self.widget), ("POST", "/api/dashboard", self.dashboard),
                                   ("POST", "/api/widgetsBundle", {}), ("DELETE", "/api/dashboard/x", None),
                                   ("POST", "/api/plugins/telemetry/DEVICE/x/SERVER_SCOPE", {}),
                                   ("POST", "/api/rpc/oneway/x", {}), ("PUT", "/api/x", {})]:
            with self.assertRaises(vent_demo_common.Blocked):
                tb._check(method, path, body)
        creator = vent_demo_common.GuardedTB(allow_create=True)
        creator._check("POST", "/api/widgetType", self.widget)
        creator._check("POST", "/api/dashboard", self.dashboard)
        with self.assertRaises(vent_demo_common.Blocked):
            creator._check("POST", "/api/dashboard", dict(self.dashboard, id={"id": "x"}))
        with self.assertRaises(vent_demo_common.Blocked):
            creator._check("POST", "/api/widgetType", dict(self.widget, fqn="siba_custom_ui.header_bar"))
        with self.assertRaises(vent_demo_common.Blocked):
            creator._check("POST", "/api/widgetType?updateExistingByFqn=true", self.widget)
        updater = vent_demo_common.GuardedTB(allow_update_ids={"wid-1"})
        updater._check("POST", "/api/widgetType", dict(self.widget, id={"id": "wid-1"}))
        for body in (dict(self.widget, id={"id": "other"}), dict(self.widget, fqn="siba_custom_ui.header_bar", id={"id": "wid-1"}),
                     self.widget):
            with self.assertRaises(vent_demo_common.Blocked):
                updater._check("POST", "/api/widgetType", body)
        with self.assertRaises(vent_demo_common.Blocked):
            updater._check("POST", "/api/dashboard", dict(self.dashboard, id={"id": "bb585f20-a835-11f1-9683-f9c2621c1a59"}))
        deleter = vent_demo_common.GuardedTB(allow_delete_ids={"abc"})
        deleter._check("DELETE", "/api/dashboard/abc", None)
        with self.assertRaises(vent_demo_common.Blocked):
            deleter._check("DELETE", "/api/dashboard/bb585f20-a835-11f1-9683-f9c2621c1a59", None)


HARNESS = """
var payload = arguments[0], css = arguments[1], state = arguments[2];
var style = document.getElementById('ns-style') || document.head.appendChild(Object.assign(document.createElement('style'), {id: 'ns-style'}));
style.textContent = css;
var host = document.getElementById('tb-widget');
host.className = '%s';
host.innerHTML = payload.descriptor.templateHtml;
window.__opened = [];
window.__hashBefore = location.hash;
var self = {ctx: {$container: [host], settings: {viewState: state},
  stateController: {openState: function (id, params, right) { window.__opened.push([id, params, right]); },
                    getStateId: function () { return state; }}}};
new Function('self', payload.descriptor.controllerScript)(self);
self.onInit();
return true;
""" % NAMESPACE


@unittest.skipUnless(geckodriver_path(), "geckodriver không có; bỏ qua test trình duyệt")
class WidgetRuntimeHarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = StaticServer().__enter__()
        cls.browser = Browser()
        cls.payload = json.loads((BUILD / "widget_type.json").read_text())
        cls.css = namespace_css(cls.payload["descriptor"]["templateCss"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.__exit__(None, None, None)

    def mount(self, state, width=1650, height=950):
        self.browser.resize(width, height)
        self.browser._session("POST", "/url", {"url": self.server.base_url + "/tests/tb_widget_harness.html"})
        self.browser.run(HARNESS, self.payload, self.css, state)

    def test_all_states_render_with_demo_badge_and_no_shell(self):
        for state in vent_demo_common.STATES:
            self.mount(state)
            info = self.browser.run("""
              var root = document.querySelector('.vent-demo-root');
              return {badge: root.querySelector('.demo-badge').innerText,
                      active: root.querySelector('.state-tabs a.active').getAttribute('data-nav'),
                      shell: document.querySelectorAll('.tb-preview-sidebar,.tb-topbar,.tb-preview-shell').length,
                      globals: typeof window.VentilationAdapter + typeof window.VentilationDashboard,
                      bg: getComputedStyle(root.querySelector('.vent-header')).backgroundColor,
                      font: getComputedStyle(root).fontFamily};""")
            self.assertEqual(info["badge"], "DEMO DATA", state)
            self.assertEqual(info["active"], state)
            self.assertEqual(info["shell"], 0)
            self.assertEqual(info["globals"], "undefinedundefined")
            self.assertEqual(info["bg"], "rgb(21, 39, 55)")
            self.assertIn("Arial", info["font"])

    def test_navigation_uses_state_controller_not_hash(self):
        self.mount("default")
        self.browser.run("document.querySelector('.state-tabs a[data-nav=\"vent_history\"]').click();"
                         "document.querySelector('.barn-card').click();"
                         "document.querySelector('.state-tabs a[data-nav=\"default\"]').click();")
        opened = self.browser.run("return window.__opened")
        self.assertEqual(opened, [["vent_history", {}, False], ["vent_detail", {}, False]])
        self.assertEqual(self.browser.run("return location.hash"), "")

    def test_detail_values_and_global_css_isolation(self):
        self.mount("vent_detail", 1650, 600)   # thấp hơn nội dung: widget phải tự cuộn
        info = self.browser.run("""
          var root = document.querySelector('.vent-demo-root');
          return {fans: [...root.querySelectorAll('.fan')].map(g => g.getAttribute('class')),
                  secondary: [...root.querySelectorAll('.secondary-row b')].map(b => b.innerText),
                  stage: [...root.querySelectorAll('.summary-row')].filter(r => r.innerText.indexOf('Cấp hiện tại') === 0).map(r => r.querySelector('b').innerText),
                  noRatio: !/\d+ \/ \d+/.test(root.innerText),
                  tabBorder: getComputedStyle(root.querySelector('.state-tabs a:not(.active)')).borderBottomColor,
                  activeBorder: getComputedStyle(root.querySelector('.state-tabs a.active')).borderBottomColor,
                  linkBorder: getComputedStyle(root.querySelector('.text-link')).borderBottomWidth,
                  h2Spacing: getComputedStyle(root.querySelector('h2')).letterSpacing,
                  scrolls: root.scrollHeight > root.clientHeight && getComputedStyle(root).overflowY};""")
        self.assertEqual(info["fans"], ["fan RUNNING", "fan RUNNING", "fan RUNNING", "fan STOPPED", "fan UNKNOWN", "fan STOPPED"])
        self.assertEqual(info["secondary"], ["--", "--", "--", "NOT CONFIGURED"])
        self.assertEqual(info["stage"], ["4"])
        self.assertTrue(info["noRatio"])
        self.assertEqual(info["tabBorder"], "rgba(0, 0, 0, 0)")
        self.assertEqual(info["activeBorder"], "rgb(0, 212, 224)")
        self.assertEqual(info["linkBorder"], "0px")
        self.assertEqual(info["h2Spacing"], "normal")
        self.assertEqual(info["scrolls"], "auto")

    def computed_typography(self):
        return self.browser.run("""
          var root = document.querySelector('.vent-demo-root');
          function cs(sel) { var e = root.querySelector(sel); if (!e) return null; var s = getComputedStyle(e);
            return [s.fontWeight, s.lineHeight, s.fontFamily.split(',')[0].replace(/"/g, ''), s.fontSize]; }
          return {h2: cs('.panel__head h2'), h3: cs('.subsection-title'), p: cs('.panel__head p'),
                  strong: cs('.vent-header__title'), kpi: cs('.kpi__value'), th: cs('.data-table th'), td: cs('.data-table td'),
                  alarmB: cs('.data-table td b')};""")

    def test_tb_global_typography_is_neutralised(self):
        expected = {}
        for state in ("vent_detail", "vent_history", "vent_alarms"):
            self.mount(state)
            self.browser.run("document.body.classList.remove('mat-typography')")
            clean = self.computed_typography()
            self.browser.run("document.body.classList.add('mat-typography')")
            hostile = self.computed_typography()
            self.assertEqual(hostile, clean, state)
            expected.update({k: v for k, v in clean.items() if v})
        self.assertEqual(expected["h2"][:2], ["700", "normal"])
        self.assertEqual(expected["h3"][0], "700")
        self.assertEqual(expected["strong"][0], "700")
        self.assertEqual(expected["kpi"][0], "600")          # class của bản đã duyệt vẫn thắng reset
        self.assertEqual(expected["td"][2:], ["Arial", "14px"])
        self.assertEqual(expected["th"][3], "12px")

    def test_header_reserves_space_for_dashboard_toolbar_fab(self):
        self.mount("default", 1650, 950)
        gap = self.browser.run("""
          var root = document.querySelector('.vent-demo-root');
          var header = root.querySelector('.vent-header').getBoundingClientRect();
          return header.right - root.querySelector('.demo-badge').getBoundingClientRect().right;""")
        self.assertGreaterEqual(gap, 60)

    def test_build_preserves_identity_and_adds_read_only_settings_state(self):
        deployed = json.loads(subprocess.run(["git", "show", "7cb9621:deploy/thingsboard/build/dashboard.json"], cwd=ROOT,
                                             check=True, capture_output=True, text=True).stdout)
        dashboard = json.loads((BUILD / "dashboard.json").read_text())
        widget = json.loads((BUILD / "widget_type.json").read_text())
        self.assertEqual(dashboard["title"], deployed["title"])
        self.assertEqual(widget["fqn"], "siba_vent_demo.vent_demo_view")
        self.assertEqual(list(dashboard["configuration"]["states"]), vent_demo_common.STATES)
        self.assertEqual(vent_demo_common.STATES[-1], "vent_settings")
        # ID widget của 4 state cũ giữ nguyên (uuid5 xác định); chỉ thêm một widget cho vent_settings.
        old_ids, new_ids = set(deployed["configuration"]["widgets"]), set(dashboard["configuration"]["widgets"])
        self.assertTrue(old_ids < new_ids)
        self.assertEqual(len(new_ids - old_ids), 1)
        self.assertIn("VentilationContract", widget["descriptor"]["controllerScript"])

    def test_settings_state_is_read_only_in_widget_runtime(self):
        self.mount("vent_settings")
        info = self.browser.run("""
          var root = document.querySelector('.vent-demo-root');
          root.querySelector('.settings-index a[data-scroll]').click();
          return {cells: root.querySelectorAll('[data-setting-key]').length,
                  controls: root.querySelectorAll('input,select,textarea,form,button').length,
                  values: [...new Set([...root.querySelectorAll('[data-setting-key]')].map(e => e.innerText))],
                  opened: window.__opened.length, hash: location.hash};""")
        self.assertEqual(info["cells"], 224)
        self.assertEqual(info["controls"], 0)
        self.assertEqual(info["values"], ["--"])
        self.assertEqual(info["opened"], 0)
        self.assertEqual(info["hash"], "")

    def test_history_gap_and_alarms_read_only(self):
        self.mount("vent_history")
        path = self.browser.run("return document.querySelector('.chart .inside').getAttribute('d')")
        self.assertEqual(path.count("M"), 2)
        self.mount("vent_alarms")
        self.assertEqual(self.browser.run("return document.querySelectorAll('.vent-demo-root button,.vent-demo-root input').length"), 0)

    def test_mobile_width_has_no_horizontal_overflow(self):
        for state in vent_demo_common.STATES:
            self.mount(state, 390, 844)
            overflow = self.browser.run("var r=document.querySelector('.vent-demo-root');"
                                        "return [document.documentElement.scrollWidth - document.documentElement.clientWidth, r.scrollWidth - r.clientWidth]")
            self.assertEqual(overflow, [0, 0], state)


if __name__ == "__main__":
    unittest.main()
