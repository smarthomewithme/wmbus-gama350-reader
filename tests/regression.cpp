#include <cassert>
#include <cstdint>
#include <cstdio>
#include <vector>
#include <array>
#include <algorithm>

static const std::array<uint8_t, 16> codes = {
  0x16, 0x0D, 0x0E, 0x0B, 0x1C, 0x19, 0x1A, 0x13,
  0x2C, 0x25, 0x26, 0x23, 0x34, 0x31, 0x32, 0x29
};

std::vector<uint8_t> decode(const std::vector<uint8_t>& src) {
  const size_t segments = src.size() * 8 / 6;
  if (segments % 2) return {};
  std::vector<uint8_t> result;
  for (size_t i=0;i<segments;i++) {
    const size_t bit_idx=i*6, byte_idx=bit_idx/8, bit_offset=bit_idx%8;
    if (byte_idx>=src.size()) return {};
    uint8_t v=uint8_t(src[byte_idx]<<bit_offset);
    if (bit_offset>2) {
      if (byte_idx+1>=src.size()) return {};
      v |= uint8_t(src[byte_idx+1]>>(8-bit_offset));
    }
    const uint8_t symbol=v>>2;
    auto pos=std::find(codes.begin(),codes.end(),symbol);
    if (pos==codes.end()) return {};
    uint8_t nibble=uint8_t(pos-codes.begin());
    if (i%2==0) result.push_back(uint8_t(nibble<<4));
    else result.back() |= nibble;
  }
  return result;
}

uint16_t crc_en13757(const std::vector<uint8_t>& b,size_t length) {
  uint16_t crc=0;
  for(size_t i=0;i<length;i++) {
    crc ^= uint16_t(b[i])<<8;
    for(int j=0;j<8;j++)
      crc=(crc&0x8000)?uint16_t((crc<<1)^0x3D65):uint16_t(crc<<1);
  }
  return crc ^ 0xFFFF;
}

std::vector<uint8_t> encode(const std::vector<uint8_t>& src) {
  std::vector<uint8_t> out;
  uint32_t bits=0;
  int used=0;
  for(uint8_t val:src)
    for(uint8_t nib : {uint8_t(val>>4),uint8_t(val&0x0f)}) {
      bits=(bits<<6)|codes[nib];used+=6;
      while(used>=8) {
        used-=8;
        out.push_back(uint8_t(bits>>used));
        bits &= (1u<<used)-1;
      }
    }
  if(used)out.push_back(uint8_t(bits<<(8-used)));
  return out;
}

size_t original_fifo_policy(size_t available,size_t remaining) {
  return (remaining>1&&available>1)
    ? std::min(available-1,remaining) : std::min(available,remaining);
}
size_t guarded_fifo_policy(size_t available,size_t remaining,bool header) {
  if(!header&&available>=remaining) return remaining;
  if(available<=1) return 0;
  return std::min(available-1,remaining);
}
struct PacketBuffer {
  std::vector<uint8_t> data;
  PacketBuffer(){data.reserve(3);}
  uint8_t* rx_data_ptr(){return data.data()+data.size();}
  size_t rx_capacity(){size_t n=data.capacity()-data.size();data.resize(data.capacity());return n;}
  void reserve(size_t n){data.reserve(n);}
};

int main() {
  const std::vector<uint8_t> expected={
    0xBE,0x44,0xED,0x14,0x78,0x56,0x34,0x12,0x01,0x02,0x24,0x2A,0x7A
  };
  const std::vector<uint8_t> raw={
    0x8F,0x27,0x1C,0xCB,0x13,0x5C,0x4E,0xC6,0x5A,0x2D,
    0xC3,0x4E,0x58,0xD5,0x8E,0x39,0xC3,0xA6,0x4E,0x60
  };
  assert(encode(expected)==raw);
  assert(decode(raw)==expected);
  assert(crc_en13757(expected,10)==0x242A);
  puts("PASS: sanitized GAMA 350 header 3-of-6 decode and CRC");
  assert(decode(std::vector<uint8_t>(raw.begin(),raw.begin()+3)).size()==2);
  puts("PASS: short 3-byte header is in-bounds");
  auto invalid=raw;invalid[0]=0;
  assert(decode(invalid).empty());
  puts("PASS: invalid symbol rejected");
  assert(original_fifo_policy(1,30)==1);
  assert(guarded_fifo_policy(1,30,false)==0);
  assert(guarded_fifo_policy(32,30,true)==30);
  assert(guarded_fifo_policy(29,30,false)==28);
  assert(guarded_fifo_policy(30,30,false)==30);
  puts("PASS: FIFO model guard conditions");
  PacketBuffer p;
  auto* head=p.rx_data_ptr();
  const auto cap=p.rx_capacity();
  assert(cap==3);
  for(size_t i=0;i<cap;i++)head[i]=uint8_t(i+1);
  assert((p.data==std::vector<uint8_t>{1,2,3}));
  p.reserve(326);
  auto* payload=p.rx_data_ptr();
  const auto tail=p.rx_capacity();
  assert(tail>=323);
  for(size_t i=0;i<323;i++)payload[i]=uint8_t(i&0xff);
  assert(p.data[3]==0&&p.data[325]==uint8_t(322&0xff));
  puts("PASS: sequenced buffer operations, 326-byte simulated payload");
}
