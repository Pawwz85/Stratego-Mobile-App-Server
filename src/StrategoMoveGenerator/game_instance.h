
#ifndef _GAME_INSTANCE_H_
#define _GAME_INSTANCE_H_
#include "bitboards.h"
//#include <Python.h>

/*
	We must to support execute_move() command while also keeping as much calculations in c.
	This means, we want to avoid storing game_state in python module as much as possible
*/

enum piece_type {
	flag,
	spy,
	scout,
	miner,
	soldier4,
	soldier5,
	soldier6,
	soldier7,
	soldier8,
	soldier9,
	marschall,
	bomb
};


struct piece {
	piece_type type;
	unsigned int discovered;
	unsigned int color;
	unsigned int exist;
};

struct move {
	unsigned char from_;
	unsigned char to_;
};

struct strategoInstance {
	struct piece pieces[100];
	Bitboard all_red;
	Bitboard all_blue;
	Bitboard lakes;
	Bitboard scouts; 
	Bitboard movable;
};
typedef struct strategoInstance StrategoInstance;

#endif