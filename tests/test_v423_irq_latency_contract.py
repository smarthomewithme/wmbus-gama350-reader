"""v4.23: IRQ timing with no SPI / high-priority logging modifications."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"patches/0016-v4_23-irq-latency-deferred-diagnostics.patch"
class TestIrqLatency(unittest.TestCase):
    def test_scope(self):
        s=P.read_text()
        paths=[x.removeprefix("diff --git a/").split(" b/")[0] for x in s.splitlines() if x.startswith("diff --git a/")]
        self.assertEqual(paths,["components/wmbus_radio/component.cpp"])
        self.assertIn("shwm_last_irq_us.store((uint32_t) esp_timer_get_time()",s)
        self.assertIn("shwm_irq_latency_max_us.compare_exchange_weak",s)
        self.assertIn('SHWM v4.23 IRQ_LATENCY',s)
        self.assertIn("if (notifications > 1u)",s)
        adds="\n".join(x for x in s.splitlines() if x.startswith("+") and not x.startswith("+++"))
        for token in ("read_status_register(","read_register(","write_register(","restart_rx(",
                      "read_burst(","delayMicroseconds(","ESP_LOGW(","CC1101_FIFOTHR",
                      "CC1101_IOCFG0","ulTaskNotifyTake(","vTaskNotifyGiveFromISR("):
            self.assertNotIn(token,adds)
        self.assertEqual(s.count('diff --git a/'),1)
    def test_no_rejected_patch(self):
        bootstrap=(ROOT/"components/_bootstrap_v4.py").read_text()
        self.assertIn("shwm-wmbus-v4.23-irq-latency-v1",bootstrap)
        self.assertNotIn('0016-v4_22-cc1101-failure-only-snapshots.patch',bootstrap)
        self.assertNotIn('0016-v4_20-post-progress-coalesce-75us.patch',bootstrap)
if __name__=="__main__":
    unittest.main()
