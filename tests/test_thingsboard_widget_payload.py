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
    animation_pattern = r'@keyframes[^{}]+\{(?:[^{}]*\{[^{}]*\})+\s*\}'
    keyframes = re.findall(animation_pattern, css)
    css = re.sub(animation_pattern, '', css)
    def scope(block):
        out = []
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", block):
            parts = ",".join(".%s %s" % (NAMESPACE, s.strip()) for s in selector.split(","))
            out.append("%s{%s}" % (parts, body))
        return "".join(out)
    result = []
    for media, inner, plain in re.findall(r"(@media[^{]+)\{((?:[^{}]*\{[^{}]*\})*)\s*\}|([^@{}]+\{[^{}]*\})", css):
        result.append("%s{%s}" % (media, scope(inner)) if media else scope(plain))
    return "\n".join(result + keyframes)


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
var payload = arguments[0], css = arguments[1], state = arguments[2], stateParams = arguments[3] || {};
var style = document.getElementById('ns-style') || document.head.appendChild(Object.assign(document.createElement('style'), {id: 'ns-style'}));
style.textContent = css;
var host = document.getElementById('tb-widget');
host.className = '%s';
host.innerHTML = payload.descriptor.templateHtml;
window.__opened = [];
window.__hashBefore = location.hash;
var self = {ctx: {$container: [host], settings: {viewState: state},
  stateController: {openState: function (id, params, right) { window.__opened.push([id, params, right]); },
                    getStateId: function () { return state; },
                    getStateParams: function () { return stateParams; }}}};
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

    def mount(self, state, width=1650, height=950, state_params=None):
        self.browser.resize(width, height)
        self.browser._session("POST", "/url", {"url": self.server.base_url + "/tests/tb_widget_harness.html"})
        self.browser.run(HARNESS, self.payload, self.css, state, state_params or {})

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

    def test_navigation_preserves_selected_barn_in_state_controller_params(self):
        self.mount("default")
        ids = self.browser.run("return [...document.querySelectorAll('.barn-card')].map(function (card) { return card.getAttribute('data-barn-id'); })")
        self.assertGreaterEqual(len(ids), 2)
        self.browser.run("document.querySelector('.state-tabs a[data-nav=\"vent_history\"]').click();"
                         "document.querySelectorAll('.barn-card')[1].click();"
                         "document.querySelector('.state-tabs a[data-nav=\"default\"]').click();")
        opened = self.browser.run("return window.__opened")
        # Same-state selection changes preserve context; only an unchanged tab is a no-op.
        self.assertEqual(opened, [["vent_history", {"barnId": ids[0]}, False],
                                  ["vent_detail", {"barnId": ids[1]}, False],
                                  ["default", {"barnId": ids[1]}, False]])
        self.assertEqual(self.browser.run("return location.hash"), "")

    def test_non_pilot_barn_shows_context_not_pilot_detail(self):
        self.mount("default")
        non_pilot = self.browser.run("return document.querySelectorAll('.barn-card')[1].getAttribute('data-barn-id')")
        self.mount("vent_detail", state_params={"barnId": non_pilot})
        info = self.browser.run("""
          var root = document.querySelector('.vent-demo-root');
          return {context: root.querySelector('.selected-barn-context').innerText,
                  detail: root.querySelectorAll('.detail-layout').length,
                  pilotMetrics: root.innerText.indexOf('Nhiệt độ trung bình') >= 0};""")
        self.assertIn("Chưa có dữ liệu chi tiết", info["context"])
        self.assertEqual(info["detail"], 0)
        self.assertFalse(info["pilotMetrics"])

    def test_unknown_barn_parameter_does_not_silently_show_pilot_data(self):
        self.mount("vent_detail", state_params={"barnId": "not-a-barn"})
        info = self.browser.run("""
          var root = document.querySelector('.vent-demo-root');
          var link = root.querySelector('[data-nav=vent_detail][data-barn-id=barn-nd2-1]');
          return {context: root.querySelector('.selected-barn-context').innerText,
                  detail: root.querySelectorAll('.detail-layout').length,
                  pilotLink: link && link.innerText};""")
        self.assertIn("Không tìm thấy nhà", info["context"])
        self.assertEqual(info["detail"], 0)
        self.assertIn("Xem nhà mẫu ND2-1", info["pilotLink"])
        self.browser.run("document.querySelector('[data-nav=vent_detail][data-barn-id=barn-nd2-1]').click()")
        self.assertEqual(self.browser.run("return document.querySelectorAll('.detail-layout').length"), 1)
        self.assertEqual(self.browser.run("return window.__opened"), [["vent_detail", {"barnId": "barn-nd2-1"}, False]])

    def test_generated_illustration_is_embedded_and_loads_without_external_host(self):
        self.mount("default")
        self.browser.wait_for("var image=document.querySelector('.barn-illustration img'); return image && image.complete && image.naturalWidth > 0")
        self.assertTrue(self.browser.run("return document.querySelector('.barn-illustration img').src.startsWith('data:image/png;base64,')"))
        self.assertIn("MINH HỌA", self.browser.run("return document.querySelector('.barn-illustration figcaption').textContent"))

    def test_detail_values_and_global_css_isolation(self):
        self.mount("vent_detail", 1650, 600)   # thấp hơn nội dung: widget phải tự cuộn
        info = self.browser.run(r"""
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
        self.assertEqual([classes.split()[1] for classes in info["fans"]], ["RUNNING", "RUNNING", "RUNNING", "STOPPED", "UNKNOWN", "STOPPED"])
        self.assertTrue(all("quality-" in classes and "connectivity-ONLINE" in classes for classes in info["fans"]))
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
                  controls: root.querySelectorAll('input:not([data-filter-input=settings]),select,textarea,form,button').length,
                  values: [...new Set([...root.querySelectorAll('[data-setting-key]')].map(e => e.innerText))],
                  opened: window.__opened.length, hash: location.hash};""")
        self.assertEqual(info["cells"], 224)
        self.assertEqual(info["controls"], 0)
        self.assertEqual(info["values"], ["--"])
        self.assertEqual(info["opened"], 0)
        self.assertEqual(info["hash"], "")

    def test_history_gap_and_alarms_read_only(self):
        self.mount("vent_history")
        chart = self.browser.run("""
          var root = document.querySelector('.vent-demo-root');
          function path(cls) { return root.querySelector('.chart .' + cls).getAttribute('d'); }
          return {inside: path('inside'), outside: path('outside'), perceived: path('perceived'), humidity: path('humidity'),
                  left: root.querySelectorAll('.chart .axis-left').length,
                  right: root.querySelectorAll('.chart .axis-right').length,
                  samples: [...root.querySelectorAll('.chart-sample')].map(function (sample) { return {
                    tabindex: sample.getAttribute('tabindex'), role: sample.getAttribute('role'), label: sample.getAttribute('aria-label'),
                    title: (sample.querySelector('title') || {}).textContent, points: sample.querySelectorAll('.chart-point').length}; })};""")
        self.assertEqual(chart["inside"].count("M"), 2)
        self.assertEqual(chart["outside"].count("M"), 1)
        self.assertEqual(chart["perceived"].count("M"), 1)
        self.assertEqual(chart["humidity"].count("M"), 1)
        self.assertEqual((chart["left"], chart["right"]), (4, 4))
        self.assertTrue(chart["samples"])
        self.assertTrue(all(s["tabindex"] == "0" and s["role"] == "img" and s["label"] and s["title"] and s["points"] for s in chart["samples"]))
        self.mount("vent_alarms")
        self.assertEqual(self.browser.run("return document.querySelectorAll('.vent-demo-root button,.vent-demo-root input:not([data-filter-input=alarm])').length"), 0)

    def test_filters_are_local_and_settings_remain_read_only(self):
        self.mount("default")
        info = self.browser.run("""
          var root = document.querySelector('.vent-demo-root'), input = root.querySelector('[data-filter-input=barn]');
          input.value = 'no-match'; input.dispatchEvent(new Event('input', {bubbles:true}));
          return {hidden: [...root.querySelectorAll('.barn-card')].every(function (card) { return card.hidden; }),
                  empty: !root.querySelector('[data-filter-empty=barn]').hidden};""")
        self.assertEqual(info, {"hidden": True, "empty": True})
        self.mount("vent_settings")
        self.assertEqual(self.browser.run("""
          var root = document.querySelector('.vent-demo-root');
          return [root.querySelectorAll('[data-filter-input=settings]').length,
                  root.querySelectorAll('button,select,textarea,form').length,
                  root.querySelectorAll('input:not([data-filter-input=settings])').length];"""), [1, 0, 0])

    def test_raw_states_are_machine_readable_but_labels_are_vietnamese(self):
        self.mount("vent_detail")
        states = self.browser.run("""
          return [...document.querySelectorAll('[data-raw-state]')].map(function (el) {
            return [el.getAttribute('data-raw-state'), el.textContent.trim(), el.className.baseVal || el.className];
          });""")
        running = [item for item in states if item[0] == "RUNNING"]
        self.assertTrue(running)
        self.assertTrue(any(item[1] == "Đang chạy" and "status-RUNNING" in item[2] for item in running))

    def test_motion_rule_only_animates_current_online_running_fan(self):
        self.assertIn(".fan.RUNNING.quality-CURRENT.connectivity-ONLINE .fan-blades{animation:vent-fan-spin", self.css)
        self.assertIn("@media(prefers-reduced-motion:reduce)", self.css)
        self.mount("vent_detail")
        self.assertEqual(self.browser.run("return getComputedStyle(document.querySelector('.fan.RUNNING.quality-CURRENT.connectivity-ONLINE .fan-blades')).animationName"), "vent-fan-spin")

    def test_mobile_iframe_has_real_390px_width_and_no_horizontal_overflow(self):
        element_key = "element-6066-11e4-a52e-4f735466cecf"
        self.browser.resize(1280, 1000)
        try:
            self.browser._session("POST", "/url", {"url": self.server.base_url + "/deploy/thingsboard/mobile_frame.html"})
            frame = self.browser._session("POST", "/element", {"using": "css selector", "value": "#device"})[element_key]
            self.browser._session("POST", "/frame", {"id": {element_key: frame}})
            self.browser.run("location.href = arguments[0]", self.server.base_url + "/tests/tb_widget_harness.html")
            self.browser.wait_for("return window.innerWidth === 390")
            for state in vent_demo_common.STATES:
                self.browser.run(HARNESS, self.payload, self.css, state, {})
                overflow = self.browser.run("var r=document.querySelector('.vent-demo-root');"
                                            "return [document.documentElement.scrollWidth - document.documentElement.clientWidth, r.scrollWidth - r.clientWidth]")
                self.assertEqual(overflow, [0, 0], state)
        finally:
            self.browser._session("POST", "/frame/parent", {})
            self.browser.resize(1920, 1080)


if __name__ == "__main__":
    unittest.main()
