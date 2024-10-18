#include "pch.h"
#include "StrategoMoveGen.h"
#include "boot.h"

#ifdef _WIN32
	#ifdef STRATEGODLL_EXPORTS
	#define STRATEGO_MOVE_GEN_API __declspec(dllexport)
	#else
	#define STRATEGO_MOVE_GEN_API 
#endif
#else
#define STRATEGO_MOVE_GEN_API 
#endif // 
;
extern "C" STRATEGO_MOVE_GEN_API void init()
{
	boot();
}

#undef STRATEGO_MOVE_GEN_API
