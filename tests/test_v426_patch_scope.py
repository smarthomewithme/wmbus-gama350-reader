"""v4.26 only modifies bounded RX FIFO read logic on exact v4.9."""
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
def blob(f):
  b=f.read_bytes()
  return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
class TestV426(unittest.TestCase):
  def test_unchanged_eight_patch_baseline(self):
    py=(ROOT/"components/_bootstrap_v4.py").read_text()
    mod=ast.parse(py)
    node=next(x.value for x in mod.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="_PATCHES" for t in x.targets))
    self.assertEqual(ast.literal_eval(node),tuple(x for x,_ in BASE)+("0009-v426-rxbytes65-prefetch-only.patch",))
    for p,h in BASE:
      with self.subTest(path=p): self.assertEqual(blob(ROOT/"patches"/p),h)
    self.assertEqual(len(list((ROOT/"patches").glob("*.patch"))),9)
  def test_only_fifo_driver_and_helper(self):
    s=(ROOT/"patches"/"0009-v426-rxbytes65-prefetch-only.patch").read_text()
    files=[x.removeprefix("diff --git a/").split(" b/")[0] for x in s.splitlines() if x.startswith("diff --git a/")]
    self.assertEqual(files,["components/wmbus_radio/cc1101_fifo.h","components/wmbus_radio/transceiver_cc1101.cpp"])
    for word in ("component.cpp","component.h","rx_diag_window","wakeup_receiver_task_from_isr","delayMicroseconds","CC1101_FIFOTHR","CC1101_MDMCFG4","MARCSTATE","restart_rx","write_register"):
      with self.subTest(word=word): self.assertNotIn(word,s)
    for word in ("kCc1101MaxReportedRxBytes = 65","rx_fifo_incomplete_read(available, remaining)","rx_fifo_complete_read(confirmed & 0x7F, remaining)"):
      self.assertIn(word,s)
  def test_ci_2026101(self):
    for name in ("test.yml","official-v4.yml","direct-esphome-install.yml"):
      self.assertIn("esphome==2026.10.1",(ROOT/".github/workflows"/name).read_text())
if __name__=="__main__": unittest.main()
