#include "cc1101_fifo.h"
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
using esphome::wmbus_radio::rx_no_progress_backoff_us;
using esphome::wmbus_radio::rx_should_backoff_after_drain;
static_assert(rx_no_progress_backoff_us(0,3)==200u,"header");
static_assert(rx_no_progress_backoff_us(3,5)==200u,"short");
static_assert(rx_no_progress_backoff_us(3,50)==200u,"Apator");
static_assert(rx_no_progress_backoff_us(3,249)==200u,"under threshold");
static_assert(rx_no_progress_backoff_us(3,250)==50u,"threshold");
static_assert(rx_no_progress_backoff_us(3,323)==50u,"GAMA payload");
static_assert(rx_no_progress_backoff_us(3,500)==50u,"long payload");
static_assert(rx_no_progress_backoff_us(4,323)==200u,"offset guard");
static_assert(rx_should_backoff_after_drain(false),"no-progress");
static_assert(!rx_should_backoff_after_drain(true),"progress");
int main() {
  struct Sample { uint32_t offset;std::size_t length;unsigned int wait;};
  for(const auto &v:{Sample{0,3,200},Sample{3,5,200},Sample{3,50,200},
                     Sample{3,249,200},Sample{3,250,50},Sample{3,323,50},
                     Sample{4,323,200}}) {
    assert(rx_no_progress_backoff_us(v.offset,v.length)==v.wait);
  }
}
