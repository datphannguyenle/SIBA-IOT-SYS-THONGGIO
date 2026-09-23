"""VENT-011 — bộ sinh dữ liệu MÔ PHỎNG cho hệ thông gió. Không gọi ThingsBoard.

Sinh telemetry theo đúng khóa semantic của Data Contract v0.3. Số liệu ở đây là SỐ MÔ PHỎNG
phục vụ kiểm giao diện và đường dữ liệu; KHÔNG phải số của nhà cung cấp và không được dùng làm
cơ sở cấu hình thật. Mọi thiết bị mang tiền tố SIM- để không lẫn với thiết bị thật.

Bảy kịch bản, theo đúng lối đã dùng cho hệ khử mùi (SIM-DEO-*):

  NORMAL    chạy AUTO, dữ liệu đầy đủ và tươi
  BOUNDARY  cấp 0, số 0 THẬT (đàn 0, lưu lượng 0) — kiểm việc 0 không bị nhầm thành "chưa có"
  MANUAL    chế độ tay, quạt VFD vô cấp
  FAULT     lỗi thiết bị tổng + cảnh báo nhiệt độ cao
  STALE     payload đầy đủ nhưng timestamp cũ hơn ngưỡng tươi
  UNKNOWN   chỉ gửi vài khóa; phần còn lại KHÔNG gửi (phải ra "--", không được ra 0)
  OFFLINE   không gửi gì; TB tự đánh thiết bị là inactive
"""
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTRACT_JS = ROOT / "widgets/ventilation-contract-v03.js"

SIM_PROFILE = "SIM-VentController"
SIM_PREFIX = "SIM-VEN-"
SCENARIOS = ("NORMAL", "BOUNDARY", "MANUAL", "FAULT", "STALE", "UNKNOWN", "OFFLINE")
SCENARIO_LABEL = {
    "NORMAL": "Nhà mô phỏng · chạy tự động",
    "BOUNDARY": "Nhà mô phỏng · cấp 0 và số 0 thật",
    "MANUAL": "Nhà mô phỏng · chế độ tay VFD",
    "FAULT": "Nhà mô phỏng · lỗi thiết bị",
    "STALE": "Nhà mô phỏng · dữ liệu cũ",
    "UNKNOWN": "Nhà mô phỏng · thiếu mapping",
    "OFFLINE": "Nhà mô phỏng · mất kết nối",
}
# Kịch bản UNKNOWN chỉ gửi đúng mấy khóa này; thiếu các khóa còn lại là CỐ Ý.
UNKNOWN_KEYS = ("indoorTemperature01", "indoorTemperature02", "indoorTemperatureAvg")
STALE_AGE_MS = 3 * 60 * 60 * 1000
FAN_COUNT, PUMP_COUNT, STAGE_COUNT, SLOT_COUNT = 6, 2, 9, 10


def contract():
    text = CONTRACT_JS.read_text(encoding="utf-8")
    match = re.search(r"root\.VentilationContract = (\{.*\});", text, re.S)
    if not match:
        raise RuntimeError("Không đọc được contract v0.3 từ %s" % CONTRACT_JS)
    data = json.loads(match.group(1))
    if data.get("version") != "0.3":
        raise RuntimeError("Cần contract v0.3, gặp %s" % data.get("version"))
    return data


def variables(role):
    return [row[0] for row in contract()["variables"] if row[2] == role]


def _round(value, digits=1):
    return round(value + 0.0, digits)


# --- Cài đặt: hằng số cấu hình của bộ điều khiển, ghi một lần ------------------------------

def _profile_ladder():
    """Thang profile theo ngày tuổi: tuổi tăng dần, nhiệt độ đặt giảm dần, low < đặt < high."""
    rows = []
    for slot in range(1, SLOT_COUNT + 1):
        age = (slot - 1) * 7
        setpoint = 32.0 - (slot - 1) * 1.0
        rows.append((slot, age, _round(setpoint), _round(setpoint - 3.0), _round(setpoint + 3.0)))
    return rows


