"""Control v4.24 MUST change exactly one text literal, no receiver logic."""
import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
PATCH=ROOT/"patches/0016-v4_24-marker-only-binary-layout-control.patch"
OLD="  ESP_LOGI(TAG, \"SHWM wMBus v4.17 ACTIVE: midpoint 100us long no-progress polling; v4.16 preserved\");"
NEW="  ESP_LOGI(TAG, \"SHWM wMBus v4.17 ACTIVE: midpoint 100us long no-progress polling; v4.16 preserved [SHWM v4.24 MARKER_ONLY]\");"
class TestMarkerOnly(unittest.TestCase):
    def test_exact_one_line_text_change(self):
        s=PATCH.read_text()
        self.assertEqual(s.count("diff --git a/"),1)
        self.assertIn("diff --git a/components/wmbus_radio/component.cpp",s)
        minuses=[x[1:] for x in s.splitlines() if x.startswith("-") and not x.startswith("---")]
        pluses=[x[1:] for x in s.splitlines() if x.startswith("+") and not x.startswith("+++")]
        self.assertEqual(minuses,[OLD])
        self.assertEqual(pluses,[NEW])
        self.assertEqual(NEW.replace(" [SHWM v4.24 MARKER_ONLY]",""),OLD)
    def test_prior_sources_unchanged(self):
        b=(ROOT/"components/_bootstrap_v4.py").read_text()
        self.assertIn("0016-v4_24-marker-only-binary-layout-control.patch",b)
        for bad in ("0016-v4_22","0016-v4_23","0016-v4_20"):
            self.assertNotIn(bad,b)
    def test_branch_has_ci(self):
        for p in ("official-v4.yml","direct-esphome-install.yml"):
            s=(ROOT/".github/workflows"/p).read_text()
            self.assertIn("experiment/v4.24-marker-only-control",s)
if __name__=="__main__":
    unittest.main()
