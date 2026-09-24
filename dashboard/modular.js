/* VENT-010 component renderer; view model is kept inside each render closure. */
(function (window) {
  "use strict";
  var serial = 0;
  var L = {RUNNING:"Đang chạy",STOPPED:"Đã dừng",ONLINE:"Trực tuyến",OFFLINE:"Ngoại tuyến",CURRENT:"Hiện tại",STALE:"Dữ liệu cũ",HISTORICAL:"Lịch sử",UNKNOWN:"Chưa rõ",NORMAL:"Bình thường",ACTIVE:"Đang bật",CRITICAL:"Nghiêm trọng",MAJOR:"Cao",MINOR:"Thấp",WARNING:"Cảnh báo",INDETERMINATE:"Không xác định",NONE:"Không có",NOT_CONFIGURED:"Chưa cấu hình",MANUAL:"Thủ công",AUTO:"Tự động",STEP:"Theo cấp",VFD:"VFD",ENABLED:"Bật",DISABLED:"Tắt",ACTUAL_TEMPERATURE:"Nhiệt độ thực",PERCEIVED_TEMPERATURE:"Nhiệt độ cảm nhận"};
  function esc(v){return String(v==null?"":v).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];});}
  function miss(v){return v===null||v===undefined||v==="";} function txt(v){return miss(v)?"--":(L[v]||String(v));}
  function met(vm,k){return (vm.metrics||{})[k]||{key:k,value:null,quality:"UNKNOWN",configured:true,unit:""};}
  function val(x,k){x=x||{};var v=x.configured===false?"NOT_CONFIGURED":txt(x.value);return '<span'+(k?' data-metric-key="'+esc(k)+'"':"")+'>'+esc(v)+(!miss(x.value)&&typeof x.value==="number"&&x.unit?' <small>'+esc(x.unit)+'</small>':"")+'</span>';}
  function scls(v){return 'vm-status vm-status--'+esc(v||"UNKNOWN");} function demo(vm){return vm&&(vm.source==="fixture"||vm.demo===true);}
  function provenance(vm){var p=vm&&vm.provenance||{},kind=String(p.kind||(demo(vm)?"DEMO":"LIVE")).toUpperCase(),defaults={SIM:"Dữ liệu mô phỏng",DEMO:"Dữ liệu minh họa",LIVE:"Dữ liệu trực tiếp"};kind=["SIM","DEMO","LIVE"].indexOf(kind)>=0?kind:(demo(vm)?"DEMO":"LIVE");return {kind:kind,label:p.label||defaults[kind],note:p.note||""};}
  function provenanceText(vm){var p=provenance(vm);return p.kind+" · "+p.label+(p.note?" · "+p.note:"");}
  function barn(vm,p){var b=vm.barns||[],id=(p||{}).barnId;if(id)return b.filter(function(x){return x.id===id;})[0]||null;return b.filter(function(x){return x.label===(vm.scope||{}).selectedBarn;})[0]||b[0]||null;}
  function pilot(vm,p){var b=barn(vm,p);return !demo(vm)||!!b&&b.label===(vm.scope||{}).selectedBarn;}
  function nav(state,b){return 'data-nav="'+state+'"'+(b&&b.id?' data-barn-id="'+esc(b.id)+'"':"")+(b&&b.entityType?' data-barn-entity-type="'+esc(b.entityType)+'"':"")+(b&&b.label?' data-barn-label="'+esc(b.label)+'"':"");}
  function notice(vm,p,what){var b=barn(vm,p),a=(vm.barns||[]).filter(function(x){return x.label===(vm.scope||{}).selectedBarn;})[0];return '<section class="vm-panel vm-nonpilot"><p class="vm-eyebrow">NHÀ ĐƯỢC CHỌN</p><h2>'+esc((b||{}).label||"Không tìm thấy nhà")+'</h2><p>Nhà này mới có thông tin tóm tắt. Chưa có dữ liệu chi tiết để hiển thị '+esc(what)+'.</p>'+(b?'<dl><div><dt>Kết nối</dt><dd class="'+scls(b.connectivity)+'">'+esc(txt(b.connectivity))+'</dd></div><div><dt>Độ tươi dữ liệu</dt><dd class="'+scls(b.freshness)+'">'+esc(txt(b.freshness))+'</dd></div><div><dt>Chế độ</dt><dd>'+esc(txt(b.mode))+'</dd></div><div><dt>Cấp hiển thị</dt><dd>'+esc(b.stage==null?"--":b.stage)+'</dd></div></dl>':"")+(a?'<button type="button" class="vm-back" '+nav("vent_detail",a)+'>Xem nhà mẫu '+esc(a.label)+'</button>':"")+'</section>';}
  function header(vm,p){var b=barn(vm,p),st=p.state||"default",scope=[(vm.scope||{}).farm,(vm.scope||{}).area].filter(Boolean).map(esc).join(" · "),source=provenance(vm),badge='<b class="vm-badge" title="'+esc(source.label)+'">'+esc(source.kind)+'</b>',tabs='<nav class="vm-tabs">'+[["vent_detail","Giám sát"],["vent_history","Lịch sử"],["vent_alarms","Cảnh báo"],["vent_settings","Cài đặt"]].map(function(x){return '<button type="button" '+nav(x[0],b)+' class="'+(st===x[0]?"is-active":"")+'">'+x[1]+'</button>';}).join("")+'</nav>';if(st==="default")return '<header class="vm-header vm-header--home"><div><p class="vm-eyebrow">SIBA · THÔNG GIÓ</p><h1>Tổng quan toàn trại</h1><p class="vm-muted">Giám sát chỉ xem · '+esc(provenanceText(vm))+'</p></div><div class="vm-header__meta">'+(scope?'<span>'+scope+'</span>':"")+badge+'</div></header>';return '<header class="vm-header vm-header--detail"><div class="vm-header__line"><button type="button" class="vm-back" '+nav("default",b)+'>← Tổng quan</button><div class="vm-header__title"><p class="vm-eyebrow">SIBA · THÔNG GIÓ</p><h1>'+esc((b||{}).label||(vm.scope||{}).selectedBarn||"Nhà chưa chọn")+'</h1></div>'+tabs+'<span class="vm-header__scope">'+scope+'</span>'+badge+'</div></header>';}
  function card(n,v,note,tone){return '<article class="vm-card '+(tone?'vm-card--'+tone:"")+'"><p>'+esc(n)+'</p><b>'+v+'</b><small>'+esc(note||"")+'</small></article>';}
  function overview(vm){var q=vm.summary||{},source=provenanceText(vm);return '<section class="vm-overview"><div class="vm-kpis">'+card("Số nhà",esc(q.barns==null?"--":q.barns),"Toàn trại · "+source)+card("Trực tuyến",esc(q.online==null?"--":q.online),source,"ok")+card("Cần chú ý",esc(q.attention==null?"--":q.attention),source,"warn")+card("Cảnh báo đang mở",esc(q.activeAlarms==null?"--":q.activeAlarms),source,"danger")+'</div><section class="vm-panel"><div class="vm-panel__head"><div><h2>Chọn nhà</h2><p>Chọn nhà để vào ngữ cảnh giám sát.</p></div><label class="vm-search">Tìm nhà <input type="search" data-filter="barn"></label></div><div class="vm-barn-grid" data-filter-list="barn">'+(vm.barns||[]).map(function(b){var f=[b.label,b.connectivity,b.freshness,b.mode,b.alarm].join(" ").toLowerCase();return '<button type="button" class="vm-barn" '+nav("vent_detail",b)+' data-filter-text="'+esc(f)+'"><b>'+esc(b.label)+(b.identity==="SYNTHETIC"?' <small>MINH HỌA</small>':"")+'</b><span class="vm-barn__state"><strong class="'+scls(b.connectivity)+'">'+esc(txt(b.connectivity))+'</strong><span>Dữ liệu: '+esc(txt(b.freshness))+'</span></span><span class="vm-barn__mode">'+esc(txt(b.mode))+' · Cấp '+esc(b.stage==null?"--":b.stage)+'</span></button>';}).join("")+'</div><p class="vm-empty" hidden>Không có nhà phù hợp.</p>'+((vm.barns||[]).length?"":'<p class="vm-notice">'+(demo(vm)?"Fixture demo chưa khai báo nhà nào.":"Chưa có nhà nào: gán datasource nhiều entity (alias theo loại thiết bị) và khai keyMap cho widget này.")+'</p>')+'</section></section>';}
  function kpis(vm,p){if(!pilot(vm,p))return notice(vm,p,"các chỉ số môi trường");return '<section class="vm-kpis">'+[["Nhiệt độ trong nhà","indoorTemperatureAvg"],["Nhiệt độ ngoài trời","outdoorTemperature"],["Độ ẩm trong nhà","relativeHumidity"],["Nhiệt độ cảm nhận","perceivedTemperature"]].map(function(r){var m=met(vm,r[1]);return card(r[0],val(m,r[1]),m.configured===false?"Chưa cấu hình":txt(m.quality),m.quality==="CURRENT"?"ok":"");}).join("")+'</section>';}
  function synoptic(vm,p){if(!pilot(vm,p))return notice(vm,p,"sơ đồ thiết bị");var flags='<div class="vm-flags">'+(vm.systemFlags||[]).map(function(f){return '<span class="'+scls(f.value)+'">'+esc(f.label||f.key)+': '+esc(txt(f.value))+'</span>';}).join("")+'</div>', lv=vm.louvers||[],louverCards='<div class="vm-louver-cards">'+lv.map(function(x){return '<div><b>'+esc(x.label||"Cửa chớp")+'</b><span>'+val(x,x.key)+'</span><small>'+esc(txt(x.quality))+'</small></div>';}).join("")+'</div>';if(p.__narrow)return '<section class="vm-panel"><h2>Sơ đồ thông gió</h2>'+flags+louverCards+'<div class="vm-device-list">'+(vm.equipment||[]).map(function(d){return '<div><b>'+esc(d.label)+'</b><span class="'+scls(d.state)+'">'+esc(d.configured===false?"Chưa cấu hình":txt(d.state))+'</span><small>'+esc(txt(d.quality))+'</small></div>';}).join("")+'</div></section>';var id="vm-svg-"+(++serial),fans=(vm.equipment||[]).slice(0,6),pumps=(vm.equipment||[]).slice(6,8);function lou(x,y){return '<g class="vm-svg-louver"><rect x="155" y="'+y+'" width="590" height="29"/><path d="M160 '+(y+5)+'H740M160 '+(y+11)+'H740M160 '+(y+17)+'H740M160 '+(y+23)+'H740"/><text x="450" y="'+(y-8)+'">'+esc((x||{}).label||"Cửa chớp")+' · '+esc(x&&typeof x.value==="number"?x.value+" "+x.unit:"--")+'</text></g>';}return '<section class="vm-panel vm-synoptic"><h2>Sơ đồ thông gió</h2><p class="vm-muted">Sơ đồ chỉ đọc; cờ hệ thống không chỉ rõ thiết bị lỗi.</p>'+flags+'<svg class="vm-barn-svg" viewBox="0 0 900 375"><defs><linearGradient id="'+id+'-wall" x2="0" y2="1"><stop stop-color="#103a52"/><stop offset="1" stop-color="#032133"/></linearGradient></defs><path class="vm-svg-wall" d="M70 95 450 22 830 95V305H70Z"/><path class="vm-svg-roof" d="M48 104 450 20 852 104 850 111 450 30 50 111Z"/><path class="vm-svg-frame" d="M75 105V304M825 105V304M75 115H825M75 295H825"/>'+lou(lv[0],80)+lou(lv[1],269)+fans.map(function(f,i){var x=150+i*120;return '<g class="vm-svg-fan '+scls(f.state)+'"><rect x="'+(x-42)+'" y="151" width="84" height="84"/><circle cx="'+x+'" cy="193" r="35"/><g>'+[0,72,144,216,288].map(function(a){return '<path transform="rotate('+a+' '+x+' 193)" d="M'+x+' 188C'+(x+4)+' 151 '+(x+37)+' 158 '+(x+25)+' 175C'+(x+20)+' 185 '+(x+10)+' 193 '+x+' 193Z"/>';}).join("")+'</g><text x="'+x+'" y="140">'+esc(f.label)+'</text><text x="'+x+'" y="249">'+esc(txt(f.state))+'</text></g>';}).join("")+pumps.map(function(d,i){var x=260+i*340;return '<g class="vm-svg-pump"><path d="M'+x+' 312v20h-40v14"/><rect x="'+(x-58)+'" y="342" width="35" height="24"/><text x="'+(x+66)+'" y="351">'+esc(d.label)+'</text><text x="'+(x+66)+'" y="368">'+esc(txt(d.state))+'</text></g>';}).join("")+'</svg>'+louverCards+'</section>';}
  function controller(vm,p){if(!pilot(vm,p))return notice(vm,p,"tóm tắt bộ điều khiển");var rows=[["Kết nối",{value:(vm.controller||{}).online},"controllerOnline"],["Chế độ",met(vm,"operatingMode"),"operatingMode"],["Cơ sở điều khiển",met(vm,"controlBasis"),"controlBasis"],["Điều khiển quạt",met(vm,"fanControlMode"),"fanControlMode"],["Cấp hiện tại",{value:(vm.controller||{}).stageDisplay},"fanStage"],["Khử ẩm",met(vm,"dehumidificationEnabled"),"dehumidificationEnabled"],["Chất lượng dữ liệu",met(vm,"dataQuality"),"dataQuality"]], extra=[["Tốc độ gió","airSpeed"],["Lưu lượng gió","airFlow"],["Nước tiêu thụ (tổng tích lũy)","waterConsumptionTotal"],["Lưu lượng nước","waterFlow"]];function r(x){return '<div><dt>'+esc(x[0])+'</dt><dd>'+val(x[1],x[2])+'</dd></div>';}function e(x){return r([x[0],met(vm,x[1]),x[1]]);}var vfd=met(vm,"fanControlMode").value==="VFD"?'<h3 class="vm-subhead">VFD (tùy chọn)</h3><dl class="vm-summary">'+[["Tốc độ đặt kênh 1","fan01SpeedSetpoint"],["Tốc độ đặt kênh 2","fan02SpeedSetpoint"],["Phản hồi kênh 1","fan01SpeedFeedback"],["Phản hồi kênh 2","fan02SpeedFeedback"]].map(e).join("")+'</dl>':"";return '<section class="vm-controller"><section class="vm-panel"><h2>Bộ điều khiển</h2><dl class="vm-summary">'+rows.map(r).join("")+'</dl></section><section class="vm-panel"><h2>Dữ liệu bổ sung</h2><dl class="vm-summary">'+extra.map(e).join("")+'</dl>'+vfd+'</section></section>';}
  function metrics(vm,p){if(!pilot(vm,p))return notice(vm,p,"thông số vận hành");var a=[["Nhiệt độ đặt hiện tại","temperatureSetpointCurrent"],["Nhiệt độ cảm nhận đặt","perceivedTemperatureSetpointCurrent"],["Độ ẩm đặt hiện tại","humiditySetpointCurrent"],["Nhiệt độ cảm biến 1","indoorTemperature01"],["Nhiệt độ cảm biến 2","indoorTemperature02"],["Tổng đàn","pigCount"],["Heo chết tích lũy","pigDeathCount"],["Ngày tuổi","pigAgeDay"]];return '<section class="vm-panel"><h2>Thông số vận hành</h2><p class="vm-muted">`--` là không có dữ liệu, không phải 0.</p><div class="vm-metrics">'+a.map(function(x){var m=met(vm,x[1]);return '<div><small>'+esc(x[0])+'</small><b>'+val(m,x[1])+'</b><em>'+esc(m.configured===false?"Chưa cấu hình":txt(m.quality))+'</em></div>';}).join("")+'</div></section>';}
  function history(vm,p){if(!pilot(vm,p))return notice(vm,p,"lịch sử môi trường");var r=vm.history||[],source=provenanceText(vm);if(!r.length)return '<section class="vm-panel vm-notice"><h2>Lịch sử môi trường</h2><p>Nguồn: '+esc(source)+'. Chưa có mẫu lịch sử.</p></section>';function path(k,d){var down=false;return r.map(function(x,i){if(typeof x[k]!=="number"){down=false;return "";}var y=245-(x[k]-d[0])/(d[1]-d[0]||1)*175,c=down?"L":"M";down=true;return c+(55+i*620/Math.max(1,r.length-1)).toFixed(1)+" "+y.toFixed(1);}).join("");}function dom(keys){var a=[];r.forEach(function(x){keys.forEach(function(k){if(typeof x[k]==="number")a.push(x[k]);});});var n=a.length?Math.min.apply(null,a):0,x=a.length?Math.max.apply(null,a):1,q=x-n||1;return [Math.floor((n-q*.12)*2)/2,Math.ceil((x+q*.12)*2)/2];}var t=dom(["indoorTemperatureAvg","outdoorTemperature","perceivedTemperature"]),h=dom(["relativeHumidity"]);function rows(keys){return r.slice().reverse().map(function(x){return '<tr><td>'+esc(x.ts?new Date(x.ts).toLocaleString("vi-VN"):"--")+'</td>'+keys.map(function(k){return '<td>'+esc(typeof x[k[0]]==="number"?x[k[0]]+" "+k[1]:"--")+'</td>';}).join("")+'<td class="'+scls(x.quality)+'">'+esc(txt(x.quality))+'</td></tr>';}).join("");}var readings=[["indoorTemperatureAvg","Trong nhà","°C"],["outdoorTemperature","Ngoài trời","°C"],["perceivedTemperature","Cảm nhận","°C"],["relativeHumidity","Độ ẩm","%RH"],["airSpeed","Tốc độ gió","m/s"],["airFlow","Lưu lượng gió","m3/h"],["waterConsumptionTotal","Nước (tổng)","L"]];return '<section class="vm-history"><section class="vm-panel vm-history__chart"><h2>Lịch sử môi trường</h2><p class="vm-muted">Nguồn: '+esc(source)+'. Điểm thiếu tạo khoảng trống.</p><p class="vm-legend"><i class="inside"></i>Trong nhà <i class="outside"></i>Ngoài trời <i class="perceived"></i>Cảm nhận <i class="humidity"></i>Độ ẩm</p><div class="vm-chart-wrap"><svg class="vm-chart" viewBox="0 0 720 280"><path class="grid" d="M55 70H675M55 128H675M55 187H675M55 245H675"/><path class="inside" d="'+path("indoorTemperatureAvg",t)+'"/><path class="outside" d="'+path("outdoorTemperature",t)+'"/><path class="perceived" d="'+path("perceivedTemperature",t)+'"/><path class="humidity" d="'+path("relativeHumidity",h)+'"/><text x="4" y="44">'+esc(t[1])+ '°C</text><text x="678" y="44">'+esc(h[1])+'%</text><text x="55" y="266">'+esc(r[0].ts?new Date(r[0].ts).toLocaleTimeString("vi-VN",{hour:"2-digit",minute:"2-digit"}):"--")+'</text><text x="620" y="266">'+esc(r[r.length-1].ts?new Date(r[r.length-1].ts).toLocaleTimeString("vi-VN",{hour:"2-digit",minute:"2-digit"}):"--")+'</text></svg></div></section><section class="vm-panel vm-history__table"><div class="vm-panel__head"><div><h2>Bảng số liệu</h2><p>Nước là bộ đếm tổng tích lũy; không suy ra lượng theo ngày/lứa.</p></div></div><div class="vm-table-wrap"><table><thead><tr><th>Thời gian</th>'+readings.map(function(k){return '<th>'+esc(k[1])+'</th>';}).join("")+'<th>Chất lượng</th></tr></thead><tbody>'+rows(readings.map(function(k){return [k[0],k[2]];}))+'</tbody></table></div></section></section>';}
  function alarms(vm){var unloaded=vm.alarmsSource&&vm.alarmsSource.loaded===false,a=unloaded?[]:(vm.alarms||[]),on=a.filter(function(x){return x.status==="ACTIVE";}),source=provenanceText(vm),summary=unloaded?"--":on.length;return '<section class="vm-alarms"><section class="vm-panel"><div class="vm-panel__head"><div><h2>Cảnh báo</h2><p>Nguồn: '+esc(source)+' · chỉ xem.</p></div><div class="vm-alarm-summary"><b>'+esc(summary)+'</b><span>'+(unloaded?'chưa nạp':'đang hoạt động')+'</span></div></div>'+(unloaded?'<p class="vm-notice">-- chưa nạp cảnh báo</p>':'<div class="vm-table-wrap"><table><thead><tr><th>Mức</th><th>Nội dung</th><th>Nguồn</th><th>Đối tượng</th><th>Thời gian</th><th>Trạng thái</th></tr></thead><tbody>'+a.map(function(x){return '<tr><td class="'+scls(x.severity)+'">'+esc(txt(x.severity))+'</td><td>'+esc(x.type||"--")+'<br><small>'+esc(x.message||"")+'</small></td><td>'+esc(x.source||"UNKNOWN")+'</td><td>'+esc(x.originator||"--")+'</td><td>'+esc(x.created?new Date(x.created).toLocaleString("vi-VN"):"--")+'</td><td>'+esc(txt(x.status))+'</td></tr>';}).join("")+'</tbody></table></div>')+'</section></section>';}
  function settings(vm, p) {
    if (!pilot(vm, p)) return notice(vm, p, "cài đặt bộ điều khiển");
    var groups = vm.settings || [], active = +(p.settingsGroup || 0);
    var total = groups.reduce(function (n, group) { return n + group.count; }, 0);
    function cell(item) {
      return '<span data-setting-key="' + esc(item.key) + '" title="' + esc(item.label + ' · ' + item.key) + '">' + val(item) + '</span>';
    }
    function matrix(m) {
      var note = m.prefix === 'stage' ? '<p class="vm-notice">9 slot là sức chứa cấu hình, không phải số cấp đang vận hành.</p>' : '';
      return note + '<div class="vm-table-wrap"><table><thead><tr><th>' + esc(m.rowLabel) + '</th>' + m.fields.map(function (f) {
        return '<th>' + esc(f.label) + (f.unit ? '<br><small>' + esc(f.unit) + '</small>' : '') + (f.optional ? ' *' : '') + '</th>';
      }).join('') + '</tr></thead><tbody>' + m.slots.map(function (slot) {
        return '<tr><td>' + esc(m.rowLabel + ' ' + slot) + '</td>' + m.fields.map(function (f) {
          var item = m.cells[slot + ':' + f.id]; return '<td>' + (item ? cell(item) : '--') + '</td>';
        }).join('') + '</tr>';
      }).join('') + '</tbody></table></div>';
    }
    return '<section class="vm-panel vm-settings"><div class="vm-panel__head"><div><h2>Cài đặt bộ điều khiển</h2>' +
      '<p>Chỉ đọc · ' + total + ' thông số · -- là chưa có dữ liệu, không phải 0.</p></div>' +
      '<label class="vm-search">Tìm thông số <input type="search" data-filter="settings" placeholder="Tên hoặc mã thông số"></label></div>' +
      '<div class="vm-settings-tabs" role="tablist">' + groups.map(function (group, index) {
        return '<button type="button" role="tab" aria-selected="' + (index === active) + '" data-settings-tab="' + index +
          '" class="' + (index === active ? 'is-active' : '') + '">' + esc(group.name.replace('CÀI ĐẶT - ', '')) + ' <small>' + group.count + '</small></button>';
      }).join('') + '</div><div class="vm-search-results" hidden></div>' + groups.map(function (group, index) {
        return '<section class="vm-settings-group" data-settings-group="' + index + '"' + (index === active ? '' : ' hidden') +
          '><h2>' + esc(group.name) + '</h2><div class="vm-settings-list">' + (group.scalars || []).map(function (item) {
            return '<div class="vm-setting"><span>' + esc(item.label) + '</span><b>' + cell(item) + '</b></div>';
          }).join('') + '</div>' + (group.matrices || []).map(matrix).join('') + '</section>';
      }).join('') + '</section>';
  }
  function footer(vm){return '<footer class="vm-footer">Giám sát chỉ xem'+(demo(vm)?' · Bản minh họa '+esc(vm.fixtureVersion||""):"")+'</footer>';}
  function destroy(c){if(c&&c.__ventModularDestroy)c.__ventModularDestroy();}
  function render(c, vm, component, navigate, p) {
    if (!c) throw new Error('Thiếu container');
    destroy(c); p = Object.assign({}, p || {});
    p.__narrow = c.clientWidth > 0 && c.clientWidth < 560;
    c.classList.add('vent-modular'); c.classList.toggle('vm-narrow', c.clientWidth < 720);
    c.classList.toggle('vm-small', c.clientWidth < 460);
    c.setAttribute('data-vent-component', component);
    var fn = {header: header, overview: overview, kpis: kpis, synoptic: synoptic, controller: controller,
      metrics: metrics, history: history, alarms: alarms, settings: settings, footer: footer}[component];
    c.innerHTML = fn ? fn(vm || {}, p) : '';
    var selected = String(p.settingsGroup || 0);
    function selectGroup(index) {
      selected = index;
      c.querySelectorAll('[data-settings-group]').forEach(function (group) { group.hidden = group.getAttribute('data-settings-group') !== index; });
      c.querySelectorAll('[data-settings-tab]').forEach(function (tab) {
        var yes = tab.getAttribute('data-settings-tab') === index;
        tab.classList.toggle('is-active', yes); tab.setAttribute('aria-selected', String(yes));
      });
    }
    function click(event) {
      var target = event.target.closest('[data-nav],[data-settings-tab]');
      if (!target || !c.contains(target)) return;
      event.preventDefault();
      if (target.hasAttribute('data-settings-tab')) {
        var input = c.querySelector('[data-filter="settings"]'), results = c.querySelector('.vm-search-results');
        if (input) input.value = ''; if (results) { results.innerHTML = ''; results.hidden = true; }
        selectGroup(target.getAttribute('data-settings-tab')); return;
      }
      if (typeof navigate === 'function') navigate(target.getAttribute('data-nav'), {barnId: target.getAttribute('data-barn-id') || p.barnId, barnEntityType: target.getAttribute('data-barn-entity-type') || p.barnEntityType || null, barnLabel: target.getAttribute('data-barn-label') || p.barnLabel || null});
    }
    function input(event) {
      var target = event.target.closest('[data-filter]'); if (!target || !c.contains(target)) return;
      var query = target.value.trim().toLocaleLowerCase('vi-VN');
      if (target.getAttribute('data-filter') === 'settings') {
        var results = c.querySelector('.vm-search-results'); results.hidden = !query;
        if (!query) { results.innerHTML = ''; selectGroup(selected); return; }
        c.querySelectorAll('[data-settings-group]').forEach(function (group) { group.hidden = true; });
        var found = (vm.settings || []).reduce(function (all, group) { return all.concat(group.items); }, []).filter(function (item) {
          return (item.key + ' ' + item.label).toLocaleLowerCase('vi-VN').indexOf(query) >= 0;
        });
        results.innerHTML = '<p class="vm-muted">' + found.length + ' kết quả · chỉ đọc</p>' + found.map(function (item) {
          return '<div class="vm-setting"><span>' + esc(item.label) + '<small> · ' + esc(item.key) + '</small></span><b>' + val(item) + '</b></div>';
        }).join('');
      } else {
        var count = 0;
        c.querySelectorAll('[data-filter-text]').forEach(function (item) {
          item.hidden = item.getAttribute('data-filter-text').toLocaleLowerCase('vi-VN').indexOf(query) < 0;
          if (!item.hidden) count++;
        });
        var empty = c.querySelector('.vm-empty'); if (empty) empty.hidden = count > 0;
      }
    }
    c.addEventListener('click', click); c.addEventListener('input', input);
    c.__ventModularDestroy = function () {
      c.removeEventListener('click', click); c.removeEventListener('input', input); delete c.__ventModularDestroy;
    };
    return component;
  }
  window.VentilationModular={render:render,destroy:destroy,DETAIL_STATES:{kpis:"vent_detail",synoptic:"vent_detail",controller:"vent_detail",metrics:"vent_detail",history:"vent_history",alarms:"vent_alarms",settings:"vent_settings"}};
}(window));
