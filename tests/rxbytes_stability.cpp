#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <initializer_list>
#include <vector>

#include "../vendor/upstream/components/wmbus_radio/cc1101_fifo.h"

using esphome::wmbus_radio::read_stable_rxbytes;

struct Samples {
  std::vector<uint8_t> samples;
  size_t position = 0;

  explicit Samples(std::initializer_list<uint8_t> values) : samples(values) {}

  uint8_t next() {
    assert(position < samples.size());
    return samples[position++];
  }
};

int main() {
  {
    Samples read{32, 32};
    uint8_t accepted = 0xFF;
    assert(read_stable_rxbytes([&]() { return read.next(); }, accepted));
    assert(accepted == 32);
    assert(read.position == 2);
  }
  {
    // Ignore a transient wrong count rather than reading past a 32-byte FIFO.
    Samples read{63, 32, 32};
    uint8_t accepted = 0;
    assert(read_stable_rxbytes([&]() { return read.next(); }, accepted));
    assert(accepted == 32);
    assert(read.position == 3);
  }
  {
    Samples read{40, 41, 42, 43, 44, 45, 46, 47, 48};
    uint8_t accepted = 0xAA;
    assert(!read_stable_rxbytes([&]() { return read.next(); }, accepted));
    assert(accepted == 0xAA); // Fail closed: don't touch the output.
    assert(read.position == 9);
  }
  {
    Samples read{0, 0};
    uint8_t accepted = 0xAA;
    assert(read_stable_rxbytes([&]() { return read.next(); }, accepted));
    assert(accepted == 0);
  }
  {
    // Overflow indication is preserved for the caller, not masked away.
    Samples read{0x80, 0x80};
    uint8_t accepted = 0;
    assert(read_stable_rxbytes([&]() { return read.next(); }, accepted));
    assert((accepted & 0x80) != 0);
  }
  {
    Samples read{64, 64};
    uint8_t accepted = 0;
    assert(read_stable_rxbytes([&]() { return read.next(); }, accepted));
    assert(accepted == 64);
  }
  puts("PASS: CC1101 RXBYTES stable-read and bounded retry cases");
}
