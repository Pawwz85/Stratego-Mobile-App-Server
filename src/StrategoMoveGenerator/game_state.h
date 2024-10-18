#pragma once
#include "move_gen.h"
#include "bitboards.h"
#ifdef _WIN32
#ifdef STRATEGODLL_EXPORTS
#define STRATEGO_MOVE_GEN_API __declspec(dllexport)
#else
#define STRATEGO_MOVE_GEN_API __declspec(dllimport)
#endif
#else
#define STRATEGO_MOVE_GEN_API
#endif // 



/*
	Proxy to strategoInstance
*/

//Deprecated
class game_state {
	strategoInstance instance;
	bool is_red_to_move;
	
	bool is_red_flag_captured;
	bool is_blue_flag_captured;
	
	void despawn(unsigned char sq_id);
	void spawn(const piece& p, unsigned char sq_id);
	piece who_would_win(piece& attacker, piece& defender);

public:
	STRATEGO_MOVE_GEN_API game_state();
	STRATEGO_MOVE_GEN_API void game_state_set_state(piece* pieces, bool is_red_to_move); // expects an array of 100 pieces
	STRATEGO_MOVE_GEN_API void game_state_make_move(const move & m); // executes given move11, note no legaility check is performed here
	STRATEGO_MOVE_GEN_API void move_gen(move* buff, unsigned int& move_c);
	STRATEGO_MOVE_GEN_API bool get_side() const;
	STRATEGO_MOVE_GEN_API bool is_any_flag_capt() const { return this->is_blue_flag_captured || this->is_red_flag_captured; };
};

enum Side {
	none,
	red_player,
	blue_player
};

struct GameStateTrackers {
	int red_flag;
	int blue_flag;
	bool gen_called_flag;
};

struct MoveBuffer {
	move moves[256];
	unsigned int size;
};

struct GameState {
	strategoInstance instance;
	GameStateTrackers trackers;
	MoveBuffer move_buffer;
	Side player_to_move;
};


extern int despawn(GameState* state, const unsigned char& sq_id);
extern int spawn(GameState* state, const piece* p,  const unsigned char& sq_id);
extern "C" STRATEGO_MOVE_GEN_API int game_state_set_state(const void * gamestate_handle, piece* pieces, Side side);
extern "C" STRATEGO_MOVE_GEN_API int game_state_make_move(const void * gamestate_handle, const move* m);
extern "C" STRATEGO_MOVE_GEN_API const void* game_state_alloc();
extern "C" STRATEGO_MOVE_GEN_API int game_state_is_move_legal(const void* gamestate_handle, const move* m);
extern "C" STRATEGO_MOVE_GEN_API void game_state_dealloc(const void* gamestate_handle);
extern "C" STRATEGO_MOVE_GEN_API const piece* game_state_get_piece(const void* gamestate_handle, unsigned int square_id); // returns NULL if square_id is not in range
extern "C" STRATEGO_MOVE_GEN_API const move* game_state_get_move_buffer(const void* gamestate_handle, unsigned int * size); // returns handle to move buffer
extern "C" STRATEGO_MOVE_GEN_API Side get_winner(const void* gamestate_handle);
extern "C" STRATEGO_MOVE_GEN_API Side game_state_get_side_to_move(const void* gamestate_handle);