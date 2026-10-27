#include "cc1101_fifo.h"
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
using esphome::wmbus_radio::rx_no_progress_backoff_us;
using esphome::wmbus_radio::rx_v417_no_progress_backoff_us;
using esphome::wmbus_radio::rx_v418_no_progress_backoff_us;
using esphome::wmbus_radio::rx_should_backoff_after_drain;
static_assert(rx_no_progress_backoff_us(3,323)==50u,"v4.16 preserved");
static_assert(rx_v417_no_progress_backoff_us(3,323)==100u,"v4.17 preserved");
static_assert(rx_v418_no_progress_backoff_us(0,3)==200u,"header");
static_assert(rx_v418_no_progress_backoff_us(3,5)==200u,"tiny payload");
static_assert(rx_v418_no_progress_backoff_us(3,50)==200u,"Apator");
static_assert(rx_v418_no_progress_backoff_us(3,249)==200u,"threshold minus one");
static_assert(rx_v418_no_progress_backoff_us(3,250)==150u,"threshold");
static_assert(rx_v418_no_progress_backoff_us(3,323)==150u,"GAMA");
static_assert(rx_v418_no_progress_backoff_us(3,500)==150u,"longer");
static_assert(rx_v418_no_progress_backoff_us(4,323)==200u,"offset guard");
static_assert(rx_should_backoff_after_drain(false),"wait when no progress");
static_assert(!rx_should_backoff_after_drain(true),"skip wait on progress");
int main() {
 struct Case {uint32_t offset;std::size_t length;unsigned int wait;};
 for(const auto &x : {Case{0,3,200},Case{3,5,200},Case{3,50,200},Case{3,249,200},Case{3,250,150},Case{3,323,150},Case{4,323,200}})
  assert(rx_v418_no_progress_backoff_us(x.offset,x.length)==x.wait);
}
