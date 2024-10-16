#include "pch.h"
#include "boot.h"
#include "stdlib.h"
#include "time.h"
#include "fast_magic_boot.h"

#ifdef _WIN32
#ifdef STRATEGODLL_EXPORTS
#define STRATEGO_MOVE_GEN_API __declspec(dllexport)
#else
#define STRATEGO_MOVE_GEN_API 
#endif
#else
#define STRATEGO_MOVE_GEN_API 
#endif // 

void boot()
{
	if (pre_init) {
		srand(time(0));
		init_bitboard();
		if(!fast_magic_bitboard_init())
			init_magic_bitboards();
		pre_init = 0;
	}

}

#undef STRATEGO_MOVE_GEN_API
