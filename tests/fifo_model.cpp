#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <vector>

static size_t next_chunk(size_t available,size_t remaining,
                         bool header,size_t confirmed) {
  if(!available||!remaining)return 0;
  if(header||available<remaining)
    return available>1?std::min(available-1,remaining):0;
  return confirmed>=remaining?remaining:0;
}
struct Receiver {
  std::deque<uint8_t> fifo;
  std::vector<uint8_t> out;
  bool header=true;
  size_t remaining=3;
  size_t expected;
  unsigned early_empty=0;
  explicit Receiver(size_t bytes):expected(bytes){out.reserve(bytes);}
  void push(uint8_t b){fifo.push_back(b);assert(fifo.size()<=64);drain();}
  void drain() {
    for(;;){
      size_t n=next_chunk(fifo.size(),remaining,header,fifo.size());
      if(!n)break;
      if(header&&n==fifo.size())++early_empty;
      for(size_t i=0;i<n;i++){out.push_back(fifo.front());fifo.pop_front();}
      remaining-=n;
      if(!remaining&&header){header=false;remaining=expected-3;}
      if(!remaining)break;
    }
  }
};
int main() {
  assert(next_chunk(1,30,false,1)==0);
  assert(next_chunk(1,1,true,1)==0);
  assert(next_chunk(3,3,true,3)==2);
  assert(next_chunk(2,2,false,1)==0);
  assert(next_chunk(2,2,false,2)==2);
  assert(next_chunk(32,35,false,32)==31);
  for(size_t length : {size_t(53),size_t(326),size_t(430)}) {
    Receiver r(length);
    std::vector<uint8_t> source;
    for(size_t i=0;i<length;i++)source.push_back(uint8_t((i*37+19)&0xff));
    for(uint8_t b:source)r.push(b);
    r.drain();
    assert(r.out==source);
    assert(r.fifo.empty()&&r.early_empty==0);
    printf("PASS: FIFO model %zu bytes\n",length);
  }
  puts("Model does not simulate RF errors, SPI timing or IRQ preemption");
}
