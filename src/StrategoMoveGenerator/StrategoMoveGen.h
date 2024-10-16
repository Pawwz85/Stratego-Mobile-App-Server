#pragma once
#include "pch.h"

#ifdef _WIN32
	#ifdef STRATEGODLL_EXPORTS
	#define STRATEGO_MOVE_GEN_API __declspec(dllexport)
	#else
	#define STRATEGO_MOVE_GEN_API __declspec(dllimport)
	#endif
#else
#define STRATEGO_MOVE_GEN_API
#endif // 

	




extern "C" STRATEGO_MOVE_GEN_API void init();

#undef STRATEGO_MOVE_GEN_API