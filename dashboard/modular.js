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
  function provenanceText(vm){var p=provenance(vm);return (p.kind==="LIVE"?"":p.kind+" · ")+p.label+(p.note?" · "+p.note:"");}
  function barn(vm,p){var b=vm.barns||[],id=(p||{}).barnId;if(id)return b.filter(function(x){return x.id===id;})[0]||null;return b.filter(function(x){return x.label===(vm.scope||{}).selectedBarn;})[0]||b[0]||null;}
  function pilot(vm,p){var b=barn(vm,p);return !demo(vm)||!!b&&b.label===(vm.scope||{}).selectedBarn;}
  function nav(state,b){return 'data-nav="'+state+'"'+(b&&b.id?' data-barn-id="'+esc(b.id)+'"':"")+(b&&b.entityType?' data-barn-entity-type="'+esc(b.entityType)+'"':"")+(b&&b.label?' data-barn-label="'+esc(b.label)+'"':"");}
  function notice(vm,p,what){var b=barn(vm,p),a=(vm.barns||[]).filter(function(x){return x.label===(vm.scope||{}).selectedBarn;})[0];return '<section class="vm-panel vm-nonpilot"><p class="vm-eyebrow">NHÀ ĐƯỢC CHỌN</p><h2>'+esc((b||{}).label||"Không tìm thấy nhà")+'</h2><p>Nhà này mới có thông tin tóm tắt. Chưa có dữ liệu chi tiết để hiển thị '+esc(what)+'.</p>'+(b?'<dl><div><dt>Kết nối</dt><dd class="'+scls(b.connectivity)+'">'+esc(txt(b.connectivity))+'</dd></div><div><dt>Độ tươi dữ liệu</dt><dd class="'+scls(b.freshness)+'">'+esc(txt(b.freshness))+'</dd></div><div><dt>Chế độ</dt><dd>'+esc(txt(b.mode))+'</dd></div><div><dt>Cấp hiển thị</dt><dd>'+esc(b.stage==null?"--":b.stage)+'</dd></div></dl>':"")+(a?'<button type="button" class="vm-back" '+nav("vent_detail",a)+'>Xem nhà mẫu '+esc(a.label)+'</button>':"")+'</section>';}
  function header(vm,p){var b=barn(vm,p),st=p.state||"default",scope=[(vm.scope||{}).farm,(vm.scope||{}).area].filter(Boolean).map(esc).join(" · "),source=provenance(vm),
    badge='<span class="vm-shell__badge vm-shell__badge--src" title="'+esc(source.label)+'">'+esc(source.kind==='LIVE'?'TRỰC TIẾP':source.kind)+'</span>',
    tabs='<nav class="vm-tabs vm-shell__switches">'+[["default","Tổng quan"],["vent_detail","Giám sát"],["vent_history","Lịch sử"],["vent_alarms","Cảnh báo"],["vent_settings","Cài đặt"]].map(function(x){return '<button type="button" '+nav(x[0],b)+' class="vm-shell__switch '+(st===x[0]?"is-active":"")+'">'+x[1]+'</button>';}).join("")+'</nav>',
    brand=function(sub){return '<div class="vm-shell__brand">'+(p.hubDashboardId?'<a class="siba-home" href="/dashboards/'+encodeURIComponent(p.hubDashboardId)+'">← Tổng quan hệ thống</a>':'<p class="vm-eyebrow">SIBA OPERATIONS</p>')+'<h1>SIBA · <span>Hệ thống thông gió</span></h1><p class="vm-shell__sub">'+sub+'</p></div>';},
    meta=function(extra){return '<div class="vm-shell__meta">'+extra+(scope?'<span class="vm-shell__scope">'+scope+'</span>':"")+badge+'<span class="vm-shell__badge">CHỈ XEM</span></div>';};
    if(st==="default")return '<header class="vm-shell"><div class="vm-shell__line">'+brand(esc("Giám sát chỉ xem · "+provenanceText(vm)))+meta(tabs)+'</div></header>';
    return '<header class="vm-shell is-detail"><div class="vm-shell__line"><button type="button" class="vm-back vm-shell__back" '+nav("default",b)+'>← Tổng quan</button>'+brand(esc((b||{}).label||(vm.scope||{}).selectedBarn||"Nhà chưa chọn"))+meta(tabs)+'</div></header>';}
  function card(n,v,note,tone,icon){return '<article class="vm-card vm-kpi '+(tone?'vm-card--'+tone:"")+'"><div class="vm-kpi__icon"><span class="material-icons" aria-hidden="true">'+esc(icon||"insights")+'</span></div><div class="vm-kpi__body"><p>'+esc(n)+'</p><b>'+v+'</b><small>'+esc(note||"")+'</small></div></article>';}
  function overview(vm){var q=vm.summary||{},source=provenanceText(vm);return '<section class="vm-overview"><div class="vm-kpis">'+card("Số nhà",esc(q.barns==null?"--":q.barns),"Toàn trại · "+source,"","home_work")+card("Trực tuyến",esc(q.online==null?"--":q.online),source,"ok","wifi")+card("Cần chú ý",esc(q.attention==null?"--":q.attention),source,"warn","report_problem")+card("Cảnh báo đang mở",esc(q.activeAlarms==null?"--":q.activeAlarms),source,"danger","notifications_active")+'</div><section class="vm-panel"><div class="vm-panel__head"><div><h2>Chọn nhà</h2><p>Chọn nhà để vào ngữ cảnh giám sát.</p></div><label class="vm-search">Tìm nhà <input type="search" data-filter="barn"></label></div><div class="vm-barn-grid" data-filter-list="barn">'+(vm.barns||[]).map(function(b){var f=[b.label,b.connectivity,b.freshness,b.mode,b.alarm].join(" ").toLowerCase();return '<button type="button" class="vm-barn" '+nav("vent_detail",b)+' data-filter-text="'+esc(f)+'"><b>'+esc(b.label)+(b.identity==="SYNTHETIC"?' <small>MINH HỌA</small>':"")+'</b><span class="vm-barn__state"><strong class="'+scls(b.connectivity)+'">'+esc(txt(b.connectivity))+'</strong><span>Dữ liệu: '+esc(txt(b.freshness))+'</span></span><span class="vm-barn__mode">'+esc(txt(b.mode))+' · Cấp '+esc(b.stage==null?"--":b.stage)+'</span></button>';}).join("")+'</div><p class="vm-empty" hidden>Không có nhà phù hợp.</p>'+((vm.barns||[]).length?"":'<p class="vm-notice">'+(demo(vm)?"Fixture demo chưa khai báo nhà nào.":"Chưa có nhà nào: gán datasource nhiều entity (alias theo loại thiết bị) và khai keyMap cho widget này.")+'</p>')+'</section></section>';}
  function kpis(vm,p){if(!pilot(vm,p))return notice(vm,p,"các chỉ số môi trường");return '<section class="vm-kpis">'+[["Nhiệt độ trong nhà","indoorTemperatureAvg","home"],["Nhiệt độ ngoài trời","outdoorTemperature","wb_sunny"],["Độ ẩm trong nhà","relativeHumidity","water_drop"],["Nhiệt độ cảm nhận","perceivedTemperature","thermostat"]].map(function(r){var m=met(vm,r[1]);return card(r[0],val(m,r[1]),m.configured===false?"Chưa cấu hình":txt(m.quality),m.quality==="CURRENT"?"ok":"",r[2]);}).join("")+'</section>';}
  function synoptic(vm,p){if(!pilot(vm,p))return notice(vm,p,"sơ đồ thiết bị");var flags='<div class="vm-flags">'+(vm.systemFlags||[]).map(function(f){return '<span class="'+scls(f.value)+'">'+esc(f.label||f.key)+': '+esc(txt(f.value))+'</span>';}).join("")+'</div>', lv=vm.louvers||[],louverCards='<div class="vm-louver-cards">'+lv.map(function(x){return '<div><b>'+esc(x.label||"Cửa chớp")+'</b><span>'+val(x,x.key)+'</span><small>'+esc(txt(x.quality))+'</small></div>';}).join("")+'</div>';if(p.__narrow)return '<section class="vm-panel"><h2>Sơ đồ thông gió</h2>'+flags+louverCards+'<div class="vm-device-list">'+(vm.equipment||[]).map(function(d){return '<div><b>'+esc(d.label)+'</b><span class="'+scls(d.state)+'">'+esc(d.configured===false?"Chưa cấu hình":txt(d.state))+'</span><small>'+esc(txt(d.quality))+'</small></div>';}).join("")+'</div></section>';var eq=vm.equipment||[],fans=eq.slice(0,6),pumps=eq.slice(6,8),anyFan=fans.some(function(f){return f.state==="RUNNING";}),anyPump=pumps.some(function(d){return d.state==="RUNNING";});
    // Mô hình 2.5D: đầu hồi có 6 quạt, vách dọc có cửa chớp hông và giàn mát, mái có cửa chớp trần. Quạt quay, luồng gió chạy và màu đổi theo dữ liệu.
    function st(d){return d.configured===false?"NOCONF":(d.state||"UNKNOWN");}
    function badge(x,y,label,key){var m=met(vm,key),has=typeof m.value==="number"&&m.configured!==false;return '<g class="vm3-badge vm3-q--'+esc(m.quality||"UNKNOWN")+'"><rect x="'+x+'" y="'+y+'" width="118" height="30" rx="5"/><text class="k" x="'+(x+9)+'" y="'+(y+20)+'">'+esc(label)+'</text><text class="v" x="'+(x+110)+'" y="'+(y+20)+'">'+(has?esc(m.value+" "+(m.unit||"")):"--")+'</text></g>';}
    function pct(x){return x&&typeof x.value==="number"?Math.max(0,Math.min(100,x.value)):null;}
    var cols=[150,240,330],rows=[212,300],fanSvg=fans.map(function(f,i){var x=cols[i%3],y=rows[Math.floor(i/3)],c=st(f);return '<g class="vm3-fan vm3-fan--'+esc(c)+'"><rect x="'+(x-40)+'" y="'+(y-40)+'" width="80" height="80" rx="4"/><circle class="ring" cx="'+x+'" cy="'+y+'" r="33"/><g class="blades"><circle cx="'+x+'" cy="'+y+'" r="33" fill="none" stroke="none"/>'+[0,72,144,216,288].map(function(a){return '<path transform="rotate('+a+' '+x+' '+y+')" d="M'+x+' '+(y-4)+'C'+(x+5)+' '+(y-33)+' '+(x+30)+' '+(y-27)+' '+(x+21)+' '+(y-14)+'C'+(x+16)+' '+(y-7)+' '+(x+8)+' '+y+' '+x+' '+y+'Z"/>';}).join("")+'</g><circle class="hub" cx="'+x+'" cy="'+y+'" r="5"/><text class="n" x="'+(x-34)+'" y="'+(y-28)+'">'+(i+1)+'</text></g>';}).join("");
    var side=pct(lv[1]),ceil=pct(lv[0]),slats="";for(var k=0;k<7;k++){var sx=470+k*38,t=150-.125*(sx-420),b=370-.25*(sx-420),h=b-t,y1=t+h*.30,y2=t+h*.62,open=side===null?0:side/100;slats+='<path class="slat" d="M'+sx+' '+y1+'L'+(sx+30)+' '+(y1-3.75)+'L'+(sx+30-open*14)+' '+(y2-7.5+open*4)+'L'+(sx-open*14)+' '+(y2+open*4)+'Z"/>';}
    var inlets=[0,1,2].map(function(n){var x=470+n*120,y=112-n*13;return '<path class="inlet" d="M'+x+' '+y+'L'+(x+70)+' '+(y-8)+'L'+(x+92)+' '+(y+4)+'L'+(x+22)+' '+(y+12)+'Z"/><path class="inlet-open" style="opacity:'+(ceil===null?0:(.15+ceil/100*.85))+'" d="M'+(x+8)+' '+(y+2)+'L'+(x+66)+' '+(y-5)+'L'+(x+80)+' '+(y+3)+'L'+(x+22)+' '+(y+10)+'Z"/>';}).join("");
    var pumpSvg=pumps.map(function(d,i){var x=800+i*62,y=318-i*16,c=st(d);return '<g class="vm3-pump vm3-fan--'+esc(c)+'"><circle cx="'+x+'" cy="'+y+'" r="13"/><path d="M'+(x-5)+' '+(y+6)+'L'+(x+8)+' '+y+'L'+(x-5)+' '+(y-6)+'Z"/><text x="'+x+'" y="'+(y+30)+'">Bơm '+(i+1)+'</text></g>';}).join("");
    var legend=eq.map(function(d){return '<div class="vm3-item vm3-fan--'+esc(st(d))+'"><i></i><b>'+esc(d.label)+'</b><span>'+esc(d.configured===false?"Chưa cấu hình":txt(d.state))+'</span></div>';}).join("");
    return '<section class="vm-panel vm-synoptic vm3"><div class="vm3-head"><h2>Mô hình thông gió</h2>'+flags+'</div><div class="vm3-body"><svg class="vm-barn-svg vm3-svg" viewBox="0 0 1000 430" preserveAspectRatio="xMidYMid meet">'+
      '<path class="vm3-roof" d="M240 78 760 28 900 90 420 150Z"/><path class="vm3-roof-l" d="M60 150 240 78 420 150Z"/>'+inlets+
      '<path class="vm3-side" d="M420 150 900 90V250L420 370Z"/><path class="vm3-end" d="M60 150H420V370H60Z"/>'+
      '<path class="vm3-louver" d="M462 178.6 744 143.4V223.3L462 293.8Z"/>'+slats+
      '<path class="vm3-pad '+(anyPump?"is-wet":"")+'" d="M770 124 890 109V236L770 266Z"/><path class="vm3-pad-h" d="M770 150 890 135M770 178 890 163M770 206 890 191M770 234 890 219M800 120V258M830 116V251M860 113V243"/>'+
      (anyFan?'<path class="vm3-air" d="M760 300C660 330 560 350 440 372"/><path class="vm3-air" d="M740 215C640 235 560 250 440 270"/><path class="vm3-air out" d="M52 212H8M52 300H8"/>':'')+
      fanSvg+pumpSvg+
      '<text class="vm3-cap" x="240" y="396">Đầu hồi · quạt hút</text><text class="vm3-cap" x="600" y="352" transform="rotate(-14 600 352)">'+esc((lv[1]||{}).label||"Cửa chớp hông")+' · '+(side===null?"--":side+" %")+'</text><text class="vm3-cap" x="600" y="42" transform="rotate(-5.5 600 42)">'+esc((lv[0]||{}).label||"Cửa chớp trần")+' · '+(ceil===null?"--":ceil+" %")+'</text><text class="vm3-cap" x="832" y="96" transform="rotate(-7 832 96)">Giàn mát</text>'+
      badge(476,300,"T1","indoorTemperature01")+badge(610,268,"T2","indoorTemperature02")+badge(300,112,"Độ ẩm","relativeHumidity")+badge(872,12,"Ngoài trời","outdoorTemperature")+
      '</svg><div class="vm3-list">'+legend+'</div></div></section>';}
  function controller(vm,p){if(!pilot(vm,p))return notice(vm,p,"tóm tắt bộ điều khiển");var rows=[["Kết nối",{value:(vm.controller||{}).online},"controllerOnline"],["Chế độ",met(vm,"operatingMode"),"operatingMode"],["Cơ sở điều khiển",met(vm,"controlBasis"),"controlBasis"],["Điều khiển quạt",met(vm,"fanControlMode"),"fanControlMode"],["Cấp hiện tại",{value:(vm.controller||{}).stageDisplay},"fanStage"],["Khử ẩm",met(vm,"dehumidificationEnabled"),"dehumidificationEnabled"],["Chất lượng dữ liệu",met(vm,"dataQuality"),"dataQuality"]], extra=[["Tốc độ gió","airSpeed"],["Lưu lượng gió","airFlow"],["Nước tiêu thụ (tổng tích lũy)","waterConsumptionTotal"],["Lưu lượng nước","waterFlow"]];function r(x){return '<div><dt>'+esc(x[0])+'</dt><dd>'+val(x[1],x[2])+'</dd></div>';}function e(x){return r([x[0],met(vm,x[1]),x[1]]);}var vfd=met(vm,"fanControlMode").value==="VFD"?'<h3 class="vm-subhead">VFD (tùy chọn)</h3><dl class="vm-summary">'+[["Tốc độ đặt kênh 1","fan01SpeedSetpoint"],["Tốc độ đặt kênh 2","fan02SpeedSetpoint"],["Phản hồi kênh 1","fan01SpeedFeedback"],["Phản hồi kênh 2","fan02SpeedFeedback"]].map(e).join("")+'</dl>':"";return '<section class="vm-controller"><section class="vm-panel"><h2>Bộ điều khiển</h2><dl class="vm-summary">'+rows.map(r).join("")+'</dl></section><section class="vm-panel"><h2>Dữ liệu bổ sung</h2><dl class="vm-summary">'+extra.map(e).join("")+'</dl>'+vfd+'</section></section>';}
  function metrics(vm,p){if(!pilot(vm,p))return notice(vm,p,"thông số vận hành");var a=[["Nhiệt độ đặt hiện tại","temperatureSetpointCurrent"],["Nhiệt độ cảm nhận đặt","perceivedTemperatureSetpointCurrent"],["Độ ẩm đặt hiện tại","humiditySetpointCurrent"],["Nhiệt độ cảm biến 1","indoorTemperature01"],["Nhiệt độ cảm biến 2","indoorTemperature02"],["Tổng đàn","pigCount"],["Heo chết tích lũy","pigDeathCount"],["Ngày tuổi","pigAgeDay"]];return '<section class="vm-panel"><h2>Thông số vận hành</h2><p class="vm-muted">`--` là không có dữ liệu, không phải 0.</p><div class="vm-metrics">'+a.map(function(x){var m=met(vm,x[1]);return '<div><small>'+esc(x[0])+'</small><b>'+val(m,x[1])+'</b><em>'+esc(m.configured===false?"Chưa cấu hình":txt(m.quality))+'</em></div>';}).join("")+'</div></section>';}
  function history(vm,p){if(!pilot(vm,p))return notice(vm,p,"lịch sử môi trường");var r=vm.history||[],source=provenanceText(vm);var W=Math.max(360,Math.round(p.__chartW||720)),H=Math.max(140,Math.round(p.__chartH||280)),T=Math.round(H*.25),B=H-35,S=B-T;if(!r.length)return '<section class="vm-panel vm-notice"><h2>Lịch sử môi trường</h2><p>Nguồn: '+esc(source)+'. Chưa có mẫu lịch sử.</p></section>';function path(k,d){var down=false;return r.map(function(x,i){if(typeof x[k]!=="number"){down=false;return "";}var y=B-(x[k]-d[0])/(d[1]-d[0]||1)*S,c=down?"L":"M";down=true;return c+(55+i*(W-100)/Math.max(1,r.length-1)).toFixed(1)+" "+y.toFixed(1);}).join("");}function dom(keys){var a=[];r.forEach(function(x){keys.forEach(function(k){if(typeof x[k]==="number")a.push(x[k]);});});var n=a.length?Math.min.apply(null,a):0,x=a.length?Math.max.apply(null,a):1,q=x-n||1;return [Math.floor((n-q*.12)*2)/2,Math.ceil((x+q*.12)*2)/2];}var t=dom(["indoorTemperatureAvg","outdoorTemperature","perceivedTemperature"]),h=dom(["relativeHumidity"]);function rows(keys){return r.slice().reverse().map(function(x){return '<tr><td>'+esc(x.ts?new Date(x.ts).toLocaleString("vi-VN"):"--")+'</td>'+keys.map(function(k){return '<td>'+esc(typeof x[k[0]]==="number"?x[k[0]]+" "+k[1]:"--")+'</td>';}).join("")+'<td class="'+scls(x.quality)+'">'+esc(txt(x.quality))+'</td></tr>';}).join("");}var readings=[["indoorTemperatureAvg","Trong nhà","°C"],["outdoorTemperature","Ngoài trời","°C"],["perceivedTemperature","Cảm nhận","°C"],["relativeHumidity","Độ ẩm","%RH"],["airSpeed","Tốc độ gió","m/s"],["airFlow","Lưu lượng gió","m3/h"],["waterConsumptionTotal","Nước (tổng)","L"]];return '<section class="vm-history"><section class="vm-panel vm-history__chart"><h2>Lịch sử môi trường</h2><p class="vm-muted">Nguồn: '+esc(source)+'. Điểm thiếu tạo khoảng trống.</p><p class="vm-legend"><i class="inside"></i>Trong nhà <i class="outside"></i>Ngoài trời <i class="perceived"></i>Cảm nhận <i class="humidity"></i>Độ ẩm</p><div class="vm-chart-wrap"><svg class="vm-chart" viewBox="0 0 '+W+' '+H+'"><path class="grid" d="'+[0,1,2,3].map(function(g){return "M55 "+(T+Math.round(S*g/3))+"H"+(W-45);}).join("")+'"/><path class="inside" d="'+path("indoorTemperatureAvg",t)+'"/><path class="outside" d="'+path("outdoorTemperature",t)+'"/><path class="perceived" d="'+path("perceivedTemperature",t)+'"/><path class="humidity" d="'+path("relativeHumidity",h)+'"/><text x="4" y="'+(T-26)+'">'+esc(t[1])+ '°C</text><text x="'+(W-42)+'" y="'+(T-26)+'">'+esc(h[1])+'%</text><text x="55" y="'+(H-14)+'">'+esc(r[0].ts?new Date(r[0].ts).toLocaleTimeString("vi-VN",{hour:"2-digit",minute:"2-digit"}):"--")+'</text><text x="'+(W-100)+'" y="'+(H-14)+'">'+esc(r[r.length-1].ts?new Date(r[r.length-1].ts).toLocaleTimeString("vi-VN",{hour:"2-digit",minute:"2-digit"}):"--")+'</text></svg></div></section><section class="vm-panel vm-history__table"><div class="vm-panel__head"><div><h2>Bảng số liệu</h2><p>Nước là bộ đếm tổng tích lũy; không suy ra lượng theo ngày/lứa.</p></div></div><div class="vm-table-wrap"><table><thead><tr><th>Thời gian</th>'+readings.map(function(k){return '<th>'+esc(k[1])+'</th>';}).join("")+'<th>Chất lượng</th></tr></thead><tbody>'+rows(readings.map(function(k){return [k[0],k[2]];}))+'</tbody></table></div></section></section>';}
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
  // Vùng cuộn bên trong (danh sách nhà, bảng, cài đặt...). Widget vẽ lại mỗi 5 giây nên phải giữ vị trí cuộn
  // và nội dung ô tìm kiếm, nếu không danh sách nhảy về đầu và chữ đang gõ biến mất.
  var KEEP = ['.vm-barn-grid', '.vm-table-wrap', '.vm-settings', '.vm-controller', '.vm-synoptic', '.vm-history',
    '.vm-alarms>.vm-panel', '.vm-metrics-panel', '.vm-search-results'];
  function capture(c) {
    var scrolls = KEEP.map(function (sel) { return [].map.call(c.querySelectorAll(sel), function (e) { return e.scrollTop; }); });
    var inputs = [].map.call(c.querySelectorAll('[data-filter]'), function (e) {
      var on = document.activeElement === e;
      return {kind: e.getAttribute('data-filter'), value: e.value, focus: on, caret: on && e.selectionStart != null ? e.selectionStart : null};
    });
    return {top: c.scrollTop, scrolls: scrolls, inputs: inputs};
  }
  function restore(c, saved) {
    if (!saved) return;
    c.scrollTop = saved.top;
    saved.inputs.forEach(function (item) {
      var input = c.querySelector('[data-filter="' + item.kind + '"]');
      if (!input || !item.value) return;
      input.value = item.value; input.dispatchEvent(new Event('input', {bubbles: true}));
      if (item.focus) { input.focus(); try { input.setSelectionRange(item.caret, item.caret); } catch (e) {} }
    });
    KEEP.forEach(function (sel, i) { [].forEach.call(c.querySelectorAll(sel), function (e, j) { if (saved.scrolls[i][j]) e.scrollTop = saved.scrolls[i][j]; }); });
  }
  function render(c, vm, component, navigate, p) {
    if (!c) throw new Error('Thiếu container');
    destroy(c); p = Object.assign({}, p || {});
    p.__narrow = c.clientWidth > 0 && c.clientWidth < 560;
    c.classList.add('vent-modular'); c.classList.toggle('vm-narrow', c.clientWidth < 720);
    c.classList.toggle('vm-small', c.clientWidth < 460);
    c.setAttribute('data-vent-component', component);
    var fn = {header: header, overview: overview, kpis: kpis, synoptic: synoptic, controller: controller,
      metrics: metrics, history: history, alarms: alarms, settings: settings, footer: footer}[component];
    var saved = capture(c);
    c.innerHTML = fn ? fn(vm || {}, p) : '';
    // Biểu đồ vẽ theo kích thước THẬT của khung (1 đơn vị viewBox = 1px): đo, nếu lệch thì vẽ lại một lần.
    var wrap = component === 'history' ? c.querySelector('.vm-chart-wrap') : null;
    if (wrap && !p.__chartMeasured && wrap.clientWidth > 0 && wrap.clientHeight > 0 &&
        (Math.abs(wrap.clientWidth - (p.__chartW || 720)) > 6 || Math.abs(wrap.clientHeight - (p.__chartH || 280)) > 6)) {
      p.__chartW = wrap.clientWidth; p.__chartH = wrap.clientHeight; p.__chartMeasured = true;
      c.innerHTML = fn(vm || {}, p);
    }
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
    restore(c, saved);
    c.__ventModularDestroy = function () {
      c.removeEventListener('click', click); c.removeEventListener('input', input); delete c.__ventModularDestroy;
    };
    return component;
  }
  window.VentilationModular={render:render,destroy:destroy,DETAIL_STATES:{kpis:"vent_detail",synoptic:"vent_detail",controller:"vent_detail",metrics:"vent_detail",history:"vent_history",alarms:"vent_alarms",settings:"vent_settings"}};
}(window));
