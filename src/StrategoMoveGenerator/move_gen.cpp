#include "pch.h"
#include "move_gen.h"
#include "game_instance.h"
#include "logging.h"
#include <stdio.h>

Bitboard scout_attack_masks[100];
Magic magic_bitboards[100];
bool __after_LUT_optimization = false;
Bitboard* magic_lookup_tables = nullptr; // variable initialized during LUT optimization
bool __post_magic_init = false;

unsigned long long rand_u64()
{
	unsigned long long result = 0ull;
	for (unsigned int i = 0; i < 64; i += sizeof(int)) {
		result <<= sizeof(int);
		result |= rand();
	}
	return result;
}

int __verify_magic_numbers(Magic* m, unsigned int sq_index)
{
	// Verifies if given magic assigns different index for 
	Bitboard t_minus_one;
	Bitboard t, attack_mask;
	__assign(&t, &m->relevancy_mask);

	for (unsigned int i = 0; i <( 1ull << m->bits); ++i) {
		m->lookup_table[i].high &= ~(1ull << 47);
	}
		
		
	unsigned long long index;

	while (t.low || t.high) {
		index = (m->magic_number.high * t.high ^ m->magic_number.low * t.low) >> (64ull - m->bits);
		__generate_scout_attacks(&attack_mask, &t, sq_index); 
		if (m->lookup_table[index].high & (1ull << 47)){
			// Collision! Now we must check if stored attack mask for this position is identical from one generated from "t"
			

			if (attack_mask.low != m->lookup_table[index].low || attack_mask.high != (m->lookup_table[index].high ^(1ull << 47) )) {
				return 0; // test failed
			}
			
		}
		__assign(m->lookup_table + index, &attack_mask); // copy attack mask to calculated index		
		m->lookup_table[index].high |= 1ull << 47;

		__dec(&t_minus_one, &t);
		__and(&t, &t_minus_one, &m->relevancy_mask);
	} 

	__generate_scout_attacks(&attack_mask, &t, sq_index);
	if (m->lookup_table[0].high & (1ull << 47)) // index 0 is for empty board, which misses the test in while loop above
	{
		return 0; // test failed
	}
	__assign(m->lookup_table, &attack_mask); // copy attack mask to calculated index		
	m->lookup_table[0].high |= 1ull << 47;

	return 1; // test succesfull

}


int __bruteforce_magic_number(Magic* magic, unsigned int target_key_bits, unsigned int sq_index, unsigned int tries_count)
{
	if (magic->lookup_table) {
		free(magic->lookup_table);
		magic->lookup_table = 0;	
	}
	magic->lookup_table = (Bitboard*) malloc((1ull << target_key_bits) * sizeof(Bitboard) );
	magic->bits = target_key_bits;
	int result = 0;
	unsigned int counter = 0;
	do {
		magic->magic_number.high = rand_u64(); 
		magic->magic_number.low = rand_u64(); 
	} while (!(result = __verify_magic_numbers(magic, sq_index)) && counter++ != tries_count);
	
	return result;
}


/*
	This procedure generates a bitboard containg all pieces that are not scout that can move in given horizontal direction.
*/
inline void __generate_horizontal_moves_for_no_scouts(Bitboard* res, const Bitboard* us_no_scout, const Bitboard* movable_target, const Bitboard* band, void(*__shift)(Bitboard*, const Bitboard*, unsigned char))
{
	Bitboard t = { 0,0 };
	__negate(&t, band);
	
	__shift(res, movable_target, 1);
	__and(res, res, us_no_scout);
	__and(res, res, &t);
}

inline void __generate_vertical_moves_for_no_scouts(Bitboard* res, const Bitboard* us_no_scout, const Bitboard* movable, const Bitboard* band, void(*__shift)(Bitboard*, const Bitboard*, unsigned char))
{
	Bitboard t = { 0,0 };

	__negate(&t, band);
	__shift(res, movable, 10);
	__and(res, res, us_no_scout);
	__and(res, res, &t);
}

