"""Tổng alarm dùng totalElements, không suy từ độ dài trang; không ghi ThingsBoard."""
import pathlib
import unittest
try:
    from webdriver_support import Browser, ROOT
except ModuleNotFoundError:
    from tests.webdriver_support import Browser, ROOT


class AlarmTotalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = Browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()

    def test_total_and_failure_and_cleanup(self):
        source = (ROOT / 'dashboard/alarm-total-subscription.js').read_text()
        result = self.browser.run(source + '''
          var opt, link, state, destroyed=0, cancelled=0;
          var sub={alarms:{data:[{}],totalElements:287},
            subscribeForAlarms:function(p){link=p;},destroy:function(){destroyed++;}};
          var ctx={subscriptionApi:{createSubscription:function(o){opt=o;return {
            subscribe:function(handler){handler.next(sub);return {unsubscribe:function(){cancelled++;}};}};}}};
          var h=VentilationAlarmTotal.attach(ctx,{alarmSource:{type:'entity'}},function(s){state=Object.assign({},s);});
          var initial=h.state.total;
          opt.callbacks.onDataUpdated(sub); var total=state.total;
          opt.callbacks.onDataUpdateError(); var failed=state.total===null && !state.loaded;
          sub.alarms={data:[],totalElements:0};opt.callbacks.onDataUpdated(sub); var zero=state.total;
          h.destroy();return {initial:initial,total:total,failed:failed,zero:zero,
            destroyed:destroyed,cancelled:cancelled,status:link.statusList,
            longWindow:opt.timeWindowConfig.realtime.timewindowMs===315360000000,propagate:link.searchPropagatedAlarms};
        ''')
        self.assertIsNone(result['initial'])
        self.assertEqual(result['total'], 287)
        self.assertTrue(result['failed'])
        self.assertEqual(result['zero'], 0)
        self.assertEqual(result['destroyed'], 1)
        self.assertEqual(result['cancelled'], 1)
        self.assertEqual(result['status'], ['ACTIVE'])
        self.assertTrue(result['longWindow'])
        self.assertFalse(result['propagate'])