def settings_payload(scenario):
    """Giá trị cài đặt mô phỏng, nhất quán với nhau (xem test_vent011_simulation)."""
    if scenario == "OFFLINE":
        return {}
    values = {}
    manual = scenario == "MANUAL"
    values["settingControlBasis"] = 0                 # 0 = nhiệt độ thực
    values["settingDehumidificationEnabled"] = 1 if scenario == "NORMAL" else 0
    values["settingFanControlMode"] = 1 if manual else 0   # 1 = VFD vô cấp
    values["barnLength"] = 90.0
    values["barnWidth"] = 15.0
    values["barnHeight"] = 3.2
    values["fanRatedAirflow"] = 36000.0
    values["settingPigCount"] = 0 if scenario == "BOUNDARY" else 1200
    values["settingPigDeathCount"] = 0 if scenario == "BOUNDARY" else 4
    values["settingPigAgeDay"] = 0 if scenario == "BOUNDARY" else 36
    values["humiditySetpoint"] = 65.0
    values["humidityLowThreshold"] = 45.0
    values["coolingTemperatureOffset"] = 1.5
    values["heatingTemperatureOffset"] = 2.0

    for slot, age, setpoint, low, high in _profile_ladder():
        tag = "%02d" % slot
        values["temperatureProfile%sAgeDay" % tag] = age
        values["temperatureProfile%sSetpoint" % tag] = setpoint
        values["temperatureProfile%sLowAlarm" % tag] = low
        values["temperatureProfile%sHighAlarm" % tag] = high
        values["perceivedProfile%sAgeDay" % tag] = age
        values["perceivedProfile%sSetpoint" % tag] = _round(setpoint - 1.0)
        values["perceivedProfile%sLowAlarm" % tag] = _round(low - 1.0)
        values["perceivedProfile%sHighAlarm" % tag] = _round(high - 1.0)

    for stage in range(1, STAGE_COUNT + 1):
        tag = "%02d" % stage
        values["stage%sTemperatureOffset" % tag] = _round(stage * 0.5)
        values["stage%sPerceivedTemperatureOffset" % tag] = _round(stage * 0.4)
        for fan in range(1, FAN_COUNT + 1):
            values["stage%sFan%02dEnabled" % (tag, fan)] = 1 if fan <= fans_for_stage(stage) else 0
        for channel in range(1, 3):
            values["stage%sFan%02dFrequency" % (tag, channel)] = _round(30.0 + stage * 2.0)
        values["stage%sRoofInletPositionSetpoint" % tag] = _round(min(100.0, stage * 11.0))
        values["stage%sSideInletPositionSetpoint" % tag] = _round(min(100.0, stage * 9.0))

    values["stageSampleDelay"] = 120
    values["fanOffDelay"] = 60
    for fan in range(1, FAN_COUNT + 1):
        values["fan%02dCycleOnTime" % fan] = 180
        values["fan%02dCycleOffTime" % fan] = 300
    for pump in range(1, PUMP_COUNT + 1):
        values["coolingPump%02dCycleOnTime" % pump] = 60
        values["coolingPump%02dCycleOffTime" % pump] = 600
    values["indoorTemperature01Calibration"] = 0.0
    values["indoorTemperature02Calibration"] = -0.2
    values["outdoorTemperatureCalibration"] = 0.0
    values["relativeHumidityCalibration"] = 0.0

    if scenario == "UNKNOWN":
        return {}
    return values


def fans_for_stage(stage):
    """Cấp càng cao càng nhiều quạt; đơn điệu không giảm."""
    if stage <= 0:
        return 0
    return min(FAN_COUNT, int(math.ceil(stage * FAN_COUNT / float(STAGE_COUNT))))


# --- Giám sát: thay đổi theo thời gian ------------------------------------------------------

def stage_for(scenario, tick):
    if scenario == "BOUNDARY":
        return 0
    if scenario == "FAULT":
        return STAGE_COUNT
    if scenario == "MANUAL":
        return 3
    return 3 + (tick % 3)


