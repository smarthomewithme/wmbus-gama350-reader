#include "cc1101_fifo.h"
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
using esphome::wmbus_radio::rx_v420_post_progress_wait_us;
using esphome::wmbus_radio::rx_v417_no_progress_backoff_us;
using esphome::wmbus_radio::rx_should_backoff_after_drain;
static_assert(rx_v420_post_progress_wait_us(3,323,true)==75u,"GAMA only after progress");
static_assert(rx_v420_post_progress_wait_us(3,250,true)==75u,"long threshold");
static_assert(rx_v420_post_progress_wait_us(3,249,true)==0u,"threshold minus one");
static_assert(rx_v420_post_progress_wait_us(3,50,true)==0u,"Apator short");
static_assert(rx_v420_post_progress_wait_us(3,5,true)==0u,"tiny short");
static_assert(rx_v420_post_progress_wait_us(0,3,true)==0u,"header");
static_assert(rx_v420_post_progress_wait_us(4,323,true)==0u,"offset guard");
static_assert(rx_v420_post_progress_wait_us(3,323,false)==0u,"no progress");
static_assert(rx_v417_no_progress_backoff_us(3,323)==100u,"v4.17 idle long");
static_assert(rx_v417_no_progress_backoff_us(3,50)==200u,"v4.17 Apator idle");
static_assert(rx_should_backoff_after_drain(false),"idle wait");
static_assert(!rx_should_backoff_after_drain(true),"no idle wait after burst");
int main(){
 struct Sample {uint32_t offset;std::size_t length;bool progress;unsigned int wait;};
 for(const auto &s:{Sample{0,3,true,0},Sample{3,50,true,0},Sample{3,249,true,0},
                    Sample{3,250,true,75},Sample{3,323,true,75},Sample{3,500,true,75},
                    Sample{3,323,false,0},Sample{4,323,true,0}}){
   assert(rx_v420_post_progress_wait_us(s.offset,s.length,s.progress)==s.wait);
 }
}
