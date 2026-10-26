#include <cstdint>
#include <cstdio>
#include <vector>
struct Packet {
  std::vector<uint8_t> data;
  Packet(){data.reserve(3);}
  __attribute__((noinline)) uint8_t* rx_data_ptr(){return data.data()+data.size();}
  __attribute__((noinline)) size_t rx_capacity(){auto n=data.capacity()-data.size();data.resize(data.capacity());return n;}
};
__attribute__((noinline)) void read_in_task(uint8_t* dst,size_t count,int){
  fprintf(stderr,"count=%zu\n",count);
  dst[0]=0xAB;
}
int main(){
  Packet p;
  read_in_task(p.rx_data_ptr(),p.rx_capacity(),0);
  printf("Byte: %02X\n",p.data[0]);
}
