#pragma once

#include "pch.h"
#define uint64 unsigned long long

uint64 __n_biggest_bits_mask(unsigned char n);
uint64 __n_smallest_bits_mask(unsigned char n);

struct bitboard {
	uint64 low; // squares from  0 to 63
	uint64 high; // squares from 64 to 99
};

typedef bitboard Bitboard;


inline extern void __assign(Bitboard* b1, const Bitboard* b2);
inline extern void __negate(Bitboard* result, const Bitboard* b);
inline extern void __and(Bitboard* result, const Bitboard* b1, const Bitboard* b2);
inline extern void __or(Bitboard* result, const Bitboard* b1, const Bitboard* b2);
inline extern void __xor(Bitboard* result, const Bitboard* b1, const Bitboard* b2);
inline extern void __lshift(Bitboard* result, const Bitboard* b, unsigned char off);
inline extern void __rshift(Bitboard* result, const Bitboard* b, unsigned char off);
inline extern void __inc(Bitboard* res, Bitboard* src);
inline extern void __dec(Bitboard* res, Bitboard* src);
inline extern void __add(Bitboard* result, const Bitboard* b1,  const Bitboard* b2);
inline extern void __sub(Bitboard* result, const Bitboard* b1, const Bitboard* b2);

inline extern int  __get_bit_at(const Bitboard* b, unsigned int index); // 0 if bit 0 1 othewises
inline extern void break_down_bitboard(const Bitboard* b, unsigned char* buffer, unsigned int * len);
inline extern void __populate_bitboard(Bitboard* b, unsigned char* squares, unsigned int len);

struct byte_bit_pos_list {
	unsigned char pos[8];
	unsigned char len;
};
typedef struct byte_bit_pos_list byte_bit_pos_list;
extern byte_bit_pos_list bit_poses[256];

extern void init_bitboard();  
extern void __init_bit_poses();
extern void __be_bit_scanner(unsigned char * src, unsigned char * bits_found , unsigned int * bit_found_count, unsigned int src_size, unsigned char bit_off);
extern void __se_bit_scanner(unsigned char* src, unsigned char* bits_found, unsigned int * bit_found_count, unsigned int src_size, unsigned char bit_off);

static int __is_be_endian();
extern void (*__bit_scanner)(unsigned char*, unsigned char*, unsigned int*, unsigned int, unsigned char);

const static Bitboard LeftBand  =  {0x1004010040100401ull,		 0x0000001004010040ull};
const static Bitboard RightBand =  {0x1004010040100401ull * 512, 0x0000001004010040ull * 512 + 32};
const static Bitboard UpperBand =  {0x00000000000003ffull, 0ull};
const static Bitboard LowerBand =  {0ull, 0x00000000000003ffull << 26ull };
const static Bitboard Lakes		=  {0x330CC0000000000ull, 0ull};