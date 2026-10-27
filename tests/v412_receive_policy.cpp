// SHWM v4.12: no MARCSTATE polling after making FIFO progress.
// Synthetic policy-only test; not a physical radio/ESPHome test.
#include <cassert>
#include <cstddef>
#include "cc1101_fifo.h"

using esphome::wmbus_radio::rx_should_probe_marcstate;
using esphome::wmbus_radio::rx_fifo_incomplete_read;

static_assert(!rx_should_probe_marcstate(true, 0, 326), "no EOF probe after progress");
static_assert(!rx_should_probe_marcstate(true, 150, 326), "drain without status SPI");
static_assert(rx_should_probe_marcstate(false, 150, 326), "probe stalled partial frame");
static_assert(rx_should_probe_marcstate(false, 1, 3), "probe stalled short header");
static_assert(!rx_should_probe_marcstate(false, 0, 326), "no data, no EOF");
static_assert(!rx_should_probe_marcstate(false, 326, 326), "complete frame, no EOF");
static_assert(!rx_should_probe_marcstate(false, 327, 326), "cannot over-read");

int main() {
  for (std::size_t length = 1; length < 600; ++length) {
    for (std::size_t received = 0; received <= length; ++received) {
      assert(!rx_should_probe_marcstate(true, received, length));
      assert(rx_should_probe_marcstate(false, received, length) ==
             (received > 0 && received < length));
    }
  }
  assert(rx_fifo_incomplete_read(65, 326) == 64);
  return 0;
}
