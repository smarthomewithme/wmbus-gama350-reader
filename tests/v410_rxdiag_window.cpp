// Pure five-minute diagnostic counter fixture: no hardware and no ESPHome.
#include <cassert>
#include <cstdint>
#include "rx_diag_window.h"

using esphome::wmbus_radio::RxDiagSnapshot;
using esphome::wmbus_radio::rx_diag_delta;

int main() {
  const RxDiagSnapshot first{
      200, 192, 8, 189, 3, 43, 0, 190, 2,
  };
  const RxDiagSnapshot after{
      250, 239, 11, 236, 3, 51, 0, 237, 2,
  };
  const auto interval = rx_diag_delta(after, first);
  assert(interval.irq_notifications == 50);
  assert(interval.headers_ok == 47);
  assert(interval.headers_failed == 3);
  assert(interval.payloads_ok == 47);
  assert(interval.payloads_failed == 0);
  assert(interval.long_radio_frames == 8);
  assert(interval.queue_drops == 0);
  assert(interval.frame_converted == 47);
  assert(interval.frame_conversion_failed == 0);

  // A zero initial snapshot represents counters since boot.
  const auto boot = rx_diag_delta(first, {});
  assert(boot.irq_notifications == 200);
  assert(boot.long_radio_frames == 43);
  assert(boot.frame_conversion_failed == 2);

  // Unsigned counter wrap must never look like a huge interval.
  const RxDiagSnapshot near_wrap{
      0xFFFFFFFEu, 0xFFFFFFFFu, 7, 5, 1, 15, 0, 6, 2,
  };
  const RxDiagSnapshot wrapped{
      3, 2, 7, 5, 1, 15, 0, 6, 2,
  };
  const auto wrapped_window = rx_diag_delta(wrapped, near_wrap);
  assert(wrapped_window.irq_notifications == 5);
  assert(wrapped_window.headers_ok == 3);
  assert(wrapped_window.headers_failed == 0);
  assert(wrapped_window.payloads_ok == 0);
  assert(wrapped_window.long_radio_frames == 0);
}
