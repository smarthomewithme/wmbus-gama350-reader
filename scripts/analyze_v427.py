#!/usr/bin/env python3
"""v4.27 passive evidence collector for unchanged v4.9 ESPHome CC1101 logs.

No firmware hooks, SPI transactions, IRQ code, AES keys, or raw telegrams.
Only classifies actually logged frames and inferred 30 s silent windows.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
import statistics
from datetime import datetime, timedelta
from pathlib import Path

CLOCK = re.compile(r"\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]")
LONG = re.compile(r"Long RX: bytes=(\d+)\s+bursts=(\d+)\s+peak_fifo=(\d+)\s+ms=(\d+)\s+rssi=(-?\d+)\s+unstable_rxbytes=(\d+)")
RF = re.compile(r"RF_DIAG bytes=(\d+)\s+freqest_raw=(-?\d+)\s+lqi_raw=(\d+)\s+marcstate=(0x[0-9A-Fa-f]+)")
DECODE_ERROR = re.compile(r"Long frame 3of6 error:\s*encoded_byte=(\d+)/(\d+)\s+symbol=(\d+)")
IRQ = re.compile(r"RX_DIAG cumulative\s+irq_notifications=(\d+)\s+header_ok=(\d+)\s+header_fail=(\d+)\s+payload_ok=(\d+)\s+payload_fail=(\d+)\s+long_radio_frames=(\d+)\s+queue_drops=(\d+)")
WARN = ("RX FIFO overflow", "Invalid RX FIFO count: 65", "RX timeout after 0 bytes", "esphome.coroutine took a long time")
OUTPUT_KEYS = ("time","status","rssi_dbm","lqi_raw","freqest_raw","bursts","peak_fifo","rx_ms","unstable_rxbytes","encoded_byte","symbol","water_near_250ms","header_timeout_near_500ms")

def rounded_median(values):
    return round(statistics.median(values), 3) if values else None

def parse_logs(paths):
    # Re-exported log windows often repeat all previous lines. Deduplicate them
    # by clock+body, not by timestamp alone (multiple events share one millisecond).
    seen = set()
    ordered = []
    for path in paths:
        for raw in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
            m = CLOCK.search(raw)
            if not m:
                continue
            sec = ((int(m[1])*60+int(m[2]))*60+int(m[3]))*1000+int(m[4])
            body = raw[m.end():].strip()
            key = (sec, body)
            if key not in seen:
                seen.add(key)
                ordered.append((sec, body))
    ordered.sort(key=lambda x: x[0])
    # Normal use is a same-day log. A day rollover in concatenated files can be
    # ambiguous; refuse silently wrong timing rather than invent elapsed days.
    if ordered and ordered[-1][0]-ordered[0][0] > 20*3600*1000:
        raise ValueError("Log may cross midnight: split analysis into day-scoped files.")
    return ordered

def clock_str(ms):
    ms %= 86400000
    return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms%1000:03d}"

def nearest_distance(ms, points):
    return min((abs(ms-x) for x in points), default=None)

def analyze(rows, period_s=30.0, tolerance_ms=2000):
    if not rows:
        raise ValueError("No ESPHome [HH:MM:SS.mmm] log lines found.")
    period_ms = round(period_s*1000)
    if not 5000 <= period_ms <= 300000:
        raise ValueError("Period must be between 5s and 300s.")
    frames = []
    water = []
    warnings = {w:[] for w in WARN}
    irqs = []
    last_rf = None
    for ms, body in rows:
        r = RF.search(body)
        if r:
            last_rf = dict(time_ms=ms, bytes=int(r[1]), freqest_raw=int(r[2]),
                           lqi_raw=int(r[3]), marcstate=r[4])
        m = LONG.search(body)
        if m and int(m[1]) == 326:
            frame = dict(time_ms=ms,status="full_not_decoded",rssi_dbm=int(m[5]),
                         lqi_raw=None,freqest_raw=None,marcstate=None,bursts=int(m[2]),
                         peak_fifo=int(m[3]),rx_ms=int(m[4]),unstable_rxbytes=int(m[6]),
                         encoded_byte=None,symbol=None)
            if last_rf is not None and ms-last_rf["time_ms"] <= 500 and last_rf["bytes"]==326:
                frame.update({k:last_rf[k] for k in ("freqest_raw","lqi_raw","marcstate")})
            frames.append(frame)
        if "Telegram otrzymany od licznika wody!" in body:
            water.append(ms)
        if "Telegram otrzymany od licznika prądu!" in body:
            for f in reversed(frames):
                if 0 <= ms-f["time_ms"] <= 1500 and f["status"]=="full_not_decoded":
                    f["status"]="decoded"
                    break
        er = DECODE_ERROR.search(body)
        if er:
            for f in reversed(frames):
                if 0 <= ms-f["time_ms"] <= 1500 and f["status"]=="full_not_decoded":
                    f.update(status="3of6_error",encoded_byte=int(er[1]),symbol=int(er[3]))
                    break
        q = IRQ.search(body)
        if q:
            irqs.append(dict(zip(("irq_notifications","header_ok","header_fail",
                                  "payload_ok","payload_fail","long_radio_frames","queue_drops"),
                                 (int(q[i]) for i in range(1,8))),time=clock_str(ms)))
        for w in WARN:
            if w in body:
                warnings[w].append(ms)
    for f in frames:
        near_water = nearest_distance(f["time_ms"],water)
        near_header = nearest_distance(f["time_ms"],warnings["RX timeout after 0 bytes"])
        f["water_near_250ms"]=near_water is not None and near_water <= 250
        f["header_timeout_near_500ms"]=near_header is not None and near_header <= 500

    slots = []
    if frames:
        anchor = frames[0]["time_ms"]
        last = rows[-1][0]
        count = max(0,(last-anchor)//period_ms+1)
        if count > 50000:
            raise ValueError("Too many inferred transmission slots")
        grouped = {}
        for f in frames:
            i = round((f["time_ms"]-anchor)/period_ms)
            if i >= 0 and abs(f["time_ms"]-(anchor+i*period_ms)) <= tolerance_ms:
                grouped.setdefault(i,[]).append(f)
        for i in range(count):
            middle = anchor+i*period_ms
            group = grouped.get(i,[])
            if group:
                status=("decoded" if any(f["status"]=="decoded" for f in group)
                        else "3of6_error" if any(f["status"]=="3of6_error" for f in group)
                        else "full_not_decoded")
            else:
                status = "NO_FULL_FRAME_OBSERVED"
            near_water = nearest_distance(middle,water)
            near_header = nearest_distance(middle,warnings["RX timeout after 0 bytes"])
            slots.append(dict(time=clock_str(middle),status=status,
                              full_frames=len(group),
                              water_near_250ms=near_water is not None and near_water<=250,
                              header_timeout_near_500ms=near_header is not None and near_header<=500))
    errors = [{k:(clock_str(f["time_ms"]) if k=="time" else f.get(k))
               for k in OUTPUT_KEYS} for f in frames if f["status"]=="3of6_error"]
    intervals = [b-a for a,b in zip(water,water[1:])]
    slow_water = None
    for i in range(3,len(intervals)):
        if all(45000 <= x <= 90000 for x in intervals[i-3:i+1]):
            slow_water = clock_str(water[i-2])
            break
    stats = dict(
        log_start=clock_str(rows[0][0]),log_end=clock_str(rows[-1][0]),
        duration_s=round((rows[-1][0]-rows[0][0])/1000,3),
        long_frames_326=len(frames),
        gama_decoded=sum(f["status"]=="decoded" for f in frames),
        gama_3of6_errors=len(errors),
        gama_full_other=sum(f["status"]=="full_not_decoded" for f in frames),
        full_frame_decode_pct=round(100*sum(f["status"]=="decoded" for f in frames)/len(frames),2) if frames else None,
        water_telegrams=len(water),water_median_gap_s=round(rounded_median(intervals)/1000,2) if intervals else None,
        water_slow_cadence_candidate_at=slow_water,
        rx_fifo_overflows=len(warnings["RX FIFO overflow"]),
        rxbytes65_warnings=len(warnings["Invalid RX FIFO count: 65"]),
        header_zero_byte_timeouts=len(warnings["RX timeout after 0 bytes"]),
        irq_snapshot_count=len(irqs),last_irq_cumulative=irqs[-1] if irqs else None,
        fifo_burst_mean=round(statistics.mean(f["bursts"] for f in frames),2) if frames else None,
        frame_rssi_mean=round(statistics.mean(f["rssi_dbm"] for f in frames),2) if frames else None,
        nominal_period_s=period_s,
        nominal_slots=len(slots),
        nominal_slots_without_full_frame=sum(s["status"]=="NO_FULL_FRAME_OBSERVED" for s in slots),
        nominal_slots_with_3of6=sum(s["status"]=="3of6_error" for s in slots),
        nominal_slots_decoded=sum(s["status"]=="decoded" for s in slots))
    return stats,slots,errors

def dump_csv(path,fields,rows):
    with path.open("w",newline="",encoding="utf-8") as out:
        w=csv.DictWriter(out,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def write_reports(output,stats,slots,errors):
    output.mkdir(parents=True,exist_ok=True)
    (output/"summary.json").write_text(json.dumps(stats,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    dump_csv(output/"gama_slots.csv",
             ("time","status","full_frames","water_near_250ms","header_timeout_near_500ms"),slots)
    dump_csv(output/"errors_3of6.csv",OUTPUT_KEYS,errors)
    line=[
        "# v4.27 passive diagnostic report (v4.9 receiver unchanged)",
        f"Window: {stats['log_start']}–{stats['log_end']} ({stats['duration_s']}s)",
        f"Full GAMA 326B radio frames: **{stats['long_frames_326']}**; decoded: **{stats['gama_decoded']}**; 3of6 errors: **{stats['gama_3of6_errors']}**.",
        f"Decoded FULL frames: {stats['full_frame_decode_pct']}% (NOT percentage of actual transmissions).",
        f"Apator decoded: {stats['water_telegrams']}; median interval: {stats['water_median_gap_s']}s.",
        f"Nominal {stats['nominal_period_s']}s slots: **{stats['nominal_slots']}**, decoded {stats['nominal_slots_decoded']}, 3of6 {stats['nominal_slots_with_3of6']}, **NO FULL FRAME OBSERVED {stats['nominal_slots_without_full_frame']}**.",
        f"Actual FIFO overflow: {stats['rx_fifo_overflows']}; RXBYTES65 warnings: {stats['rxbytes65_warnings']}; header 0-byte timeout: {stats['header_zero_byte_timeouts']}.",
        "",
        "## Interpret with care",
        "- NO FULL FRAME OBSERVED means *we lack a logged complete frame*, not evidence the transmitter sent and receiver lost it.",
        "- A GAMA transmission could be absent, corrupted before FIFO synchronization, collide, or be missing in this log window.",
        "- The 3of6 position/symbol and preceding RF_DIAG raw fields are correlations, not proof of RF origin.",
        "- RF_DIAG lqi_raw is the uncalibrated/raw diagnostic, not a guaranteed signal quality percentage.",
        "- Radio IRQ counters aggregate all meters. A missing expected GAMA slot cannot be inferred from total IRQ delta alone.",
        "- This analysis does NOT store telegram contents, meter IDs, AES keys, IP addresses, sensor readings or SSIDs.",
        "- Multiple overlapping exports are de-duplicated by clock and line content. Split logs by day at midnight.",
        "",
        "## 3of6 bad symbol events",
        *([f"- {e['time']}: byte {e['encoded_byte']}, symbol {e['symbol']}, RSSI {e['rssi_dbm']}, LQI(raw) {e['lqi_raw']}, FREQEST(raw) {e['freqest_raw']}"
          for e in errors] or ["- None logged"]),
        "",
        "## Unobserved nominal GAMA slots",
        *([f"- {s['time']}: water_near_250ms={s['water_near_250ms']}, header_timeout_near_500ms={s['header_timeout_near_500ms']}"
          for s in slots if s['status']=="NO_FULL_FRAME_OBSERVED"] or ["- None inferred"]),
        "",
    ]
    (output/"report.md").write_text("\n".join(line),encoding="utf-8")

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",action="append",required=True,help="ESPHome exported .txt or .md; repeat for overlapping logs")
    p.add_argument("--out",required=True,help="Directory for JSON, Markdown and CSV analysis (no raw radio data)")
    p.add_argument("--period",type=float,default=30.0,help="Expected GAMA interval in seconds, assumption (default 30)")
    p.add_argument("--tolerance-ms",type=int,default=2000)
    args=p.parse_args(argv)
    stats,slots,errors=analyze(parse_logs(args.input),args.period,args.tolerance_ms)
    write_reports(Path(args.out),stats,slots,errors)
    print(json.dumps(stats,indent=2,ensure_ascii=False))
    print("Reports:",Path(args.out).resolve())
if __name__=="__main__":
    main()
