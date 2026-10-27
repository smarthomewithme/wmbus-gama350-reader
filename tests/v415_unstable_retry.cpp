#include "cc1101_fifo.h"
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <initializer_list>

using esphome::wmbus_radio::rx_should_backoff_after_unstable;
static_assert(rx_should_backoff_after_unstable(0, 3), "header");
static_assert(rx_should_backoff_after_unstable(3, 5), "short");
static_assert(rx_should_backoff_after_unstable(3, 50), "Apator");
static_assert(rx_should_backoff_after_unstable(3, 249), "boundary below");
static_assert(!rx_should_backoff_after_unstable(3, 250), "boundary at");
static_assert(!rx_should_backoff_after_unstable(3, 323), "GAMA payload");
static_assert(!rx_should_backoff_after_unstable(3, 500), "longer payload");
static_assert(rx_should_backoff_after_unstable(0, 323), "header-like");
static_assert(rx_should_backoff_after_unstable(4, 323), "other offset");

int main() {
  struct Sample { uint32_t offset; std::size_t length; bool wait; };
  for (const auto &sample : {Sample{0, 3, true}, Sample{3, 5, true},
                             Sample{3, 50, true}, Sample{3, 249, true},
                             Sample{3, 250, false}, Sample{3, 323, false},
                             Sample{4, 323, true}}) {
    assert(rx_should_backoff_after_unstable(sample.offset, sample.length) == sample.wait);
  }
}
