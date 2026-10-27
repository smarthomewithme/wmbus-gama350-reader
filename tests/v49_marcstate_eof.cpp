// Native CC1101 v4.9 model: isolated, bounded MARCSTATE EOF confirmation.
// Compiled against the exact cc1101_fifo.h prepared from pinned upstream.
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <vector>
#include "cc1101_fifo.h"

using esphome::wmbus_radio::confirm_marcstate_eof;

namespace {
constexpr uint8_t IDLE = 1;
constexpr uint8_t RX_END = 2;
constexpr uint8_t RX_ACTIVE = 13;

bool probe(uint8_t initial, std::initializer_list<uint8_t> subsequent,
           bool expected, std::size_t expected_reads) {
  const std::vector<uint8_t> samples(subsequent);
  std::size_t reads = 0;
  const auto terminal = [](uint8_t value) {
    return value == IDLE || value == RX_END;
  };
  const bool result = confirm_marcstate_eof(
      initial,
      [&]() -> uint8_t {
        assert(reads < samples.size());
        return samples[reads++];
      },
      terminal);
  assert(reads == expected_reads);
  assert(result == expected);
  return result;
}
}  // namespace

int main() {
  // A normal receive state never incurs additional status SPI transactions.
  assert(!probe(RX_ACTIVE, {}, false, 0));
  // Immediate repeated terminal samples are accepted.
  assert(probe(IDLE, {IDLE}, true, 1));
  assert(probe(RX_END, {RX_END}, true, 1));
  // The realistic RX_END -> IDLE transition requires a stable second IDLE.
  assert(probe(RX_END, {IDLE, IDLE}, true, 2));
  // A transient false IDLE/RX_END cannot truncate the FIFO read.
  assert(!probe(IDLE, {RX_ACTIVE}, false, 1));
  assert(!probe(RX_END, {RX_ACTIVE}, false, 1));
  assert(!probe(RX_END, {IDLE, RX_ACTIVE}, false, 2));
  // Three alternating terminal readings exhaust the bounded retry budget.
  assert(!probe(IDLE, {RX_END, IDLE, RX_END}, false, 3));
  assert(!probe(RX_END, {IDLE, RX_END, IDLE}, false, 3));
}