/*
	Scans given bitboard array and for every bits appends move_list array with a move with move by constant offset
*/
inline void scan_moves_from_bitboard_with_const_offset(const Bitboard* b, move* move_list, unsigned int* move_c, char off)
{
	unsigned char bits[128];
	unsigned int len = 0;
	break_down_bitboard(b, bits, &len);

	for (unsigned int i = 0; i < len; ++i) {
		move_list[*move_c].from_ = bits[i];
		move_list[*move_c].to_ = bits[i] + off;

		(*move_c)++;
	}
}

inline void scan_moves_from_bitboard(const Bitboard* b, move* move_list, unsigned int* move_c, unsigned char origin)
{
	unsigned char buff[128];
	unsigned int buff_len = 0;
	break_down_bitboard(b, buff, &buff_len);
	for (unsigned int i = 0; i < buff_len; ++i) {
		move_list[*move_c].from_ = origin;
		move_list[*move_c].to_   = buff[i];
		(*move_c)++;
	}
	
}

void __generate_moves_for_no_scouts(StrategoInstance* instance, const Bitboard* us, const Bitboard* enemy, move* move_list, unsigned int* count) {

	Bitboard movable_target = { 0, 0 };
	__or(&movable_target, &Lakes, us);
	__negate(&movable_target, &movable_target);

	Bitboard t = { 0,0 };
	Bitboard t2 = { 0,0 };
	Bitboard us_not_scout;

	__negate(&us_not_scout, &instance->scouts);
	__and(&us_not_scout, &us_not_scout, us);
	__and(&us_not_scout, &us_not_scout, &instance->movable); // Ged rid of bombs and flags

	__generate_horizontal_moves_for_no_scouts(&t, &us_not_scout, &movable_target, &LeftBand, __lshift);
	__generate_horizontal_moves_for_no_scouts(&t2, &us_not_scout, &movable_target, &RightBand, __rshift);
	scan_moves_from_bitboard_with_const_offset(&t, move_list, count, -1);
	scan_moves_from_bitboard_with_const_offset(&t2, move_list, count, 1);

	__generate_vertical_moves_for_no_scouts(&t, &us_not_scout, &movable_target, &UpperBand, __lshift);
	__generate_vertical_moves_for_no_scouts(&t2, &us_not_scout, &movable_target, &LowerBand, __rshift);
	scan_moves_from_bitboard_with_const_offset(&t, move_list, count, -10);
	scan_moves_from_bitboard_with_const_offset(&t2, move_list, count, 10);
}

void generate_moves(StrategoInstance* instance, move* move_list, unsigned int* count, bool is_red)
{
	*count = 0;
	if (is_red)
		generate_moves_for_red(instance, move_list, count);
	else
		generate_moves_for_blue(instance, move_list, count);

}

void __dealoc_magic_lookup_tables()
{
	if (!__after_LUT_optimization) {
		for (unsigned int i = 0; i < 100; ++i) {
			auto magic = magic_bitboards + i;
			if (magic->lookup_table) {
				free(magic->lookup_table);
				magic->lookup_table = 0;
			}
				
		}
	}else
		delete[] magic_lookup_tables;

	for (unsigned int i = 0; i < 100; ++i) {
		auto magic = magic_bitboards + i;
		magic->lookup_table = 0;
	}

}

bool check_magic_flag(const Bitboard& b)
{
	return (b.high & (1ull << 47)) == 0;
}

unsigned long long __optimize_LUTs()
{
	fixed_arr<__LUT<Bitboard>> luts(100);
	for (size_t i = 0; i < 100; ++i) {
		__LUT<Bitboard> l;
		l.data = fixed_arr<Bitboard>(magic_bitboards[i].lookup_table, (1ull << magic_bitboards[i].bits));
		l.isGarbage = check_magic_flag;
		luts[i] = l;
	}
	__dealoc_magic_lookup_tables(); 
	LUT_opt_result<Bitboard> opt_res = LUT_opt(luts);
	magic_lookup_tables = opt_res.LUT.c_array();

	for (size_t i = 0; i < 100; ++i) {
		magic_bitboards[i].lookup_table = magic_lookup_tables + opt_res.offsets[i];
	}

	__after_LUT_optimization = true;
	return  opt_res.LUT.get_size() * sizeof(Bitboard);

}

