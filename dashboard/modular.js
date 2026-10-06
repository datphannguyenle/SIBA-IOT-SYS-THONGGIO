/* VENT-010 component renderer; view model is kept inside each render closure. */
(function (window) {
  "use strict";
  var serial = 0;
  var L = {RUNNING:"Đang chạy",STOPPED:"Đã dừng",ONLINE:"Trực tuyến",OFFLINE:"Ngoại tuyến",CURRENT:"Hiện tại",STALE:"Dữ liệu cũ",HISTORICAL:"Lịch sử",UNKNOWN:"Chưa rõ",MISSING:"Thiếu dữ liệu",NORMAL:"Bình thường",ACTIVE:"Đang bật",CRITICAL:"Nghiêm trọng",MAJOR:"Cao",MINOR:"Thấp",WARNING:"Cảnh báo",INDETERMINATE:"Không xác định",NONE:"Không có",NOT_CONFIGURED:"Chưa cấu hình",MANUAL:"Thủ công",AUTO:"Tự động",STEP:"Theo cấp",VFD:"VFD",ENABLED:"Bật",DISABLED:"Tắt",ACTUAL_TEMPERATURE:"Nhiệt độ thực",PERCEIVED_TEMPERATURE:"Nhiệt độ cảm nhận"};
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
    badge=(p.showcaseBanner?'<span class="siba-showcase">'+esc(p.showcaseBanner)+'</span>':'')+'<span class="vm-shell__badge vm-shell__badge--src" title="'+esc(source.label)+'">'+esc(source.kind==='LIVE'?'TRỰC TIẾP':source.kind)+'</span>',
    tabs='<nav class="vm-tabs vm-shell__switches">'+[["default","Tổng quan"],["vent_detail","Giám sát"],["vent_history","Lịch sử"],["vent_alarms","Cảnh báo"],["vent_settings","Cài đặt"]].map(function(x){return '<button type="button" '+nav(x[0],b)+' class="vm-shell__switch '+(st===x[0]?"is-active":"")+'">'+x[1]+'</button>';}).join("")+'</nav>',
    brand=function(sub){return '<div class="vm-shell__brand">'+(p.hubDashboardId?'<a class="siba-home" href="/dashboards/'+encodeURIComponent(p.hubDashboardId)+'">← Tổng quan hệ thống</a>':'<p class="vm-eyebrow">SIBA OPERATIONS</p>')+'<h1>SIBA · <span>Hệ thống thông gió</span></h1><p class="vm-shell__sub">'+sub+'</p></div>';},
    meta=function(extra){return '<div class="vm-shell__meta">'+extra+(scope?'<span class="vm-shell__scope">'+scope+'</span>':"")+badge+'<span class="vm-shell__badge">CHỈ XEM</span></div>';};
    if(st==="default")return '<header class="vm-shell"><div class="vm-shell__line">'+brand(esc("Giám sát chỉ xem · "+provenanceText(vm)))+meta(tabs)+'</div></header>';
    return '<header class="vm-shell is-detail"><div class="vm-shell__line"><button type="button" class="vm-back vm-shell__back" '+nav("default",b)+'>← Tổng quan</button>'+brand(esc((b||{}).label||(vm.scope||{}).selectedBarn||"Nhà chưa chọn"))+meta(tabs)+'</div></header>';}
  function card(n,v,note,tone,icon){return '<article class="vm-card vm-kpi '+(tone?'vm-card--'+tone:"")+'"><div class="vm-kpi__icon"><span class="material-icons" aria-hidden="true">'+esc(icon||"insights")+'</span></div><div class="vm-kpi__body"><p>'+esc(n)+'</p><b>'+v+'</b><small>'+esc(note||"")+'</small></div></article>';}
  function overview(vm){var q=vm.summary||{},source=provenanceText(vm);return '<section class="vm-overview"><div class="vm-kpis">'+card("Số nhà",esc(q.barns==null?"--":q.barns),"Toàn trại · "+source,"","home_work")+card("Trực tuyến",esc(q.online==null?"--":q.online),source,"ok","wifi")+card("Cần chú ý",esc(q.attention==null?"--":q.attention),source,"warn","report_problem")+card("Cảnh báo đang mở",esc(q.activeAlarms==null?"--":q.activeAlarms),source,"danger","notifications_active")+'</div><section class="vm-panel"><div class="vm-panel__head"><div><h2>Chọn nhà</h2><p>Chọn nhà để vào ngữ cảnh giám sát.</p></div><label class="vm-search">Tìm nhà <input type="search" data-filter="barn"></label></div><div class="vm-barn-grid" data-filter-list="barn">'+(vm.barns||[]).map(function(b){var f=[b.label,b.connectivity,b.freshness,b.mode,b.alarm].join(" ").toLowerCase();return '<button type="button" class="vm-barn" '+nav("vent_detail",b)+' data-filter-text="'+esc(f)+'"><b>'+esc(b.label)+(b.identity==="SYNTHETIC"?' <small>MINH HỌA</small>':"")+'</b><span class="vm-barn__state"><strong class="'+scls(b.connectivity)+'">'+esc(txt(b.connectivity))+'</strong><span>Dữ liệu: '+esc(txt(b.freshness))+'</span></span><span class="vm-barn__mode">'+esc(txt(b.mode))+' · Cấp '+esc(b.stage==null?"--":b.stage)+'</span></button>';}).join("")+'</div><p class="vm-empty" hidden>Không có nhà phù hợp.</p>'+((vm.barns||[]).length?"":'<p class="vm-notice">'+(demo(vm)?"Fixture demo chưa khai báo nhà nào.":"Chưa có nhà nào: gán datasource nhiều entity (alias theo loại thiết bị) và khai keyMap cho widget này.")+'</p>')+'</section></section>';}
  function kpis(vm,p){if(!pilot(vm,p))return notice(vm,p,"các chỉ số môi trường");
    function dual(name,defs,icon){var ms=defs.map(function(d){return met(vm,d[1]);}),tone=ms.every(function(m){return m.quality==="CURRENT";})?"ok":"";return '<article class="vm-card vm-kpi '+(tone?'vm-card--ok':"")+'"><div class="vm-kpi__icon"><span class="material-icons" aria-hidden="true">'+esc(icon)+'</span></div><div class="vm-kpi__body"><p>'+esc(name)+'</p><b class="vm-kpi__dual">'+defs.map(function(d,i){return '<span><em>'+esc(d[0])+'</em>'+val(ms[i],d[1])+'</span>';}).join("")+'</b><small>'+esc(ms.every(function(m){return m.configured===false;})?"Chưa cấu hình":(function(q){return q.filter(function(x,i){return q.indexOf(x)===i;}).join(" · ");}(ms.map(function(m){return txt(m.configured===false?"NOT_CONFIGURED":m.quality);}))))+'</small></div></article>';}
    return '<section class="vm-kpis">'+dual("Nhiệt độ trong nhà",[["CB1","indoorTemperature01"],["CB2","indoorTemperature02"]],"home")+[["Nhiệt độ cảm nhận","perceivedTemperature","thermostat"]].map(function(r){var m=met(vm,r[1]);return card(r[0],val(m,r[1]),m.configured===false?"Chưa cấu hình":txt(m.quality),m.quality==="CURRENT"?"ok":"",r[2]);}).join("")+dual("Độ ẩm trong nhà",[["CB1","relativeHumidity"],["CB2","relativeHumidity02"]],"water_drop")+dual("Tốc độ gió",[["CB1","airSpeed"],["CB2","airSpeed02"]],"air")+'</section>';}
  function synoptic(vm,p){if(!pilot(vm,p))return notice(vm,p,"sơ đồ thiết bị");var flags='<div class="vm-flags">'+(vm.systemFlags||[]).map(function(f){var short={equipmentFaultActive:"Lỗi thiết bị",externalHighTemperatureAlarm:"Thermostat ngoài báo cao",temperatureLowAlarmActive:"Nhiệt độ thấp",temperatureHighAlarmActive:"Nhiệt độ cao",perceivedTemperatureLowAlarmActive:"Cảm nhận thấp",perceivedTemperatureHighAlarmActive:"Cảm nhận cao"};return '<span class="'+scls(f.value)+'">'+esc(short[f.key]||f.label||f.key)+': '+esc(txt(f.value))+'</span>';}).join("")+'</div>', lv=vm.louvers||[],louverCards='<div class="vm-louver-cards">'+lv.map(function(x){return '<div><b>'+esc(x.label||"Cửa chớp")+'</b><span>'+val(x,x.key)+'</span><small>'+esc(txt(x.quality))+'</small></div>';}).join("")+'</div>';if(p.__narrow)return '<section class="vm-panel"><h2>Sơ đồ thông gió</h2>'+flags+louverCards+'<div class="vm-device-list">'+(vm.equipment||[]).map(function(d){return '<div><b>'+esc(d.label)+'</b><span class="'+scls(d.state)+'">'+esc(d.configured===false?"Chưa cấu hình":txt(d.state))+'</span><small>'+esc(txt(d.quality))+'</small></div>';}).join("")+'</div></section>';var eq=vm.equipment||[],fans=eq.slice(0,6),pumps=eq.slice(6,8),anyFan=fans.some(function(f){return f.state==="RUNNING";}),anyPump=pumps.some(function(d){return d.state==="RUNNING";});
    // Mô hình 2.5D: đầu hồi có 6 quạt, vách dọc có cửa chớp hông và giàn mát, mái có cửa chớp trần. Quạt quay, luồng gió chạy và màu đổi theo dữ liệu.
    function st(d){return d.configured===false?"NOCONF":(d.state||"UNKNOWN");}
    function badge(x,y,label,key){var m=met(vm,key),has=typeof m.value==="number"&&m.configured!==false;return '<g class="vm3-badge vm3-q--'+esc(m.quality||"UNKNOWN")+'"><rect x="'+x+'" y="'+y+'" width="118" height="30" rx="5"/><text class="k" x="'+(x+9)+'" y="'+(y+20)+'">'+esc(label)+'</text><text class="v" x="'+(x+110)+'" y="'+(y+20)+'">'+(has?esc(m.value+" "+(m.unit||"")):"--")+'</text></g>';}
    function pct(x){return x&&typeof x.value==="number"?Math.max(0,Math.min(100,x.value)):null;}
    // Sơ đồ phẳng (mặt cắt dọc nhà): quạt hút bên trái, giàn mát bên phải, cửa chớp trần phía trên, cửa chớp hông ở giữa. Mọi thứ thẳng hàng theo lưới.
    var fanPos=[[81,168],[147,168],[213,168],[279,168],[147,252],[213,252]],fanSvg=fans.map(function(f,i){var x=fanPos[i][0],y=fanPos[i][1],c=st(f);return '<g class="vm3-fan vm3-fan--'+esc(c)+'"><rect x="'+(x-30)+'" y="'+(y-30)+'" width="60" height="60" rx="4"/><circle class="ring" cx="'+x+'" cy="'+y+'" r="25"/><g class="blades">'+(c==="RUNNING"?'<animateTransform attributeName="transform" type="rotate" from="0 '+x+' '+y+'" to="360 '+x+' '+y+'" dur="1.1s" repeatCount="indefinite"/>':'')+[0,72,144,216,288].map(function(a){return '<path transform="rotate('+a+' '+x+' '+y+') translate('+x+' '+y+') scale(.8) translate('+(-x)+' '+(-y)+')" d="M'+x+' '+(y-4)+'C'+(x+5)+' '+(y-31)+' '+(x+28)+' '+(y-25)+' '+(x+20)+' '+(y-13)+'C'+(x+15)+' '+(y-7)+' '+(x+8)+' '+y+' '+x+' '+y+'Z"/>';}).join("")+'</g><circle class="hub" cx="'+x+'" cy="'+y+'" r="4"/><text class="n" x="'+(x-26)+'" y="'+(y-19)+'">'+(i+1)+'</text></g>';}).join("");
    var side=pct(lv[1]),ceil=pct(lv[0]),slats="";for(var k=0;k<10;k++){var sx=356+k*38,o=side===null?0:side/100;slats+='<rect class="slat-bg" x="'+sx+'" y="196" width="28" height="44" rx="2"/><rect class="slat" x="'+sx+'" y="'+(196+44*(1-o))+'" width="28" height="'+(44*o)+'" rx="2"/>';}
    var inlets=[0,1,2,3].map(function(n){var x=366+n*96;return '<rect class="inlet" x="'+x+'" y="100" width="68" height="14" rx="2"/><rect class="inlet-open" x="'+x+'" y="100" width="'+(ceil===null?0:68*ceil/100)+'" height="14" rx="2"/>';}).join("");
    var pumpSvg=pumps.map(function(d,i){var x=940,y=170+i*92,c=st(d);return '<g class="vm3-pump vm3-fan--'+esc(c)+'"><path class="pl" d="M896 '+y+'H'+(x-14)+'"/><circle cx="'+x+'" cy="'+y+'" r="14"/><path d="M'+(x-5)+' '+(y+7)+'L'+(x+9)+' '+y+'L'+(x-5)+' '+(y-7)+'Z"/><text x="'+x+'" y="'+(y+32)+'">Bơm '+(i+1)+'</text></g>';}).join("");
    var ms=vm.misting||{state:null,configured:false},mc=ms.configured===false?"NOCONF":(ms.state||"UNKNOWN"),mistOn=mc==="RUNNING",
      nozzles=[0,1,2,3,4,5,6,7,8,9].map(function(n){var nx=352+n*42;return '<circle class="nz" cx="'+nx+'" cy="132" r="3.5"/>'+(mistOn?'<path class="vm3-drop" d="M'+nx+' 139V152"/>':'');}).join(""),
      mistSvg='<g class="vm3-mist vm3-mist--'+esc(mc)+'"><path class="pl" d="M330 132H770"/>'+nozzles+'<text class="vm3-cap vm3-cap--sm" x="545" y="162">Phun sương · '+esc(mc==="NOCONF"?"Chưa cấu hình":txt(ms.state))+'</text></g>';
    var legend=eq.concat([{label:"Phun sương",state:ms.state,configured:ms.configured}]).map(function(d){return '<div class="vm3-item vm3-fan--'+esc(st(d))+'"><i></i><b>'+esc(String(d.label).replace("Bơm làm mát","Bơm"))+'</b><span>'+esc(d.configured===false?"Chưa cấu hình":txt(d.state))+'</span></div>';}).join("");
    return '<section class="vm-panel vm-synoptic vm3"><div class="vm3-head"><h2>Mô hình thông gió</h2>'+flags+'</div><div class="vm3-body"><svg class="vm-barn-svg vm3-svg" viewBox="0 30 1000 350" preserveAspectRatio="xMidYMid meet">'+
      '<path class="vm3-roof" d="M30 92 470 44 910 92Z"/><rect class="vm3-end" x="30" y="92" width="880" height="250" rx="3"/><rect class="vm3-side" x="46" y="118" width="268" height="198" rx="3"/>'+
      inlets+slats+
      '<rect class="vm3-pad '+(anyPump?"is-wet":"")+'" x="776" y="118" width="120" height="198" rx="3"/><path class="vm3-pad-h" d="M776 151H896M776 184H896M776 217H896M776 250H896M776 283H896M806 118V316M836 118V316M866 118V316"/>'+
      (anyFan?'<path class="vm3-air" d="M766 168H324"/><path class="vm3-air" d="M766 252H324"/><path class="vm3-air out" d="M36 168H2M36 252H2"/>':'')+
      fanSvg+pumpSvg+mistSvg+
      '<text class="vm3-cap" x="180" y="366">Quạt hút (4 trên · 2 dưới)</text><text class="vm3-cap" x="836" y="366">Giàn mát</text><text class="vm3-cap" x="545" y="86">'+esc((lv[0]||{}).label||"Cửa chớp trần")+' · '+(ceil===null?"--":ceil+" %")+'</text><text class="vm3-cap" x="545" y="186">'+esc((lv[1]||{}).label||"Cửa chớp hông")+' · '+(side===null?"--":side+" %")+'</text>'+
      badge(372,252,"T1","indoorTemperature01")+badge(372,286,"T2","indoorTemperature02")+badge(508,252,"Ẩm 1","relativeHumidity")+badge(508,286,"Ẩm 2","relativeHumidity02")+badge(644,252,"Gió 1","airSpeed")+badge(644,286,"Gió 2","airSpeed02")+
      '</svg><div class="vm3-list">'+legend+'</div></div></section>';}
  function controller(vm,p){if(!pilot(vm,p))return notice(vm,p,"tóm tắt bộ điều khiển");var rows=[["Kết nối",{value:(vm.controller||{}).online},"controllerOnline"],["Chế độ",met(vm,"operatingMode"),"operatingMode"],["Cơ sở điều khiển",met(vm,"controlBasis"),"controlBasis"],["Điều khiển quạt",met(vm,"fanControlMode"),"fanControlMode"],["Cấp hiện tại",{value:(vm.controller||{}).stageDisplay},"fanStage"],["Khử ẩm",met(vm,"dehumidificationEnabled"),"dehumidificationEnabled"],["Chất lượng dữ liệu",met(vm,"dataQuality"),"dataQuality"]], extra=[["Hệ thống phun sương","mistingRun"],["Lưu lượng gió","airFlow"],["Nước tiêu thụ (tổng tích lũy)","waterConsumptionTotal"],["Lưu lượng nước","waterFlow"]];function r(x){return '<div><dt>'+esc(x[0])+'</dt><dd>'+val(x[1],x[2])+'</dd></div>';}function e(x){return r([x[0],met(vm,x[1]),x[1]]);}var vfd=met(vm,"fanControlMode").value==="VFD"?'<h3 class="vm-subhead">VFD (tùy chọn)</h3><dl class="vm-summary">'+[["Tốc độ đặt kênh 1","fan01SpeedSetpoint"],["Tốc độ đặt kênh 2","fan02SpeedSetpoint"],["Phản hồi kênh 1","fan01SpeedFeedback"],["Phản hồi kênh 2","fan02SpeedFeedback"]].map(e).join("")+'</dl>':"";return '<section class="vm-controller"><section class="vm-panel"><h2>Bộ điều khiển</h2><dl class="vm-summary">'+rows.map(r).join("")+'</dl></section><section class="vm-panel"><h2>Dữ liệu bổ sung</h2><dl class="vm-summary">'+extra.map(e).join("")+'</dl>'+vfd+'</section></section>';}
  function metrics(vm,p){if(!pilot(vm,p))return notice(vm,p,"thông số vận hành");var a=[["Nhiệt độ đặt","temperatureSetpointCurrent"],["Cảm nhận đặt","perceivedTemperatureSetpointCurrent"],["Độ ẩm đặt","humiditySetpointCurrent"],["Tổng đàn","pigCount"],["Heo chết","pigDeathCount"],["Ngày tuổi","pigAgeDay"]];return '<section class="vm-panel"><h2>Thông số vận hành</h2><p class="vm-muted">`--` là không có dữ liệu, không phải 0.</p><div class="vm-metrics">'+a.map(function(x){var m=met(vm,x[1]);return '<div><small>'+esc(x[0])+'</small><b>'+val(m,x[1])+'</b><em>'+esc(m.configured===false?"Chưa cấu hình":txt(m.quality))+'</em></div>';}).join("")+'</div></section>';}
  function history(vm,p){if(!pilot(vm,p))return notice(vm,p,"lịch sử môi trường");var r=vm.history||[],source=provenanceText(vm);var W=Math.max(360,Math.round(p.__chartW||720)),H=Math.max(140,Math.round(p.__chartH||280)),T=18,B=H-30,S=B-T;if(!r.length)return '<section class="vm-panel vm-history-empty"><h2>Lịch sử môi trường</h2><div class="vm-empty-chart"><span class="material-icons">show_chart</span><b>Chưa có mẫu lịch sử</b><span>Bộ điều khiển chưa gửi dữ liệu trong khoảng thời gian đang xem. Nguồn: '+esc(source)+'.</span></div></section>';function path(k,d){var down=false;return r.map(function(x,i){if(typeof x[k]!=="number"){down=false;return "";}var y=B-(x[k]-d[0])/(d[1]-d[0]||1)*S,c=down?"L":"M";down=true;return c+(55+i*(W-100)/Math.max(1,r.length-1)).toFixed(1)+" "+y.toFixed(1);}).join("");}function dom(keys){var a=[];r.forEach(function(x){keys.forEach(function(k){if(typeof x[k]==="number")a.push(x[k]);});});var n=a.length?Math.min.apply(null,a):0,x=a.length?Math.max.apply(null,a):1,q=x-n||1;return [Math.floor((n-q*.12)*2)/2,Math.ceil((x+q*.12)*2)/2];}var t=dom(["indoorTemperatureAvg","perceivedTemperature"]),h=dom(["relativeHumidity","relativeHumidity02"]);function rows(keys){return r.slice().reverse().map(function(x){return '<tr><td>'+esc(x.ts?new Date(x.ts).toLocaleString("vi-VN"):"--")+'</td>'+keys.map(function(k){return '<td>'+esc(typeof x[k[0]]==="number"?x[k[0]]+" "+k[1]:"--")+'</td>';}).join("")+'<td class="'+scls(x.quality)+'">'+esc(txt(x.quality))+'</td></tr>';}).join("");}var readings=[["indoorTemperatureAvg","Trong nhà","°C"],["perceivedTemperature","Cảm nhận","°C"],["relativeHumidity","Độ ẩm 1","%RH"],["relativeHumidity02","Độ ẩm 2","%RH"],["airSpeed","Gió 1","m/s"],["airSpeed02","Gió 2","m/s"],["airFlow","Lưu lượng gió","m3/h"],["waterConsumptionTotal","Nước (tổng)","L"]];return '<section class="vm-history"><section class="vm-panel vm-history__chart"><h2>Lịch sử môi trường</h2><p class="vm-muted">Nguồn: '+esc(source)+'. Điểm thiếu tạo khoảng trống.</p><p class="vm-legend"><i class="inside"></i>Trong nhà <i class="perceived"></i>Cảm nhận <i class="humidity"></i>Độ ẩm 1 <i class="humidity2"></i>Độ ẩm 2</p><div class="vm-chart-wrap"><svg class="vm-chart" viewBox="0 0 '+W+' '+H+'"><path class="grid" d="'+[0,1,2,3].map(function(g){return "M55 "+(T+Math.round(S*g/3))+"H"+(W-45);}).join("")+'"/><path class="inside" d="'+path("indoorTemperatureAvg",t)+'"/><path class="perceived" d="'+path("perceivedTemperature",t)+'"/><path class="humidity" d="'+path("relativeHumidity",h)+'"/><path class="humidity humidity--2" d="'+path("relativeHumidity02",h)+'"/>'+[0,1,2,3].map(function(g){var y=T+Math.round(S*g/3)+4;return '<text class="yl" x="48" y="'+y+'">'+esc((t[1]-(t[1]-t[0])*g/3).toFixed(1))+'°C</text><text class="yr" x="'+(W-40)+'" y="'+y+'">'+esc(Math.round(h[1]-(h[1]-h[0])*g/3))+'%</text>';}).join("")+[0,1,2,3,4].map(function(k){var i=Math.round((r.length-1)*k/4),x=55+i*(W-100)/Math.max(1,r.length-1);return '<text class="xl" x="'+x.toFixed(1)+'" y="'+(H-9)+'">'+esc(r[i]&&r[i].ts?new Date(r[i].ts).toLocaleTimeString("vi-VN",{hour:"2-digit",minute:"2-digit"}):"--")+'</text>';}).join("")+'</svg></div></section><section class="vm-panel vm-history__table"><div class="vm-panel__head"><div><h2>Bảng số liệu</h2><p>Nước là bộ đếm tổng tích lũy; không suy ra lượng theo ngày/lứa.</p></div></div><div class="vm-table-wrap"><table><thead><tr><th>Thời gian</th>'+readings.map(function(k){return '<th>'+esc(k[1])+'</th>';}).join("")+'<th>Chất lượng</th></tr></thead><tbody>'+rows(readings.map(function(k){return [k[0],k[2]];}))+'</tbody></table></div></section></section>';}
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
