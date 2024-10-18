#include "pch.h"
#include "bitboards.h"
#include "logging.h"

uint64 __n_biggest_bits_mask(unsigned char n) {
	if (n >= 64)
		return 0xffffffffffffffffull;
	unsigned int off = 64 - n;
	uint64 result = (0xffffffffffffffffull >> off) << off;
	return result;
}

uint64 __n_smallest_bits_mask(unsigned char n) {
	if (n >= 64)
		return  0xffffffffffffffffull;
	return (1ull << n) - 1;
}

inline void __assign(Bitboard* b1, const Bitboard* b2)
{
	b1->low = b2->low;
	b1->high = b2->high;
}

inline void __negate(Bitboard* result, const Bitboard* b)
{
	result->low  = ~b->low;
	result->high = ~b->high;
}

inline void __and(Bitboard* result, const Bitboard* b1, const Bitboard* b2)
{
	result->low = b1->low & b2->low;
	result->high = b1->high & b2->high;
}

inline void __or(Bitboard* result, const Bitboard* b1, const Bitboard* b2)
{
	result->low  = b1->low  | b2->low;
	result->high = b1->high | b2->high;
}

inline void __xor(Bitboard* result, const Bitboard* b1, const Bitboard* b2)
{
	result->low  = b1->low  ^ b2->low;
	result->high = b1->high ^ b2->high;
}

inline void __lshift(Bitboard* result, const Bitboard* b, unsigned char off)
{
	if (off == 0) {
		result->low = b->low;
		result->high = b->high;
		return;
	}

	if (off < 64) {
		uint64 carry = b->low & __n_biggest_bits_mask(off); 
		result->low = b->low << off;
		result->high = b->high << off;
		result->high |= carry >> (64 - off);
	}
	else {
		result->high = b->low << (off - 64);
		result->low = 0ull;
	}
	
}

inline void __rshift(Bitboard* result, const Bitboard* b, unsigned char off)
{
	if (off == 0) {
		result->low = b->low;
		result->high = b->high;
		return;
	}

	if (off < 64) {
	uint64 carry = b->high & __n_smallest_bits_mask(off);
	result->low = b->low >> off;
	result->high = b->high >> off;
	result->low |= carry << (64 - off);
	}
	else {
		result->low = b->high >> (off - 64);
		result->high = 0ull;
	}
	
}

inline void __inc(Bitboard* res, Bitboard* src)
{
	if (src->low == 0xffffffffffffffffull) {
		res->high = src->high + 1;
		res->low = 0ull;
	}
	else {
		res->high = src->high;
		res->low = src->low + 1;
	}
}

inline void __dec(Bitboard* res, Bitboard* src)
{
	if (src->low == 0ull) {
		res->high = src->high - 1;
		res->low = 0xffffffffffffffffull;
	}
	else {
		res->high = src->high;
		res->low = src->low - 1;
	}
}

inline void __add(Bitboard* result, const Bitboard* b1, const Bitboard* b2)
{
	uint64 m = b1->low;
	result->low = b1->low + b2->low;
	if (result->low < m)
		result->high = 1 + b1->high + b2->high;
	else
		result->high = b1->high + b2->high;
	
}

inline void __sub(Bitboard* result, const Bitboard* b1, const Bitboard* b2)
{
	uint64 m = b1->low;
	result->high = b1->high - b2->high;
	result->low = b1->low - b2->low;
	if (result->low > m)
		--result->high;
}

inline int __get_bit_at(const Bitboard* b, unsigned int index)
{
	if (index < 64)
		return (b->low & (1ull << index)) ? 1 : 0;
	else
		return (b->high & (1ull << (index - 64))) ? 1 : 0;
}

inline void break_down_bitboard(const Bitboard* b, unsigned char* buffer, unsigned int* len)
{
	__bit_scanner((unsigned char *) & b->low,  buffer, len, sizeof(b->low), 0);
	__bit_scanner((unsigned char *) & b->high, buffer, len, sizeof(b->high), 64);
}

inline extern void __populate_bitboard(Bitboard* b, unsigned char* squares, unsigned int len)
{
	b->low = b->high = 0;
	for (unsigned int i = 0; i < len; ++i) 
		if (squares[i] < 64)
			b->low |= 1ull << squares[i];
		else
			b->high |= 1ull << (squares[i] - 64);
	
}

byte_bit_pos_list bit_poses[256];
void (*__bit_scanner)(unsigned char*, unsigned char*, unsigned int*, unsigned int, unsigned char) = 0;

void init_bitboard()
{
	__bit_scanner = (__is_be_endian()) ? __be_bit_scanner : __se_bit_scanner;
	__init_bit_poses();
}

void __init_bit_poses()
{
	for (unsigned int i = 0; i <= 255; ++i) {
		bit_poses[i].len = 0;
		for (unsigned int j = 0; j < 8; ++j)
			if (i & (1u << j))
				bit_poses[i].pos[bit_poses[i].len++] = j;

	}
}

void __be_bit_scanner(unsigned char* src, unsigned char* bits_found, unsigned int * bit_found_count, unsigned int src_size, unsigned char bit_off)
{
	unsigned char off = (src_size - 1) * 8 + bit_off;
	unsigned char byte;
	for (int i = src_size - 1; i >= 0; --i) {
		byte = *src;
		++src;
		for (unsigned char j = 0; j < bit_poses[byte].len; ++j)
		{
			bits_found[(*bit_found_count)] = bit_poses[byte].pos[j] + off;
			++(*bit_found_count);
		}
		off -= 8;
	}

}
void __se_bit_scanner(unsigned char* src, unsigned char* bits_found, unsigned int* bit_found_count, unsigned int src_size, unsigned char bit_off)
{
	unsigned char off = bit_off;
	unsigned char byte;
	for (unsigned int i = 0; i < src_size; ++i) {
		byte = *src;
		++src;
		for (unsigned char j = 0; j < bit_poses[byte].len; ++j)
		{
			bits_found[(*bit_found_count)] = bit_poses[byte].pos[j] + off;
			++(*bit_found_count);
		}
		off += 8;
	}

}

int __is_be_endian() {
	int n = 1;
	return *(char*)&n == 0;
}


