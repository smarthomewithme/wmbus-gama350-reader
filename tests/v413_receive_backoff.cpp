// v4.13: leave the FIFO recovery/threshold untouched, skip 200us delay after a drain.
// Synthetic policy test, not evidence of physical radio success.
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include "cc1101_fifo.h"

using esphome::wmbus_radio::rx_should_backoff_after_drain;
using esphome::wmbus_radio::rx_fifo_incomplete_read;
using esphome::wmbus_radio::rx_fifo_complete_read;

static_assert(!rx_should_backoff_after_drain(true), "progress: poll immediately");
static_assert(rx_should_backoff_after_drain(false), "no progress: retain 200us delay");
static_assert(rx_fifo_incomplete_read(0, 326) == 0);
static_assert(rx_fifo_incomplete_read(1, 326) == 0);
static_assert(rx_fifo_incomplete_read(63, 326) == 62);
static_assert(rx_fifo_incomplete_read(64, 326) == 63);
static_assert(rx_fifo_incomplete_read(65, 326) == 64);
static_assert(rx_fifo_incomplete_read(66, 326) == 0);
static_assert(rx_fifo_incomplete_read(65, 1) == 1);
static_assert(rx_fifo_complete_read(65, 65) == 64);
static_assert(rx_fifo_complete_read(65, 64) == 64);
static_assert(rx_fifo_complete_read(63, 64) == 0);

int main() {
  // Polling policy is independent of count/remaining: it depends only on
  // whether this iteration successfully drained a FIFO burst.
  for (std::size_t remaining = 1; remaining <= 326; ++remaining) {
    for (unsigned available : {0u, 1u, 63u, 64u, 65u, 66u}) {
      for (bool made_progress : {false, true}) {
        (void) remaining;
        (void) available;
        assert(rx_should_backoff_after_drain(made_progress) == !made_progress);
      }
    }
  }
  return 0;
}
