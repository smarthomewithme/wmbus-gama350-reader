"""Unit tests for offline v4.27 diagnostics: no radio code or network calls."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"analyze_v427.py"
spec=importlib.util.spec_from_file_location("shwm_diag",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestPassiveV427(unittest.TestCase):
    def test_one_missing_slot_corrupt_and_water(self):
        log="""[18:00:00.000][D][CC1101:398][radio_recv]: RF_DIAG bytes=326 freqest_raw=19 lqi_raw=128 marcstate=0x0D
[18:00:00.010][D][CC1101:401][radio_recv]: Long RX: bytes=326 bursts=32 peak_fifo=39 ms=25 rssi=-71 unstable_rxbytes=0
[18:00:00.030][I][main:687]: Telegram otrzymany od licznika prądu!
[18:00:10.000][I][main:657]: Telegram otrzymany od licznika wody!
[18:01:00.000][D][CC1101:398][radio_recv]: RF_DIAG bytes=326 freqest_raw=23 lqi_raw=232 marcstate=0x0D
[18:01:00.010][D][CC1101:401][radio_recv]: Long RX: bytes=326 bursts=29 peak_fifo=40 ms=25 rssi=-72 unstable_rxbytes=0
[18:01:00.020][W][3of6:044]: Long frame 3of6 error: encoded_byte=3/326 symbol=5
[18:01:00.030][I][wmbus:048]: RX_DIAG cumulative irq_notifications=5 header_ok=5 header_fail=0 payload_ok=5 payload_fail=0 long_radio_frames=2 queue_drops=0
[18:01:00.500][I][main:657]: Telegram otrzymany od licznika wody!
[18:01:00.600][W][CC1101:389][radio_recv]: RX timeout after 0 bytes (need 3)
[18:01:10.000][D][wifi:2598]: Roam scan (-55 dBm, attempt 1/3)
"""
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"raw.log";p.write_text(log)
            rows=mod.parse_logs([p,p])
            s,slots,errs=mod.analyze(rows)
            self.assertEqual((s["long_frames_326"],s["gama_decoded"],s["gama_3of6_errors"]),(2,1,1))
            self.assertEqual(s["water_telegrams"],2)
            self.assertEqual(s["nominal_slots"],3)
            self.assertEqual([x["status"] for x in slots],
                             ["decoded","NO_FULL_FRAME_OBSERVED","3of6_error"])
            self.assertEqual(s["nominal_slots_without_full_frame"],1)
            self.assertEqual((errs[0]["encoded_byte"],errs[0]["symbol"],errs[0]["lqi_raw"]),(3,5,232))
            self.assertEqual(s["header_zero_byte_timeouts"],1)
            self.assertEqual(s["last_irq_cumulative"]["queue_drops"],0)
            mod.write_reports(Path(t)/"out",s,slots,errs)
            self.assertTrue((Path(t)/"out"/"report.md").is_file())
            self.assertTrue((Path(t)/"out"/"errors_3of6.csv").is_file())
            self.assertNotIn("secret", (Path(t)/"out"/"report.md").read_text())
    def test_no_firmware_events(self):
        with self.assertRaises(ValueError):
            mod.analyze([])
        s,slots,errors=mod.analyze([(0,"[main] unrelated"),(61000,"[main] unrelated")])
        self.assertEqual(s["long_frames_326"],0)
        self.assertEqual(s["nominal_slots"],0)
        self.assertEqual(errors,[])
    def test_multiple_log_dedup_distinct_same_millisecond(self):
        with tempfile.TemporaryDirectory() as t:
            a=Path(t)/"a.txt";a.write_text("[11:00:00.000] foo\n[11:00:00.000] bar\n")
            self.assertEqual(len(mod.parse_logs([a,a])),2)
    def test_nominal_gap_is_not_claimed_lost_rf(self):
        s,slots,err=mod.analyze([
            (0,"[radio_recv]: Long RX: bytes=326 bursts=31 peak_fifo=40 ms=25 rssi=-70 unstable_rxbytes=0"),
            (20,"Telegram otrzymany od licznika prądu!"),
            (60000,"[radio_recv]: Long RX: bytes=326 bursts=31 peak_fifo=40 ms=25 rssi=-70 unstable_rxbytes=0"),
            (60020,"Telegram otrzymany od licznika prądu!")])
        self.assertEqual(s["nominal_slots_without_full_frame"],1)
        self.assertEqual(slots[1]["status"],"NO_FULL_FRAME_OBSERVED")
if __name__=="__main__":unittest.main()
