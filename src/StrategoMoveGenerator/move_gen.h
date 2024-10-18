#pragma once
#include "game_instance.h"
#include "LUT_optimizer.h"
#include "stdlib.h"
#include "logging.h"
typedef struct move move;

unsigned long long rand_u64();

struct magic {
	Bitboard* lookup_table; // pointer to look up table of an attack mask 
	Bitboard relevancy_mask;
	Bitboard magic_number;
	unsigned int bits;
};

typedef struct magic Magic;

int extern  __verify_magic_numbers(Magic* m, unsigned int sq_index);
int extern __bruteforce_magic_number(Magic* magic, unsigned int target_key_bits, unsigned int sq_index, unsigned int tries_count); // returns 1 if magic number was found, 0 otherwise

// generates the scout attacks for given sq and blocker board using the ray technique, this is pretty much unefficient but it is used to pregenerate lookup tables
void extern __generate_scout_attacks(Bitboard* res, const Bitboard * blockers, unsigned int sq_id); 
void extern __generate_scout_moves(StrategoInstance* instance, const Bitboard* us, const Bitboard* enemy, const Bitboard* blockers, move* move_list, unsigned int* count);
void extern inline __generate_horizontal_moves_for_no_scouts(Bitboard* res, const Bitboard* us_no_scout, const Bitboard* movable, const Bitboard* band, void (*__shift)(Bitboard*, const Bitboard*, unsigned char));
void extern inline __generate_vertical_moves_for_no_scouts(Bitboard* res, const Bitboard* us_no_scout, const Bitboard* movable, const Bitboard* band, void (*__shift)(Bitboard*, const Bitboard*, unsigned char));
void extern inline scan_moves_from_bitboard_with_const_offset(const Bitboard* b,  move* move_list, unsigned int* move_c, char off);
void extern inline scan_moves_from_bitboard(const Bitboard* b, move* move_list, unsigned int* move_c, unsigned char origin);
void __generate_moves_for_no_scouts(StrategoInstance* instance, const Bitboard* us, const Bitboard* enemy, move* move_list, unsigned int* count);

void extern generate_moves(StrategoInstance* instance, move* move_list, unsigned int* count, bool is_red);


inline static void generate_moves_for_red(StrategoInstance* instance, move* move_list, unsigned int* count)
{


	__generate_moves_for_no_scouts(instance, &instance->all_red, &instance->all_blue, move_list, count);

	Bitboard blockers;
	__or(&blockers, &instance->all_blue, &instance->all_red);

	__or(&blockers, &blockers, &Lakes);
	__generate_scout_moves(instance, &instance->all_red, &instance->all_blue, &blockers, move_list, count);
}


inline static void generate_moves_for_blue(StrategoInstance* instance, move* move_list, unsigned int* count)
{

	__generate_moves_for_no_scouts(instance, &instance->all_blue, &instance->all_red, move_list, count);

	Bitboard blockers;
	__or(&blockers, &instance->all_blue, &instance->all_red);
	__or(&blockers, &blockers, &Lakes);

	__generate_scout_moves(instance, &instance->all_blue, &instance->all_red, &blockers, move_list, count);
}


extern Bitboard scout_attack_masks[100];
extern Magic magic_bitboards[100];
extern bool __after_LUT_optimization;
extern Bitboard* magic_lookup_tables; // variable initialized during LUT optimization
extern bool __post_magic_init;
extern void __dealoc_magic_lookup_tables();

static bool check_magic_flag(const Bitboard& b);
static unsigned long long __optimize_LUTs();
extern void __init_scout_attack_masks();
extern void __init_relevant_sqaures_for_magic_scout_gen();
extern void __clear_magic_not_garbage_flag();
extern void init_magic_bitboards(); // call this function AFTER init_bitboard() call