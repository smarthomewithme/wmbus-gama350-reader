"""v4.14: one RX critical-path change, preallocate Packet before IRQ wake."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/0013-v4_14-preallocate-packet-before-irq.patch"


class TestV414PacketPreallocation(unittest.TestCase):
    def test_patch_scope_and_single_allocation(self):
        p = PATCH.read_text(encoding="utf-8")
        paths = [line.removeprefix("diff --git a/").split(" b/")[0]
                 for line in p.splitlines() if line.startswith("diff --git a/")]
        self.assertEqual(paths, ["components/wmbus_radio/component.cpp"])
        self.assertIn("SHWM wMBus v4.14 ACTIVE", p)
        self.assertIn("+  auto packet = std::make_unique<Packet>();", p)
        self.assertIn("-  auto packet = std::make_unique<Packet>();", p)
        self.assertIn("const uint32_t notifications = ulTaskNotifyTake(", p)
        self.assertIn("SHWM v4.14 packet preallocation", p)
        adds = "\n".join(line for line in p.splitlines()
                         if line.startswith("+") and not line.startswith("+++"))
        for forbidden in ("CC1101_MDMCFG4", "CC1101_FIFOTHR", "CC1101_FREQ",
                          "read_in_task(", "restart_rx(", "wakeup_receiver_task_from_isr(",
                          "decode3of6", "CC1101_MARCSTATE", "xTaskCreate",
                          "vTaskNotifyGiveFromISR"):
            self.assertNotIn(forbidden, adds)

    def test_loader_ci_and_patch_order(self):
        boot = (ROOT / "components/_bootstrap_v4.py").read_text()
        shell = (ROOT / "scripts/prepare_cc1101_v4.sh").read_text()
        for s in (boot, shell):
            self.assertLess(s.index("0012-v4_13-progress-poll.patch"), s.index(PATCH.name))
            self.assertIn("SHWM wMBus v4.14 ACTIVE", s)
        self.assertIn("shwm-wmbus-v4.20-post-progress-75us-v1", boot)
        for name in ("official-v4.yml", "direct-esphome-install.yml"):
            s = (ROOT / ".github/workflows" / name).read_text()
            self.assertIn("experiment/v4.14-prealloc-irq", s)
            self.assertIn("std::make_unique<Packet>()", s)


if __name__ == "__main__":
    unittest.main()