void __init_scout_attack_masks()
{
	int lakes_sq[8] = { 42, 43, 46, 47, 52, 53, 56, 57 };
	int dirs[4] = { -10, -1, 1, 10 };
	unsigned char sq_buff[20] = { 0 };
	unsigned int sq_count;

	// Calculate attack masks for each square on empty boards
	for (int i = 0; i < 100; ++i) {
		sq_count = 0;

		for (unsigned int j = 0; j < 4; ++j) {
			int sq_index = i + dirs[j];
			while (sq_index >= 0 && sq_index < 100) {

				if (dirs[j] == -1 && sq_index % 10 == 9)
					goto AFTER_WHILE_LOOP;

				if (dirs[j] == 1 && sq_index % 10 == 0)
					goto AFTER_WHILE_LOOP;

				// Check if sq_index is pointing to the lake
				for (unsigned k = 0; k < 8; ++k) 
					if (sq_index == lakes_sq[k]) 
						goto AFTER_WHILE_LOOP; 

				sq_buff[sq_count++] = sq_index;
				sq_index += dirs[j];

			
			};
		AFTER_WHILE_LOOP:;
		}
		__populate_bitboard(scout_attack_masks + i, sq_buff, sq_count);
	}

	// No scout ever should eve be on the lake, so clear those squares
	for (unsigned k = 0; k < 8; ++k) {
		scout_attack_masks[lakes_sq[k]].low = 0;
		scout_attack_masks[lakes_sq[k]].high = 0;
	}

}

void __init_relevant_sqaures_for_magic_scout_gen()
{
	/*
		Relevant squares of sq (x, y) are defined as follows:
		- We call point P(x1, x2) relevant to sq if and only if:
		  1. blocker placed on point P would intersect any of rays emited by sq on otherwise empty board
		  2. blocker is not placed on the farthest square belonging to such ray
	*/

	int lakes_sq[8] = { 42, 43, 46, 47, 52, 53, 56, 57 };
	int dirs[4] = { -10, -1, 1, 10 };
	unsigned char sq_buff[20] = { 0 };
	unsigned int sq_count;
	int ray_not_empty;

	// Calculate attack masks for each square on empty boards
	for (int i = 0; i < 100; ++i) {
		sq_count = 0;

		for (unsigned int j = 0; j < 4; ++j) {
			int sq_index = i + dirs[j];
			ray_not_empty = 0;
			while (sq_index >= 0 && sq_index < 100) {

				if (dirs[j] == -1 && sq_index % 10 == 9)
					goto AFTER_WHILE_LOOP;

				if (dirs[j] == 1 && sq_index % 10 == 0)
					goto AFTER_WHILE_LOOP;

				// Check if sq_index is pointing to the lake
				for (unsigned k = 0; k < 8; ++k) if (sq_index == lakes_sq[k]) goto AFTER_WHILE_LOOP;
				ray_not_empty = 1;
				sq_buff[sq_count++] = sq_index;
				sq_index += dirs[j];

			};

			AFTER_WHILE_LOOP:;
			if (ray_not_empty)
				--sq_count; // remove a square from the edge of the ray

		}
		__populate_bitboard(&magic_bitboards[i].relevancy_mask, sq_buff, sq_count);
	}

	// No scout ever should ever be on the lake, so clear those squares
	for (unsigned k = 0; k < 8; ++k) {
		magic_bitboards[lakes_sq[k]].relevancy_mask.low = 0;
		magic_bitboards[lakes_sq[k]].relevancy_mask.high = 0;
	}

}

