/* VENT-012: tổng alarm ACTIVE từ subscription nền tảng, không lấy độ dài trang. */
(function (root) {
  "use strict";
  function attach(ctx, options, changed) {
    var dead = false, subscription = null, request = null;
    var state = {loaded: false, total: null, error: false};
    function publish(sub) {
      if (dead) return;
      var page = (sub || subscription || {}).alarms;
      if (!page || !Array.isArray(page.data) || typeof page.totalElements !== "number") return;
      state.loaded = true; state.error = false; state.total = page.totalElements;
      changed(state);
    }
    function failure() {
      if (dead) return;
      state.loaded = false; state.total = null; state.error = true; changed(state);
    }
    if (options && options.alarmSource && ctx.subscriptionApi) {
      request = ctx.subscriptionApi.createSubscription({
        type: "alarm", alarmSource: options.alarmSource,
        // Alarm subscription cần timeWindowConfig hợp lệ khi không dùng timewindow dashboard.
        // 10 năm chỉ là cửa sổ truy vấn kỹ thuật để không bỏ alarm ACTIVE lâu ngày.
        useDashboardTimewindow: false,
        timeWindowConfig: {realtime: {timewindowMs: 315360000000}},
        callbacks: {onDataUpdated: publish, onDataUpdateError: failure}
      }, true).subscribe({next: function (sub) {
        if (dead) { sub.destroy(); return; }
        subscription = sub;
        // Không giới hạn cửa sổ: alarm vẫn ACTIVE từ lâu cũng phải được đếm.
        sub.subscribeForAlarms({page: 0, pageSize: 1,
          statusList: ["ACTIVE"], severityList: [], typeList: [],
          searchPropagatedAlarms: false,
          sortOrder: {key: {type: "ALARM_FIELD", key: "createdTime"}, direction: "DESC"}
        }, null);
      }, error: failure});
    }
    return {state: state, destroy: function () {
      dead = true;
      if (request && request.unsubscribe) request.unsubscribe();
      if (subscription && subscription.destroy) subscription.destroy();
      subscription = null;
    }};
  }
  root.VentilationAlarmTotal = {attach: attach};
}(window));
