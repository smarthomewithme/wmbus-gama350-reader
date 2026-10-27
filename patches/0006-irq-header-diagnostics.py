#!/usr/bin/env python3
"""Deterministic v4.3 passive header diagnostics overlay on pinned upstream + patches 0001-0005.

The overlay is applied during GitHub-hosted ESPHome preparation. Every edit is
guarded by an exact, unique original snippet: upstream drift fails closed.
No receive timing, modem registers, encryption, packet parsing, or FIFO logic
is modified. Only lightweight timing/failure counters are added.
"""
from __future__ import annotations

from pathlib import Path
import sys


def replace_one(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    occurrences = text.count(old)
    if occurrences != 1:
        raise RuntimeError(
            f"v4.3 overlay: expected one match in {path.name}, "
            f"found {occurrences}: {old[:90]!r}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


def apply(root: Path) -> None:
    r = root / "components" / "wmbus_radio"
    transceiver = r / "transceiver.h"
    cc_header = r / "transceiver_cc1101.h"
    cc_source = r / "transceiver_cc1101.cpp"
    radio_header = r / "component.h"
    radio_source = r / "component.cpp"

    replace_one(
        transceiver,
        "namespace wmbus_radio {\n\n// RX Gain modes",
        """namespace wmbus_radio {

// Read failure is recorded in the receiver task; no additional SPI reads.
enum class ReceiveFailure : uint8_t {
  NONE, EMPTY_TIMEOUT, PARTIAL_TIMEOUT, UNSTABLE_RXBYTES,
  FIFO_OVERFLOW, INVALID_FIFO_COUNT, EARLY_END, UNKNOWN
};

// RX Gain modes""",
    )
    replace_one(
        transceiver,
        "  virtual const char *get_name() = 0;\n",
        """  virtual const char *get_name() = 0;
  // Optional diagnostics; other radio drivers are not affected.
  virtual ReceiveFailure last_receive_failure() const { return ReceiveFailure::UNKNOWN; }
""",
    )
    replace_one(
        cc_header,
        "  const char *get_name() override;\n",
        """  const char *get_name() override;
  ReceiveFailure last_receive_failure() const override { return this->read_failure_; }
""",
    )
    replace_one(
        cc_header,
        "  int8_t last_rssi_{0};\n",
        """  int8_t last_rssi_{0};
  // Only accessed by the radio receiver task.
  ReceiveFailure read_failure_{ReceiveFailure::NONE};
""",
    )
    replace_one(
        cc_source,
        """bool CC1101::read_in_task(uint8_t *buffer, size_t length, uint32_t offset) {
  size_t total = 0;""",
        """bool CC1101::read_in_task(uint8_t *buffer, size_t length, uint32_t offset) {
  this->read_failure_ = ReceiveFailure::NONE;
  size_t total = 0;""",
    )
    replace_one(
        cc_source,
        """        ESP_LOGW(TAG, "RXBYTES unstable / no progress after %lu bytes",
                 (unsigned long) (offset + total));
        return false;""",
        """        ESP_LOGW(TAG, "RXBYTES unstable / no progress after %lu bytes",
                 (unsigned long) (offset + total));
        this->read_failure_ = ReceiveFailure::UNSTABLE_RXBYTES;
        return false;""",
    )
    replace_one(
        cc_source,
        """      ESP_LOGW(TAG, "RX FIFO overflow");
      this->restart_rx();
      return false;""",
        """      ESP_LOGW(TAG, "RX FIFO overflow");
      this->read_failure_ = ReceiveFailure::FIFO_OVERFLOW;
      this->restart_rx();
      return false;""",
    )
    replace_one(
        cc_source,
        """      ESP_LOGW(TAG, "Invalid RX FIFO count: %u", (unsigned) available);
      return false;""",
        """      ESP_LOGW(TAG, "Invalid RX FIFO count: %u", (unsigned) available);
      this->read_failure_ = ReceiveFailure::INVALID_FIFO_COUNT;
      return false;""",
    )
    replace_one(
        cc_source,
        """          ESP_LOGW(TAG, "RX FIFO overflow during final chunk");
          this->restart_rx();
          return false;""",
        """          ESP_LOGW(TAG, "RX FIFO overflow during final chunk");
          this->read_failure_ = ReceiveFailure::FIFO_OVERFLOW;
          this->restart_rx();
          return false;""",
    )
    replace_one(
        cc_source,
        """          ESP_LOGW(TAG, "RX FIFO overflow on final drain");
          return false;""",
        """          ESP_LOGW(TAG, "RX FIFO overflow on final drain");
          this->read_failure_ = ReceiveFailure::FIFO_OVERFLOW;
          return false;""",
    )
    replace_one(
        cc_source,
        """      ESP_LOGW(TAG, "RX timeout after %lu bytes (need %lu)", (unsigned long)(total + offset), (unsigned long)(length + offset));
      return false;""",
        """      ESP_LOGW(TAG, "RX timeout after %lu bytes (need %lu)", (unsigned long)(total + offset), (unsigned long)(length + offset));
      this->read_failure_ = (total == 0 && offset == 0)
                                ? ReceiveFailure::EMPTY_TIMEOUT
                                : ReceiveFailure::PARTIAL_TIMEOUT;
      return false;""",
    )
    replace_one(
        cc_source,
        """  return (total == length);
}

} // namespace wmbus_radio""",
        """  if (total != length)
    this->read_failure_ = ReceiveFailure::EARLY_END;
  return (total == length);
}

} // namespace wmbus_radio""",
    )
    replace_one(
        radio_header,
        """  uint32_t last_diag_log_ms_{0};

  std::vector""",
        """  uint32_t last_diag_log_ms_{0};

  // Cumulative mutually exclusive reasons for failed 3-byte headers.
  std::atomic<uint32_t> header_empty_timeout_{0};
  std::atomic<uint32_t> header_partial_timeout_{0};
  std::atomic<uint32_t> header_unstable_{0};
  std::atomic<uint32_t> header_overflow_{0};
  std::atomic<uint32_t> header_invalid_count_{0};
  std::atomic<uint32_t> header_early_end_{0};
  std::atomic<uint32_t> header_other_{0};
  std::atomic<uint32_t> invalid_payload_size_{0};

  std::vector""",
    )
    replace_one(
        radio_source,
        """  }
  Packet *p;
  if (xQueueReceive(this->packet_queue_, &p, 0) != pdPASS)""",
        """    ESP_LOGI(TAG, "RX_HEADER_DIAG cumulative hdr_timeout_empty=%lu hdr_timeout_partial=%lu hdr_unstable=%lu hdr_overflow=%lu hdr_invalid_fifo=%lu hdr_early_end=%lu hdr_other=%lu invalid_payload_length=%lu",
             (unsigned long) this->header_empty_timeout_.load(std::memory_order_relaxed),
             (unsigned long) this->header_partial_timeout_.load(std::memory_order_relaxed),
             (unsigned long) this->header_unstable_.load(std::memory_order_relaxed),
             (unsigned long) this->header_overflow_.load(std::memory_order_relaxed),
             (unsigned long) this->header_invalid_count_.load(std::memory_order_relaxed),
             (unsigned long) this->header_early_end_.load(std::memory_order_relaxed),
             (unsigned long) this->header_other_.load(std::memory_order_relaxed),
             (unsigned long) this->invalid_payload_size_.load(std::memory_order_relaxed));
  }
  Packet *p;
  if (xQueueReceive(this->packet_queue_, &p, 0) != pdPASS)""",
    )
    replace_one(
        radio_source,
        """  if (!this->radio->read_in_task(header_data, header_capacity, 0)) {
    this->headers_failed_.fetch_add(1, std::memory_order_relaxed);
    this->radio->restart_rx();
    return;
  }""",
        """  if (!this->radio->read_in_task(header_data, header_capacity, 0)) {
    this->headers_failed_.fetch_add(1, std::memory_order_relaxed);
    switch (this->radio->last_receive_failure()) {
      case ReceiveFailure::EMPTY_TIMEOUT:
        this->header_empty_timeout_.fetch_add(1, std::memory_order_relaxed);
        break;
      case ReceiveFailure::PARTIAL_TIMEOUT:
        this->header_partial_timeout_.fetch_add(1, std::memory_order_relaxed);
        break;
      case ReceiveFailure::UNSTABLE_RXBYTES:
        this->header_unstable_.fetch_add(1, std::memory_order_relaxed);
        break;
      case ReceiveFailure::FIFO_OVERFLOW:
        this->header_overflow_.fetch_add(1, std::memory_order_relaxed);
        break;
      case ReceiveFailure::INVALID_FIFO_COUNT:
        this->header_invalid_count_.fetch_add(1, std::memory_order_relaxed);
        break;
      case ReceiveFailure::EARLY_END:
        this->header_early_end_.fetch_add(1, std::memory_order_relaxed);
        break;
      default:
        this->header_other_.fetch_add(1, std::memory_order_relaxed);
        break;
    }
    this->radio->restart_rx();
    return;
  }""",
    )
    replace_one(
        radio_source,
        """  if (!packet->calculate_payload_size()) {
    this->payloads_failed_.fetch_add(1, std::memory_order_relaxed);
    this->radio->restart_rx();
    return;
  }""",
        """  if (!packet->calculate_payload_size()) {
    this->payloads_failed_.fetch_add(1, std::memory_order_relaxed);
    this->invalid_payload_size_.fetch_add(1, std::memory_order_relaxed);
    this->radio->restart_rx();
    return;
  }""",
    )

    # One diagnostic version marker; does not alter packet handling.
    replace_one(
        radio_source,
        """  ESP_LOGI(TAG, "Receiver task created [%p]", this->receiver_task_handle_);""",
        """  ESP_LOGI(TAG, "SHWM v4.3 passive header diagnostics enabled; FIFO16 unchanged");
  ESP_LOGI(TAG, "Receiver task created [%p]", this->receiver_task_handle_);""",
    )

    # Refuse to accept an incomplete overlay, including when re-run accidentally.
    checks = {
        transceiver: ("enum class ReceiveFailure", "last_receive_failure"),
        cc_source: ("ReceiveFailure::EMPTY_TIMEOUT", "ReceiveFailure::EARLY_END"),
        radio_header: ("header_empty_timeout_", "header_other_"),
        radio_source: ("RX_HEADER_DIAG", "SHWM v4.3 passive header diagnostics enabled"),
    }
    for path, signatures in checks.items():
        body = path.read_text(encoding="utf-8")
        for signature in signatures:
            if signature not in body:
                raise RuntimeError(f"v4.3 overlay verification failed: {path.name}: {signature}")

    print("V43_PASSIVE_DIAG_OVERLAY_PASS: pinned FIFO16 unchanged; no ISR instrumentation")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python patches/0006-irq-header-diagnostics.py <upstream-checkout>")
    apply(Path(sys.argv[1]).resolve())
