#include <cstdint>
#include <cstdio>
#include <vector>
__attribute__((noinline)) int extract(std::vector<uint8_t>& data) {
  auto segments=data.size()*8/6;
  int total=0;
  for(size_t i=0;i<segments;i++){
    auto bit_idx=i*6;
    auto byte_idx=bit_idx/8;
    auto offset=bit_idx%8;
    uint8_t code=(data[byte_idx]<<offset);
    if(offset>0)code |= (data[byte_idx+1]>>(8-offset));
    total+=code>>2;
  }
  return total;
}
int main(){std::vector<uint8_t> b{0x5A,0x3C,0xE7};printf("%d\n",extract(b));}
