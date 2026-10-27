// Native CC1101 SWRZ020E FIFO-prefetch regression: no ESPHome or radio hardware.
#include <cassert>
#include <cstddef>
#include <cstdint>
#include "cc1101_fifo.h"

using esphome::wmbus_radio::rx_fifo_count_plausible;
using esphome::wmbus_radio::rx_fifo_incomplete_read;
using esphome::wmbus_radio::rx_fifo_complete_read;

static_assert(rx_fifo_count_plausible(64), "64 is physically in FIFO");
static_assert(rx_fifo_count_plausible(65), "65 includes the prefetch byte");
static_assert(!rx_fifo_count_plausible(66), "66 is an invalid count");
static_assert(rx_fifo_incomplete_read(65, 323) == 64, "never read 65 in one burst");
static_assert(rx_fifo_incomplete_read(65, 3) == 3, "bounded header capacity");
static_assert(rx_fifo_complete_read(65, 65) == 64, "read the last byte in a second burst");
static_assert(rx_fifo_complete_read(1, 1) == 1, "read final byte");
static_assert(rx_fifo_complete_read(65, 66) == 0, "wait for incomplete packet");

int main() {
  for (uint16_t raw = 0; raw < 128; ++raw) {
    for (std::size_t remaining = 0; remaining <= 512; ++remaining) {
      const auto partial = rx_fifo_incomplete_read(static_cast<uint8_t>(raw), remaining);
      const auto final = rx_fifo_complete_read(static_cast<uint8_t>(raw), remaining);
      assert(partial <= remaining && final <= remaining);
      assert(partial <= 64 && final <= 64);
      if (raw > 65 || remaining == 0) {
        assert(partial == 0 && final == 0);
      }
      if (raw >= 2 && raw <= 65 && remaining > 0) {
        assert(partial <= raw - 1);  // Incomplete packet keeps a byte in FIFO.
      }
      if (raw < remaining)
        assert(final == 0);
    }
  }
  return 0;
}
