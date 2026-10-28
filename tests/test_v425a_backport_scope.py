"""v4.25a isolates only the original v4.10 diagnostics over v4.9."""
import ast
import hashlib
import unittest
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
def blob(path):
    a=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(a)).encode()+b"\x00"+a).hexdigest()
class TestScope(unittest.TestCase):
    def test_verbatim_known_good_and_only_one_backport(self):
        src=(ROOT/"components/_bootstrap_v4.py").read_text()
        tree=ast.parse(src)
        var=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="_PATCHES" for t in n.targets))
        self.assertEqual(ast.literal_eval(var),tuple(x for x,_ in BASE)+("0009-v4_25a-v410-deferred-diagnostics.patch",))
        for name,hash in BASE:
            with self.subTest(name=name): self.assertEqual(blob(ROOT/"patches"/name),hash)
        self.assertEqual(blob(ROOT/"patches"/"0009-v4_25a-v410-deferred-diagnostics.patch"),"4fbfb8ab77783e9c6e5103d76fd73c4c24b141fb")
        self.assertEqual(len(list((ROOT/"patches").glob("*.patch"))),9)
    def test_no_radio_hotpath_changes(self):
        s=(ROOT/"patches"/"0009-v4_25a-v410-deferred-diagnostics.patch").read_text()
        self.assertNotIn("diff --git a/components/wmbus_radio/transceiver_cc1101.cpp",s)
        self.assertNotIn("diff --git a/components/wmbus_radio/cc1101_fifo.h",s)
        for forbidden in ("delayMicroseconds(","MARCSTATE","CC1101_FIFOTHR","wakeup_receiver_task_from_isr","ulTaskNotifyTake","make_unique<Packet>","read_in_task("):
            with self.subTest(forbidden=forbidden):self.assertNotIn(forbidden,s)
        self.assertIn("RX_DIAG_5M",s)
        self.assertIn("frame_conversion_failed_",s)
    def test_ci_pins_same_toolchain(self):
        for x in ("test.yml","official-v4.yml","direct-esphome-install.yml"):
            self.assertIn("esphome==2026.10.1",(ROOT/".github/workflows"/x).read_text())
if __name__=="__main__":unittest.main()