def monitoring_payload(scenario, tick):
    """Khóa giám sát cho một lần lấy mẫu. Trả {} nếu kịch bản không gửi gì."""
    if scenario == "OFFLINE":
        return {}
    cfg = settings_payload(scenario) or settings_payload("NORMAL")
    stage = stage_for(scenario, tick)
    running = fans_for_stage(stage)
    wave = math.sin(tick / 6.0)

    age_day = 0 if scenario == "BOUNDARY" else 36 + tick // 288
    setpoint, low_alarm, high_alarm = setpoints_for_age(cfg, age_day)

    if scenario == "BOUNDARY":
        t01 = t02 = high_alarm                     # đúng ngưỡng, không vượt
    elif scenario == "FAULT":
        t01, t02 = _round(high_alarm + 1.8), _round(high_alarm + 2.1)
    else:
        t01 = _round(setpoint + 0.6 + wave * 0.5)
        t02 = _round(setpoint + 0.2 + wave * 0.4)
    t_avg = _round((t01 + t02) / 2.0)
    outdoor = _round(29.0 + wave * 2.5)
    air_speed = 0.0 if stage == 0 else _round(0.35 * running, 2)
    perceived = _round(t_avg - air_speed * 1.2)
    air_flow = _round(cfg["fanRatedAirflow"] * running, 1)

    values = {
        "indoorTemperature01": t01,
        "indoorTemperature02": t02,
        "indoorTemperatureAvg": t_avg,
        "outdoorTemperature": outdoor,
        "perceivedTemperature": perceived,
        "temperatureSetpointCurrent": setpoint,
        "perceivedTemperatureSetpointCurrent": _round(setpoint - 1.0),
        "relativeHumidity": _round(62.0 + wave * 4.0),
        "humiditySetpointCurrent": cfg["humiditySetpoint"],
        "airSpeed": air_speed,
        "airFlow": air_flow,
        # Nước chỉ tăng; cấp 0 vẫn có tổng tích lũy nhưng lưu lượng tức thời là 0 THẬT.
        "waterConsumptionTotal": _round(18450.0 + tick * 7.5),
        "waterFlow": 0.0 if stage == 0 else _round(12.0 + wave, 2),
        "pigCount": cfg["settingPigCount"],
        "pigDeathCount": cfg["settingPigDeathCount"],
        "pigAgeDay": age_day,
        "operatingMode": 0 if scenario == "MANUAL" else 1,
        "controlBasis": cfg["settingControlBasis"],
        "dehumidificationEnabled": cfg["settingDehumidificationEnabled"],
        "fanControlMode": cfg["settingFanControlMode"],
        "fanStage": stage,
        "roofInletPosition": _round(min(100.0, stage * 11.0)),
        "sideInletPosition": _round(min(100.0, stage * 9.0)),
        "equipmentFaultActive": 1 if scenario == "FAULT" else 0,
        "externalHighTemperatureAlarm": 1 if scenario == "FAULT" else 0,
        "temperatureLowAlarmActive": 1 if t_avg < low_alarm else 0,
        "temperatureHighAlarmActive": 1 if t_avg > high_alarm else 0,
        "perceivedTemperatureLowAlarmActive": 1 if perceived < low_alarm - 1.0 else 0,
        "perceivedTemperatureHighAlarmActive": 1 if perceived > high_alarm - 1.0 else 0,
    }
    for fan in range(1, FAN_COUNT + 1):
        values["fan%02dRun" % fan] = 1 if fan <= running else 0
    for pump in range(1, PUMP_COUNT + 1):
        values["coolingPump%02dRun" % pump] = 1 if stage >= 7 and pump == 1 else 0
    for channel in range(1, 3):
        frequency = cfg["stage%02dFan%02dFrequency" % (max(stage, 1), channel)]
        values["fan%02dSpeedSetpoint" % channel] = _round(min(100.0, frequency * 2.0))
        values["fan%02dSpeedFeedback" % channel] = 0.0 if stage == 0 else _round(frequency - 0.3)

    if scenario == "UNKNOWN":
        return {key: values[key] for key in UNKNOWN_KEYS}
    return values


def setpoints_for_age(cfg, age_day):
    """Slot có ngày tuổi lớn nhất mà <= ngày tuổi hiện tại; dưới slot đầu thì dùng slot 01."""
    chosen = 1
    for slot in range(1, SLOT_COUNT + 1):
        if cfg["temperatureProfile%02dAgeDay" % slot] <= age_day:
            chosen = slot
    tag = "%02d" % chosen
    return (cfg["temperatureProfile%sSetpoint" % tag], cfg["temperatureProfile%sLowAlarm" % tag],
            cfg["temperatureProfile%sHighAlarm" % tag])


def timestamp_for(scenario, now_ms, tick, period_ms):
    """STALE cố tình lùi mốc thời gian ra ngoài ngưỡng tươi."""
    base = now_ms - (tick * period_ms)
    return base - STALE_AGE_MS if scenario == "STALE" else base


def sample(scenario, now_ms, tick=0, period_ms=60000, include_settings=False):
    """Một bản tin telemetry TB: {"ts": ..., "values": {...}}; None nếu không có gì để gửi."""
    values = monitoring_payload(scenario, tick)
    if include_settings:
        values = dict(settings_payload(scenario), **values)
    if not values:
        return None
    return {"ts": timestamp_for(scenario, now_ms, tick, period_ms), "values": values}


def history(scenario, now_ms, points=180, period_ms=60000):
    """Chuỗi lịch sử từ cũ đến mới, để màn Lịch sử có đường thật thay vì một điểm."""
    batch = []
    for tick in range(points - 1, -1, -1):
        item = sample(scenario, now_ms, tick, period_ms)
        if item:
            batch.append(item)
    return batch
