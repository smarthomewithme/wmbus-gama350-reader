"""Hard guard: v4.25 is only two backports on byte-exact v4.9."""
import ast,hashlib,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=[
("0001-safe-packet-decoder-and-cc1101-fifo.patch","76c8362853aa6e1c24209d5d0e1f40e498a3c561"),
("0002-cc1101-long-frame-diagnostics.patch","6e3a55fab69cf3f6850c378485c3b8baaaeda61f"),
("0003-cc1101-stable-rxbytes.patch","36f717993947e2b619642a5224063f75adef7791"),
("0004-radio-diagnostics-and-key-redaction.patch","faecc457237908d5f002355633fe52830fd1a2af"),
("0005-experimental-fifo16-threshold.patch","fb4cfbb58d4ec7601db1ad672ad90382b1f41929"),
("0006-v4_4-clear-stale-irq.patch","7c9aa74f98f6fac2b09b67d7b35133abbb70b105"),
("0007-v4_5-initialize-isr-woken.patch","8ff9fc9422df9c5d0e26474c5d3a5df981cfb0aa"),
("0008-v4_9-confirm-marcstate-eof.patch","b2c6d9f09453e75ff654a7ed53bf61d3f3661e29")]
def blob(p):
    s=p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(s)).encode()+b"\x00"+s).hexdigest()
class Guard(unittest.TestCase):
    def test_baseline_immutable(self):
        s=(ROOT/"components/_bootstrap_v4.py").read_text()
        tree=ast.parse(s)
        n=next(x.value for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="_PATCHES" for t in x.targets))
        self.assertEqual(ast.literal_eval(n),tuple(x for x,_ in BASE)+("0009-v4_25-v410-five-minute-window.patch","0010-v4_25-v414-packet-preallocation.patch"))
        for path,hash in BASE:
            with self.subTest(path=path):self.assertEqual(blob(ROOT/"patches"/path),hash)
        self.assertEqual(blob(ROOT/"patches"/"0009-v4_25-v410-five-minute-window.patch"),"4fbfb8ab77783e9c6e5103d76fd73c4c24b141fb")
        self.assertEqual(len(list((ROOT/"patches").glob("*.patch"))),10)
    def test_cc1101_driver_untouched_by_backports(self):
        data=(ROOT/"patches"/"0009-v4_25-v410-five-minute-window.patch").read_text()+(ROOT/"patches"/"0010-v4_25-v414-packet-preallocation.patch").read_text()
        for x in ("transceiver_cc1101.cpp","cc1101_fifo.h","delayMicroseconds","CC1101_FIFOTHR","MARCSTATE","wakeup_receiver_task_from_isr","vTaskNotifyGiveFromISR"):
            with self.subTest(term=x):self.assertNotIn("diff --git a/components/wmbus_radio/"+x,data)
        self.assertNotIn("delayMicroseconds",data)
        self.assertIn("RX_DIAG_5M",data)
        self.assertIn("SHWM v4.25 PREALLOC",data)
    def test_single_packet_allocation_moved(self):
        s=(ROOT/"patches"/"0010-v4_25-v414-packet-preallocation.patch").read_text()
        self.assertEqual(s.count("diff --git a/"),1)
        self.assertEqual(len([x for x in s.splitlines() if x.startswith("-") and not x.startswith("---")]),3)
        self.assertEqual(len([x for x in s.splitlines() if x.startswith("+") and not x.startswith("+++")]),3)
    def test_ci_pinned(self):
        for filename in ("test.yml","official-v4.yml","direct-esphome-install.yml"):
            self.assertIn("esphome==2026.10.1",(ROOT/".github/workflows"/filename).read_text())
if __name__=="__main__":unittest.main()
