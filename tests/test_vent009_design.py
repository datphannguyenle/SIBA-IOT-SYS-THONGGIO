"""Checkpoint local: redesign phải đổi hình thức nhưng giữ dữ liệu chỉ đọc."""
import unittest

from webdriver_support import Browser, StaticServer, geckodriver_path


@unittest.skipUnless(geckodriver_path(), 'Cần Firefox/geckodriver để xác minh giao diện')
class ReferenceDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = StaticServer().__enter__()
        cls.browser = Browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.__exit__(None, None, None)

    def test_monitoring_uses_new_visual_surface(self):
        self.browser.open(self.server.base_url + '/dashboard/design-preview.html#vent_detail')
        result = self.browser.run("""
          return {
            panel:getComputedStyle(document.querySelector('.detail-main')).backgroundImage,
            iconCount:document.querySelectorAll('.kpi svg').length,
            fields:document.querySelectorAll('.operation-cell').length,
            fans:document.querySelectorAll('.synoptic .fan').length,
            writable:document.querySelectorAll('input:not([type=search]),textarea,select').length
          };
        """)
        self.assertIn('gradient', result['panel'])
        self.assertGreaterEqual(result['iconCount'], 4)
        self.assertEqual(result['fields'], 8)
        self.assertEqual(result['fans'], 6)
        self.assertEqual(result['writable'], 0)

    def test_approved_style_is_shared_with_settings(self):
        self.browser.open(self.server.base_url + '/dashboard/design-preview.html#vent_detail')
        self.browser.run("document.querySelector('[data-nav=vent_settings]').click()")
        self.browser.wait_for("return !!document.querySelector('.settings-index')")
        self.assertIn('gradient', self.browser.run("return getComputedStyle(document.querySelector('.panel')).backgroundImage"))

    def test_alarm_counts_derive_from_fixture_not_reference_image(self):
        self.browser.open(self.server.base_url + '/dashboard/design-preview.html#vent_alarms')
        self.assertEqual(self.browser.run("return [...document.querySelectorAll('.kpi__value')].map(e=>e.textContent)"), ['3','2','1','--'])
        self.assertEqual(self.browser.run("return document.querySelector('.alarm-donut').getAttribute('aria-label')"), '2 nghiêm trọng, 1 cảnh báo, 0 mức khác')

    def test_history_cards_explain_sample_average_and_missing_data(self):
        self.browser.open(self.server.base_url + '/dashboard/design-preview.html#vent_history')
        self.assertEqual(self.browser.run("return [...document.querySelectorAll('.kpi__value')].map(e=>e.textContent)"), ['27.1 °C','75.6 %RH','--','7'])
        self.assertIn('không phải TB theo thời gian', self.browser.run("return document.querySelector('.kpi__quality').textContent"))


if __name__ == '__main__':
    unittest.main()
