#pragma once
#include "pch.h"
#include "move_gen.h"
#include "bitboards.h"
#include <cstdio>
#include <sstream>
#include "fast_magic_boot.h"

extern bitboard fastMagicNumbers[100];
extern unsigned int fastMagicNumbers_bit_count[100];
extern const bool fastMagicNumbers_are_after_LUT;
extern unsigned int fastMagicNumbers_offsets[100];


extern std::string ull_to_hex(unsigned long long x);
extern std::string bitboard_to_string(Bitboard& b);
extern void printMagicNumbersLiteral(std::ostream& out);

int extern fast_magic_bitboard_init();
