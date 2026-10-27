#include "loop_gap_observer.h"
#include <cstdint>
#include <limits>

using esphome::wmbus_radio::estimate_missing_30s_periods;

static_assert(estimate_missing_30s_periods(0u) == 0u);
static_assert(estimate_missing_30s_periods(30000u) == 0u);
static_assert(estimate_missing_30s_periods(44999u) == 0u);
static_assert(estimate_missing_30s_periods(45000u) == 1u);
static_assert(estimate_missing_30s_periods(74999u) == 1u);
static_assert(estimate_missing_30s_periods(75000u) == 2u);
static_assert(estimate_missing_30s_periods(90000u) == 2u);
static_assert(estimate_missing_30s_periods(180000u) == 5u);
static_assert(estimate_missing_30s_periods(239998u) == 7u);
static_assert(estimate_missing_30s_periods(std::numeric_limits<uint32_t>::max()) > 1u);

int main() { return 0; }
