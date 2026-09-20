"""Chạy adapter contract v0.3 và năm state thật trong Firefox headless (bỏ qua nếu thiếu geckodriver)."""
import json
import unittest

from webdriver_support import ROOT, Browser, StaticServer, geckodriver_path

FIXTURE = json.loads((ROOT / "fixtures/ventilation/demo.json").read_text())
CONTRACT = json.loads((ROOT / "docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.3.json").read_text())

# Áp một biến thể: latest/platform/settings là bản vá; drop xóa khỏi latest; notConfigured thêm vào mapping.
BUILD_VM = """
var raw = JSON.parse(arguments[0]), v = arguments[1] || {};
Object.keys(v.latest || {}).forEach(function (key) { raw.latest[key] = v.latest[key]; });
Object.keys(v.platform || {}).forEach(function (key) { raw.platform[key] = v.platform[key]; });
Object.keys(v.settings || {}).forEach(function (key) { raw.settings[key] = v.settings[key]; });
(v.drop || []).forEach(function (key) { delete raw.latest[key]; });
raw.mapping.notConfigured = raw.mapping.notConfigured.concat(v.notConfigured || []);
return VentilationAdapter.createViewModel(raw);
"""


@unittest.skipUnless(geckodriver_path(), "geckodriver không có; bỏ qua test trình duyệt")
class DashboardBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = StaticServer().__enter__()
        cls.browser = Browser()
        cls.url = cls.server.base_url + "/dashboard/index.html"
        cls.raw = json.dumps(FIXTURE)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.__exit__(None, None, None)

    def open_state(self, state):
        self.browser.open(self.url + "#" + state)
        # Same-URL navigation does not reset a model intentionally modified by a test.
        self.browser._session("POST", "/refresh", {})
        self.browser.wait_for("return !!document.querySelector('.state-tabs a.active[href=\"#%s\"]')" % state)

    def vm(self, variant=None):
        if isinstance(variant, str):
            variant = FIXTURE["adapterTestVariants"][variant]
        return self.browser.run(BUILD_VM, self.raw, variant or {})

    # --- View model chuẩn ---
    def test_canonical_metrics_follow_contract_classification(self):
        self.open_state("default")
        vm = self.vm()
        self.assertEqual(vm["unknownKeys"], [])
        monitoring = {v["key"] for v in CONTRACT["variables"] if v["role"] != "setting"}
        self.assertEqual(set(vm["metrics"]), monitoring | {"controllerOnline", "dataQuality"})
        for key in ("stageCount", "fan06Fault", "coolingPump01Fault"):
            self.assertNotIn(key, vm["metrics"])
        cls = {k: m["classification"] for k, m in vm["metrics"].items()}
        self.assertEqual(cls["indoorTemperatureAvg"], "PRIMARY_MONITORING")
        self.assertEqual(cls["equipmentFaultActive"], "PRIMARY_MONITORING")
        self.assertEqual(cls["pigCount"], "SECONDARY_MONITORING")
        self.assertEqual(cls["waterFlow"], "OPTIONAL")
        self.assertEqual(cls["temperatureHighAlarmActive"], "OPTIONAL")
        self.assertEqual(cls["controllerOnline"], "PLATFORM_DERIVED")
        self.assertEqual(cls["dataQuality"], "PLATFORM_DERIVED")
        self.assertEqual(sum(g["count"] for g in vm["settings"]), 224)

    def test_enums_decode_and_unknown_values(self):
        self.open_state("default")
        m = self.vm()["metrics"]
        self.assertEqual([m[k]["value"] for k in ("operatingMode", "controlBasis", "fanControlMode", "dehumidificationEnabled")],
                         ["AUTO", "ACTUAL_TEMPERATURE", "STEP", "DISABLED"])
        m = self.vm("enumsVfdPerceived")["metrics"]
        self.assertEqual([m[k]["value"] for k in ("operatingMode", "controlBasis", "fanControlMode", "dehumidificationEnabled")],
                         ["MANUAL", "PERCEIVED_TEMPERATURE", "VFD", "ENABLED"])
        m = self.vm("enumsInvalid")["metrics"]
        self.assertEqual([m[k]["value"] for k in ("operatingMode", "controlBasis", "fanControlMode", "dehumidificationEnabled")],
                         ["UNKNOWN"] * 4)

    def test_equipment_states(self):
        self.open_state("default")
        base = {e["key"]: e["state"] for e in self.vm()["equipment"]}
        self.assertEqual(base, {"fan01Run": "RUNNING", "fan02Run": "RUNNING", "fan03Run": "RUNNING", "fan04Run": "STOPPED",
                                "fan05Run": "UNKNOWN", "fan06Run": "STOPPED", "coolingPump01Run": "RUNNING",
                                "coolingPump02Run": "NOT_CONFIGURED"})
        edges = {e["key"]: e for e in self.vm("equipmentEdges")["equipment"]}
        self.assertEqual(edges["fan01Run"]["state"], "STOPPED")          # 0
        self.assertEqual(edges["fan02Run"]["state"], "RUNNING")          # 1, dữ liệu STALE
        self.assertEqual(edges["fan02Run"]["quality"], "STALE")
        self.assertEqual(edges["fan03Run"]["state"], "UNKNOWN")          # mã không hợp lệ
        self.assertEqual(edges["fan04Run"]["state"], "UNKNOWN")          # boolean không phải uint16
        self.assertEqual(edges["fan05Run"]["state"], "UNKNOWN")          # thiếu telemetry ≠ NOT_CONFIGURED
        self.assertEqual(edges["fan06Run"]["state"], "NOT_CONFIGURED")   # mapping N/A thắng giá trị null
        self.assertFalse(edges["fan06Run"]["configured"])

    def test_system_flags_do_not_name_devices(self):
        self.open_state("default")
        flags = {f["key"]: f["value"] for f in self.vm()["systemFlags"]}
        self.assertEqual(flags, {"equipmentFaultActive": "ACTIVE", "externalHighTemperatureAlarm": "NORMAL"})
        flags = {f["key"]: f["value"] for f in self.vm("flagsCleared")["systemFlags"]}
        self.assertEqual(flags, {"equipmentFaultActive": "NORMAL", "externalHighTemperatureAlarm": "ACTIVE"})
        states = {e["state"] for e in self.vm()["equipment"]}
        self.assertNotIn("FAULT", states)

    def test_stage_is_current_value_only(self):
        self.open_state("default")
        self.assertEqual(self.vm()["controller"]["stageDisplay"], "4")
        self.assertEqual(self.vm("stageZero")["controller"]["stageDisplay"], "0")
        self.assertEqual(self.vm("stageMissing")["controller"]["stageDisplay"], "--")

    def test_zero_null_and_platform(self):
        self.open_state("default")
        vm = self.vm("zeroMeasurements")
        self.assertEqual([vm["metrics"][k]["value"] for k in ("sideInletPosition", "airFlow", "waterConsumptionTotal")], [0, 0, 0])
        self.assertIsNone(self.vm()["metrics"]["airFlow"]["value"])
        self.assertIsNone(self.vm()["metrics"]["waterFlow"]["value"])
        self.assertFalse(self.vm()["metrics"]["waterFlow"]["configured"])
        self.assertEqual(self.vm()["controller"]["online"], "ONLINE")
        offline = self.vm("platformOffline")
        self.assertEqual(offline["controller"]["online"], "OFFLINE")
        self.assertEqual(offline["metrics"]["dataQuality"]["value"], "OFFLINE")

    def test_settings_model(self):
        self.open_state("default")
        groups = {g["name"]: g for g in self.vm("settingsSample")["settings"]}
        self.assertEqual([g["count"] for g in groups.values()], [14, 40, 40, 108, 18, 4])
        system = {i["key"]: i["value"] for i in groups["CÀI ĐẶT - HỆ THỐNG"]["items"]}
        self.assertEqual(system["settingControlBasis"], "PERCEIVED_TEMPERATURE")
        stage = groups["CÀI ĐẶT - CẤP THÔNG GIÓ"]["matrices"][0]
        self.assertEqual(len(stage["slots"]), 9)
        self.assertEqual(len(stage["fields"]), 12)
        self.assertEqual(stage["cells"]["03:Fan02Enabled"]["value"], 0)
        self.assertFalse(stage["cells"]["01:Fan01Frequency"]["configured"])
        profile = groups["CÀI ĐẶT - NHIỆT ĐỘ"]["matrices"][0]
        self.assertEqual((len(profile["slots"]), len(profile["fields"])), (10, 4))
        self.assertEqual(profile["cells"]["02:Setpoint"]["value"], 0)
        time = groups["CÀI ĐẶT - THỜI GIAN"]
        self.assertEqual(len(time["scalars"]), 2)
        self.assertEqual([m["prefix"] for m in time["matrices"]], ["fan", "coolingPump"])

    def test_history_mapping(self):
        self.open_state("default")
        history = self.vm()["history"]
        self.assertTrue(all(isinstance(row["perceivedTemperature"], (int, float)) for row in history))
        self.assertIn(None, [row["indoorTemperatureAvg"] for row in history])
        self.assertTrue(all(row[k] is None for row in history for k in ("airSpeed", "airFlow", "waterConsumptionTotal")))
        mapped = self.browser.run("return VentilationAdapter.mapHistory({ts: 1, relativeHumidity: 0, airFlow: 'x'})")
        self.assertEqual(mapped["relativeHumidity"], 0)
        self.assertIsNone(mapped["airFlow"])
        self.assertEqual(mapped["quality"], "UNKNOWN")

    def test_empty_history_renders_notice_without_invented_points(self):
        self.open_state("default")
        info = self.browser.run("""
          var raw=JSON.parse(arguments[0]); raw.history=[];
          var vm=VentilationAdapter.createViewModel(raw), app=document.getElementById('app');
          VentilationDashboard.render(app,vm,'vent_history',function(){});
          return {text:app.innerText, points:app.querySelectorAll('.chart-point').length};
        """, self.raw)
        self.assertIn("Chưa có mẫu lịch sử", info["text"])
        self.assertEqual(info["points"], 0)

    def test_fan_motion_actually_runs_and_respects_reduced_motion(self):
        self.open_state("vent_detail")
        moved = self.browser._session("POST", "/execute/async", {"script": """
          var done=arguments[arguments.length-1], el=document.querySelector('.fan.RUNNING .fan-blades');
          var initial=getComputedStyle(el).transform;
          setTimeout(function(){done(initial!==getComputedStyle(el).transform);},180);
        """, "args": []})
        self.assertTrue(moved)
        reduced = Browser(prefs={"ui.prefersReducedMotion": 1})
        try:
            reduced.open(self.url + "#vent_detail")
            self.assertTrue(reduced.run("return matchMedia('(prefers-reduced-motion: reduce)').matches"))
            names = reduced.run("return [...document.querySelectorAll('.fan-blades')].map(function(el){return getComputedStyle(el).animationName;})")
            self.assertTrue(all(name == "none" for name in names))
        finally:
            reduced.close()

    def test_non_demo_or_wrong_contract_fixture_rejected(self):
        self.open_state("default")
        errors = self.browser.run("""
          function attempt(raw) { try { VentilationAdapter.createViewModel(raw); return null; } catch (e) { return e.message; } }
          var good = JSON.parse(arguments[0]); var wrong = JSON.parse(arguments[0]); wrong.contract.version = '0.1';
          return [attempt({demo: false}), attempt(wrong)];""", self.raw)
        self.assertIn("demo", errors[0])
        self.assertIn("0.3", errors[1])

    # --- DOM từng state ---
    def test_default_state(self):
        self.open_state("default")
        text = self.browser.run("return document.getElementById('app').innerText")
        self.assertIn("DEMO DATA", text)
        self.assertIn("Cấp: 4", text)
        sources = self.browser.run("return [...document.querySelectorAll('.alarm-mini .source-tag')].map(e => e.innerText)")
        self.assertEqual(sources, ["PLC", "PLATFORM", "PLATFORM"])

    def test_detail_state(self):
        self.open_state("vent_detail")
        info = self.browser.run("""
          var app = document.getElementById('app');
          function row(label) { var r = [...app.querySelectorAll('.summary-row')].filter(x => x.querySelector('span').innerText.indexOf(label) === 0)[0]; return r && r.querySelector('b').innerText; }
          return {text: app.innerText,
            fans: [...app.querySelectorAll('.fan')].map(g => g.getAttribute('class')),
            fanLabels: [...app.querySelectorAll('.fan .svg-sub')].map(t => t.textContent),
            cards: [...app.querySelectorAll('.equipment-card b')].map(b => b.innerText),
            flags: [...app.querySelectorAll('.system-flag b')].map(b => b.innerText),
            stage: row('Cấp hiện tại'), mode: row('Chế độ'), basis: row('Cơ sở điều khiển'), online: row('Kết nối'),
            secondary: [...app.querySelectorAll('.secondary-row b')].map(b => b.innerText),
            platformTags: app.querySelectorAll('.controller-summary .derived-tag').length,
            louvers: [...app.querySelectorAll('.louver text')].map(t => t.textContent)};""")
        self.assertEqual([classes.split()[1] for classes in info["fans"]], ["RUNNING", "RUNNING", "RUNNING", "STOPPED", "UNKNOWN", "STOPPED"])
        self.assertTrue(all("quality-" in classes and "connectivity-ONLINE" in classes for classes in info["fans"]))
        self.assertEqual(info["cards"][-1], "Chưa cấu hình")
        self.assertNotIn("FAULT", " ".join(info["cards"] + info["fanLabels"]))
        self.assertEqual(info["flags"], ["Đang bật", "Bình thường"])
        self.assertEqual((info["stage"], info["mode"], info["basis"], info["online"]), ("4", "AUTO", "Nhiệt độ thực", "ONLINE"))
        self.assertEqual(info["secondary"], ["--", "--", "--", "NOT CONFIGURED"])
        self.assertEqual(info["platformTags"], 2)
        self.assertEqual(info["louvers"], ["Cửa chớp trần · 65 % · STALE", "Cửa chớp hông · 40 % · CURRENT"])
        for value in ("27.8", "31.2", "29.1", "74", "27.6", "DEMO DATA"):
            self.assertIn(value, info["text"])
        self.assertNotRegex(info["text"], r"\d+ / \d+")
        self.assertNotIn("VFD (OPTIONAL)", info["text"])

    def test_not_configured_fan_is_visible_and_muted(self):
        self.open_state("vent_detail")
        info = self.browser.run("""
          var raw = JSON.parse(arguments[0]); raw.mapping.notConfigured.push('fan06Run');
          VentilationDashboard.render(document.getElementById('app'), VentilationAdapter.createViewModel(raw), 'vent_detail', function () {});
          var g = document.querySelectorAll('.fan')[5];
          return {cls: g.getAttribute('class'), label: g.querySelector('.svg-sub').textContent, opacity: getComputedStyle(g).opacity,
                  visible: g.getBoundingClientRect().width > 0};""", self.raw)
        self.assertEqual(info["cls"].split()[:2], ["fan", "NOT_CONFIGURED"])
        self.assertEqual(info["label"], "Chưa cấu hình")
        self.assertTrue(info["visible"])
        self.assertLess(float(info["opacity"]), 1)

    def test_history_state(self):
        self.open_state("vent_history")
        info = self.browser.run("""
          var app = document.getElementById('app');
          return {envHeaders: [...app.querySelectorAll('.env-table th')].map(th => th.innerText),
            airHeaders: [...app.querySelectorAll('.air-water th')].map(th => th.innerText),
            airCells: [...app.querySelectorAll('.air-water td')].map(td => td.innerText),
            indoor: app.querySelector('.chart .inside').getAttribute('d'), perceived: app.querySelector('.chart .perceived').getAttribute('d'),
            axes: [app.querySelectorAll('.chart .axis-left').length, app.querySelectorAll('.chart .axis-right').length],
            samples: [...app.querySelectorAll('.chart-sample')].map(sample => [sample.tabIndex, sample.getAttribute('role'), sample.getAttribute('aria-label'), sample.querySelectorAll('.chart-point').length]),
            notice: app.querySelector('.air-water .notice') && app.querySelector('.air-water .notice').innerText};""")
        self.assertEqual(info["envHeaders"], ["Thời gian", "Nhiệt độ trong", "Nhiệt độ ngoài", "Nhiệt độ cảm nhận", "Độ ẩm", "Chất lượng"])
        self.assertEqual(info["airHeaders"], ["Thời gian", "Tốc độ gió", "Lưu lượng gió", "Nước tiêu thụ (tổng)", "Chất lượng"])
        self.assertEqual(info["indoor"].count("M"), 2)
        self.assertEqual(info["perceived"].count("M"), 1)
        self.assertEqual(info["axes"], [4, 4])
        self.assertTrue(info["samples"])
        self.assertTrue(all(sample[0] == 0 and sample[1] == "img" and sample[2] and sample[3] for sample in info["samples"]))
        values = [c for i, c in enumerate(info["airCells"]) if i % 5 in (1, 2, 3)]
        self.assertEqual(set(values), {"--"})
        self.assertIn("không hiển thị giá trị giả", info["notice"])

    def test_alarms_state_read_only(self):
        self.open_state("vent_alarms")
        info = self.browser.run("""
          var app = document.getElementById('app');
          return {controls: app.querySelectorAll('button, input:not([data-filter-input=alarm]), select, textarea, form').length,
            filter: app.querySelectorAll('[data-filter-input=alarm]').length,
            types: [...app.querySelectorAll('.data-table tbody b')].map(b => b.innerText),
            sources: [...app.querySelectorAll('.data-table tbody .source-tag')].map(e => e.innerText)};""")
        self.assertEqual(info["controls"], 0)
        self.assertEqual(info["filter"], 1)
        self.assertEqual(info["types"], ["EQUIPMENT_FAULT_ACTIVE", "TELEMETRY_STALE", "DEVICE_OFFLINE"])
        self.assertEqual(info["sources"], ["PLC", "PLATFORM", "PLATFORM"])

    def test_settings_state_read_only(self):
        self.open_state("vent_settings")
        info = self.browser.run("""
          var app = document.getElementById('app');
          var hashBefore = location.hash;
          app.querySelector('.settings-index a[data-scroll]').click();
          return {tabs: [...app.querySelectorAll('.state-tabs a')].map(a => a.innerText),
            groups: [...app.querySelectorAll('.settings-group h2')].map(h => h.innerText),
            cells: app.querySelectorAll('[data-setting-key]').length,
            unique: new Set([...app.querySelectorAll('[data-setting-key]')].map(e => e.getAttribute('data-setting-key'))).size,
            values: [...new Set([...app.querySelectorAll('[data-setting-key]')].map(e => e.innerText))],
            controls: app.querySelectorAll('button, input:not([data-filter-input=settings]), select, textarea, form').length,
            filter: app.querySelectorAll('[data-filter-input=settings]').length,
            note: app.innerText.indexOf('9 slot = năng lực cấu hình tối đa') >= 0,
            hashUnchanged: location.hash === hashBefore, text: app.innerText};""")
        self.assertEqual(info["tabs"], ["Tổng quan", "Giám sát", "Lịch sử", "Cảnh báo", "Cài đặt"])
        self.assertEqual(len(info["groups"]), 6)
        self.assertEqual((info["cells"], info["unique"]), (224, 224))
        self.assertEqual(info["values"], ["--"])
        self.assertEqual(info["controls"], 0)
        self.assertEqual(info["filter"], 1)
        self.assertTrue(info["note"])
        self.assertTrue(info["hashUnchanged"])
        self.assertIn("Chỉ xem · 224 thông số", info["text"])
        self.assertNotRegex(info["text"], r"\bD1[0-4]\d\d\b")

    def test_mobile_iframe_has_real_390px_width_and_no_page_overflow(self):
        element_key = "element-6066-11e4-a52e-4f735466cecf"
        self.browser.resize(1280, 1000)
        try:
            self.browser._session("POST", "/url", {"url": self.server.base_url + "/deploy/thingsboard/mobile_frame.html"})
            frame = self.browser._session("POST", "/element", {"using": "css selector", "value": "#device"})[element_key]
            self.browser._session("POST", "/frame", {"id": {element_key: frame}})
            self.browser.run("location.href = arguments[0]", self.url + "#default")
            self.browser.wait_for("return !!document.querySelector('.vent-header') && window.innerWidth === 390")
            for state in ("default", "vent_detail", "vent_history", "vent_alarms", "vent_settings"):
                self.browser.run("location.hash = arguments[0]", state)
                self.browser.wait_for("return !!document.querySelector('.state-tabs a.active[href=\"#%s\"]')" % state)
                overflow = self.browser.run("return document.documentElement.scrollWidth - document.documentElement.clientWidth")
                self.assertLessEqual(overflow, 0, state)
        finally:
            self.browser._session("POST", "/frame/parent", {})
            self.browser.resize(1920, 1080)


if __name__ == "__main__":
    unittest.main()
