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