void __clear_magic_not_garbage_flag()
{
	for (unsigned int i = 0; i < 100; ++i) {
		for (unsigned long long index = 0ull; index < 1ull << magic_bitboards[i].bits; ++index)
			magic_bitboards[i].lookup_table[index].high &= ~(1ull << 47);
	}
}

void __generate_scout_attacks(Bitboard* res, const Bitboard* blockers, unsigned int sq_id)
{
	int lakes_sq[8] = { 42, 43, 46, 47, 52, 53, 56, 57 };
	int dirs[4] = { -10, -1, 1, 10 };
	unsigned char sq_buff[20] = { 0 };
	unsigned int sq_count = 0;
	int sq_index;
	for (unsigned int j = 0; j < 4; ++j) {
		sq_index = int(sq_id) + dirs[j];

		while (sq_index >= 0 && sq_index < 100) {
			
			if ((dirs[j] == -1) && (sq_index % 10 == 9))
				goto AFTER_WHILE_LOOP;

			if ((dirs[j] == 1) && (sq_index % 10 == 0))
				goto AFTER_WHILE_LOOP;

			// Check if sq_index is pointing to the lake
			if (__get_bit_at(&Lakes, sq_index))
				goto AFTER_WHILE_LOOP;

			// check if sq_index points to blocked square
			if (__get_bit_at(blockers, sq_index)) {
				sq_buff[sq_count++] = sq_index;
				goto AFTER_WHILE_LOOP;
			}
				

			sq_buff[sq_count++] = sq_index;

			sq_index += dirs[j];

		};
	AFTER_WHILE_LOOP:;
	}

	__populate_bitboard(res, sq_buff, sq_count);

}

void extern __generate_scout_moves(StrategoInstance* instance, const Bitboard* us, const Bitboard* enemy, const Bitboard* blockers, move* move_list, unsigned int* count)
{
	Bitboard t;
	unsigned char buff[128];
	unsigned int scout_count = 0;
	__and(&t, us, &instance->scouts);
	Magic* m;
	size_t index;
	break_down_bitboard(&t, buff, &scout_count);
	for (unsigned int i = 0; i < scout_count; ++i)
	{
		m = magic_bitboards + buff[i];
		__and(&t, blockers, &m->relevancy_mask);
		index = (t.high * m->magic_number.high) ^ (t.low * m->magic_number.low);
		index >>= 64 - m->bits;
		__negate(&t, us);
		__and(&t, &t, m->lookup_table + index);
		scan_moves_from_bitboard(&t, move_list, count, buff[i]);
	}

}

void init_magic_bitboards()
{ 
	__init_scout_attack_masks();
	__init_relevant_sqaures_for_magic_scout_gen();
	__dealoc_magic_lookup_tables();

	printf("Generating magic numbers\n");
	unsigned int is_found;
	for (unsigned int i = 0; i < 100; ++i) {
		magic_bitboards[i].lookup_table = 0; // initialize look up tables with null
		is_found = 0;
		for (unsigned int j = 6; j <= 20; ++j) {
			for (unsigned int k = 0; k < 1ull << (j - 6); ++k) // double tries count with each bit in an index
				if (is_found = __bruteforce_magic_number(magic_bitboards + i, j, i, 50)) {
					printf("square %d - %d bits\n", i + 1, j);
					goto NEXT_MAGIC;
				}
				
		};

		if (!is_found) {
			printf("Failed to find magic for square %d\n", i);
		}
	NEXT_MAGIC:;
		
	}
	
	
	unsigned long long size_counter = 0;


	for (size_t i = 0; i < 100; ++i) {
		size_counter += (1ull << magic_bitboards[i].bits) * sizeof(Bitboard);
	}

	printf("Magic look tables weight %llu bytes.", size_counter);

	printf("Optimizing Lookup table..");
	size_counter =  __optimize_LUTs();
	printf("Lookup table was optimized");
	printf("Magic look tables weight %llu bytes.", size_counter);
	__clear_magic_not_garbage_flag();
	__post_magic_init = true;
}
