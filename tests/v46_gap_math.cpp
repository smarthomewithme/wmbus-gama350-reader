#include "long_gap_diagnostics.h"

using esphome::wmbus_radio::estimate_missing_30s_periods;
static_assert(estimate_missing_30s_periods(0u) == 0u, "no frame");
static_assert(estimate_missing_30s_periods(30000u) == 0u, "normal period");
static_assert(estimate_missing_30s_periods(44999u) == 0u, "below missing boundary");
static_assert(estimate_missing_30s_periods(45000u) == 1u, "first skipped period");
static_assert(estimate_missing_30s_periods(60000u) == 1u, "one skipped period");
static_assert(estimate_missing_30s_periods(89999u) == 2u, "near third period");
static_assert(estimate_missing_30s_periods(90000u) == 2u, "two skipped periods");
static_assert(estimate_missing_30s_periods(180000u) == 5u, "five skipped periods");

int main() { return 0; }
