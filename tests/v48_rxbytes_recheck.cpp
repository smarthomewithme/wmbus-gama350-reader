#include <cassert>
#include <cstdint>
#include <cstdio>
#include <initializer_list>
#include <utility>
#include <vector>

#include "../vendor/cc1101_v4/components/wmbus_radio/cc1101_fifo.h"

using esphome::wmbus_radio::retry_invalid_fifo_count;

struct Samples {
  std::vector<std::pair<bool, uint8_t>> sequence;
  size_t used = 0;
  explicit Samples(std::initializer_list<std::pair<bool, uint8_t>> values) : sequence(values) {}
  bool next(uint8_t &value) {
    assert(used < sequence.size());
    const auto sample = sequence[used++];
    if (sample.first)
      value = sample.second;
    return sample.first;
  }
};

int main() {
  {
    // A single transient 65 must recover without touching the normal path.
    uint8_t raw = 65;
    Samples sample{{true, 35}};
    unsigned int pauses = 0;
    assert(retry_invalid_fifo_count(raw,
                                   [&](uint8_t &next) { return sample.next(next); },
                                   [&]() { ++pauses; }));
    assert(raw == 35 && pauses == 1 && sample.used == 1);
  }
  {
    // Both unstable and overflow-marked samples must be rejected.
    uint8_t raw = 65;
    Samples sample{{false, 0}, {true, 0x80}, {true, 64}};
    unsigned int pauses = 0;
    assert(retry_invalid_fifo_count(raw,
                                   [&](uint8_t &next) { return sample.next(next); },
                                   [&]() { ++pauses; }));
    assert(raw == 64 && pauses == 3 && sample.used == 3);
  }
  {
    // Persistent impossible values fail closed after exactly three tries.
    uint8_t raw = 65;
    Samples sample{{true, 65}, {true, 65}, {true, 65}};
    unsigned int pauses = 0;
    assert(!retry_invalid_fifo_count(raw,
                                    [&](uint8_t &next) { return sample.next(next); },
                                    [&]() { ++pauses; }));
    assert(raw == 65 && pauses == 3 && sample.used == 3);
  }
  {
    // Never reinterpret a real hardware overflow as a recoverable sample.
    uint8_t raw = 0xC1;
    unsigned int samples = 0, pauses = 0;
    assert(!retry_invalid_fifo_count(raw,
                                    [&](uint8_t &) { ++samples; return true; },
                                    [&]() { ++pauses; }));
    assert(raw == 0xC1 && samples == 0 && pauses == 0);
  }
  {
    // Do not add retries for an already valid FIFO count.
    uint8_t raw = 64;
    unsigned int samples = 0, pauses = 0;
    assert(!retry_invalid_fifo_count(raw,
                                    [&](uint8_t &) { ++samples; return true; },
                                    [&]() { ++pauses; }));
    assert(raw == 64 && samples == 0 && pauses == 0);
  }
  {
    // A stable empty count is not an invitation to read past FIFO boundaries.
    uint8_t raw = 65;
    Samples sample{{true, 0}};
    assert(retry_invalid_fifo_count(raw,
                                   [&](uint8_t &next) { return sample.next(next); },
                                   []() {}));
    assert(raw == 0);
  }
  std::puts("V48_INVALID_RXBYTES_BOUNDED_RECOVERY_PASS");
}
