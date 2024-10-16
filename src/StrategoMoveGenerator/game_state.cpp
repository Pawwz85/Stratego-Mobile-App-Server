#include "pch.h"
#include "game_state.h"
#include "bitboards.h"
#include <memory>
#include <cstring>

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

#define BITBOARD_RESET(BITBOARD)  BITBOARD.low = 0; BITBOARD.high = 0;
#define BITBOARD_SET_LOW_BIT(BITBOARD, sq_id) BITBOARD.low |= (1ull<<sq_id);
#define BITBOARD_SET_HIGH_BIT(BITBOARD, sq_id) BITBOARD.high |= (1ull<<sq_id);
void game_state::game_state_set_state(piece* pieces, bool is_red_to_move)
{
	this->is_red_to_move = is_red_to_move;
	this->is_blue_flag_captured = this->is_red_flag_captured = true;
	std::memcpy(this->instance.pieces, pieces, 100 * sizeof(piece));
	BITBOARD_RESET(this->instance.all_blue);
	BITBOARD_RESET(this->instance.all_red);
	BITBOARD_RESET(this->instance.movable);
	BITBOARD_RESET(this->instance.scouts);
	
	piece p;

	// initialize bitboards using provided data
	for (unsigned int i = 0; i < 64; ++i) {
		p = this->instance.pieces[i];
		if (!p.exist) {
			continue; // piece do not exist
		}

		if (p.color)
			BITBOARD_SET_LOW_BIT(this->instance.all_red, i)
		else
			BITBOARD_SET_LOW_BIT(this->instance.all_blue, i)

		if (p.type == piece_type::scout)
			BITBOARD_SET_LOW_BIT(this->instance.scouts, i)

		if (!(p.type == piece_type::bomb || p.type == piece_type::flag))
			BITBOARD_SET_LOW_BIT(this->instance.movable, i);

		if (p.type == flag) {
			if (p.color) this->is_red_flag_captured = false; else this->is_blue_flag_captured = false;
		}

	}

	// Populate upper part of our bitboards
	for(unsigned int i = 0; i<36; ++i) {
		p = this->instance.pieces[i + 64];
		if (!p.exist) {
			continue; // piece do not exist
		}

		if (p.color)
			BITBOARD_SET_HIGH_BIT(this->instance.all_red, i)
		else
			BITBOARD_SET_HIGH_BIT(this->instance.all_blue, i)

		if (p.type == piece_type::scout)
			BITBOARD_SET_HIGH_BIT(this->instance.scouts, i)

		if (!(p.type == piece_type::bomb || p.type == piece_type::flag))
			BITBOARD_SET_HIGH_BIT(this->instance.movable, i);
	}


}

void game_state::game_state_make_move(const move& m)
{

	piece winner = this->who_would_win(this->instance.pieces[m.from_], this->instance.pieces[m.to_]);

	// Step 2. despawn old pieces to update book keeping
	despawn(m.from_);
	despawn(m.to_);
	spawn(winner, m.to_);


}

void game_state::move_gen(move* buff, unsigned int& move_c)
{
	generate_moves(&this->instance, buff, &move_c, this->is_red_to_move);
}

bool game_state::get_side() const
{
	return this->is_red_to_move;
}


void game_state::despawn(unsigned char sq_id)
{
	this->instance.pieces[sq_id].exist = false;

	bitboard clr_mask;
	clr_mask.high = 0;
	clr_mask.low = 1;
	__lshift(&clr_mask, &clr_mask, sq_id);
	__negate(&clr_mask, &clr_mask);

	__and(&this->instance.movable,  &this->instance.movable,  &clr_mask);
	__and(&this->instance.all_blue, &this->instance.all_blue, &clr_mask);
	__and(&this->instance.all_red,  &this->instance.all_red,  &clr_mask);
	__and(&this->instance.scouts,   &this->instance.scouts,   &clr_mask);

	if (this->instance.pieces[sq_id].type == piece_type::flag) {
		if (this->instance.pieces[sq_id].color)
			this->is_red_flag_captured = true;
		else
			this->is_blue_flag_captured = true;
	}

}

void game_state::spawn(const piece& p, unsigned char sq_id)
{
	this->instance.pieces[sq_id] = p;

	if (!p.exist) 
		return;

	bitboard set_mask;
	set_mask.high = 0;
	set_mask.low = 1;
	__lshift(&set_mask, &set_mask, sq_id);

	if (p.type != piece_type::flag && p.type != piece_type::bomb) 
		__or(&this->instance.movable, &this->instance.movable, &set_mask);
	
	if (p.color)
		__or(&this->instance.all_red, &this->instance.all_red, &set_mask);
	else
		__or(&this->instance.all_blue, &this->instance.all_blue, &set_mask);

	if (p.type == piece_type::scout)
		__or(&this->instance.scouts, &this->instance.scouts, &set_mask);

	if (this->instance.pieces[sq_id].type == piece_type::flag) {
		if (this->instance.pieces[sq_id].color)
			this->is_red_flag_captured = false;
		else
			this->is_blue_flag_captured = false;
	}
}

piece game_state::who_would_win(piece& attacker, piece& defender)
{
	if (!defender.exist)
		return attacker;

	//special attack privileges: 1. Miner vs bomb 2. spy vs marchall

	if ((attacker.type == piece_type::miner && defender.type == piece_type::bomb)		||
		(attacker.type == piece_type::spy   && defender.type == piece_type::marschall))
		return attacker;

	// special case: equal force attack equal force

	if (attacker.type == defender.type) {
		piece p;
		p.exist = false;
		return p;
	 }

	// general case,  piece higher in hierarchy wins

	return (attacker.type > defender.type) ? attacker : defender;
}

game_state::game_state()
{
	this->is_red_to_move = false;
	BITBOARD_RESET(this->instance.all_blue);
	BITBOARD_RESET(this->instance.all_red);
	BITBOARD_RESET(this->instance.movable);
	BITBOARD_RESET(this->instance.scouts);
	this->is_blue_flag_captured = this->is_red_flag_captured = true;
	for (unsigned int i = 0; i < 100; ++i)
		this->instance.pieces[i].exist = false;
}

#undef BITBOARD_SET_LOW_BIT
#undef BITBOARD_SET_HIGH_BIT
#undef BITBOARD_RESETOARD_RESET


piece who_would_win(piece& attacker, piece& defender)
{
	if (!defender.exist)
		return attacker;

	//special attack privileges: 1. Miner vs bomb 2. spy vs marchall

	if ((attacker.type == piece_type::miner && defender.type == piece_type::bomb) ||
		(attacker.type == piece_type::spy && defender.type == piece_type::marschall))
		return attacker;

	// special case: equal force attack equal force

	if (attacker.type == defender.type) {
		piece p;
		p.exist = false;
		return p;
	}

	// general case,  piece higher in hierarchy wins

	return (attacker.type > defender.type) ? attacker : defender;
}

int despawn(GameState* state, const unsigned char& sq_id)
{
	if (sq_id >= 100)
		return -1;
	if (!state->instance.pieces[sq_id].exist)
		return 1;
	
	state->instance.pieces[sq_id].exist = 0;
	
	bitboard clr_mask;
	clr_mask.high = 0;
	clr_mask.low = 1;
	__lshift(&clr_mask, &clr_mask, sq_id);
	__negate(&clr_mask, &clr_mask);

	__and(&state->instance.movable, &state->instance.movable, &clr_mask);
	__and(&state->instance.all_blue, &state->instance.all_blue, &clr_mask);
	__and(&state->instance.all_red, &state->instance.all_red, &clr_mask);
	__and(&state->instance.scouts, &state->instance.scouts, &clr_mask);

	if (state->instance.pieces[sq_id].type == piece_type::flag) {
		if (state->instance.pieces[sq_id].color)
			state->trackers.red_flag -= 1;
		else
			state->trackers.blue_flag -= 1;
	}

	return 1;
}

int spawn(GameState* state, const piece* p, const unsigned char& sq_id)
{

	if (state->instance.pieces[sq_id].exist || sq_id >= 100)
		return -1;

	state->instance.pieces[sq_id] = *p;

	if (!p->exist)
		return 1;

	bitboard set_mask = { 1ull, 0ull };
	__lshift(&set_mask, &set_mask, sq_id);

	if (p->type != piece_type::flag && p->type != piece_type::bomb)
		__or(&state->instance.movable, &state->instance.movable, &set_mask);

	if (p->color)
		__or(&state->instance.all_red, &state->instance.all_red, &set_mask);
	else
		__or(&state->instance.all_blue, &state->instance.all_blue, &set_mask);

	if (p->type == piece_type::scout)
		__or(&state->instance.scouts, &state->instance.scouts, &set_mask);

	if (state->instance.pieces[sq_id].type == piece_type::flag) {
		if (state->instance.pieces[sq_id].color)
			state->trackers.red_flag += 1;
		else
			state->trackers.blue_flag += 1;
	}

	return 1;
}

STRATEGO_MOVE_GEN_API int game_state_set_state(const void * handle, piece* pieces, Side  side)
{
	GameState* state = (GameState*)handle;

	switch (side)
	{
	case red_player:
	case blue_player:
	case none: break;
	default:
		return 0;
	};

	for (unsigned char i = 0; i < 100; ++i) {
			despawn(state, i);
			spawn(state, pieces + i, i);
	}
	
	state->player_to_move = side;
	return 1;
}

STRATEGO_MOVE_GEN_API int game_state_make_move(const void * handle, const move* m)
{
	GameState* state = (GameState*)handle;
	piece winner = who_would_win(state->instance.pieces[m->from_], state->instance.pieces[m->to_]);

	// Step 2. despawn old pieces to update book keeping
	despawn(state, m->from_);
	despawn(state, m->to_);
	spawn(state, &winner, m->to_);


	// TODO: check player turn or smth
	
	state->trackers.gen_called_flag = 0;
	return 1;
}

STRATEGO_MOVE_GEN_API const void* game_state_alloc()
{
	// aloccation
	GameState* result = new GameState;
	
	// Initialization
	result->instance.all_blue = result->instance.all_red = result->instance.movable = result->instance.scouts = { 0ull , 0ull };
	result->instance.lakes = Lakes; 
	
	for (int i = 0; i < 100; ++i)
		result->instance.pieces[i].exist = false;

	result->move_buffer.size = 0;
	result->player_to_move = none;

	result->trackers.blue_flag = result->trackers.red_flag = 0;
	result->trackers.gen_called_flag = false;
	return result;
}

STRATEGO_MOVE_GEN_API int game_state_is_move_legal(const void* gamestate_handle, const move* m)
 {
	 unsigned int move_c;
	 const move* move_buff = game_state_get_move_buffer(gamestate_handle, &move_c);
	
	 DEBUG_PRINTLN("Move_c: " << move_c);
	 DEBUG_PRINT("[ ");



	 for (unsigned i = 0; i < move_c; ++i) {
		 DEBUG_PRINT("("<< (int)move_buff[i].from_ << ", "<< (int)move_buff[i].to_ << " ), ")
		 if (m->from_ == move_buff[i].from_ && m->to_ == move_buff[i].to_)
			 return 1;
	 }
	DEBUG_PRINT("]\n")

	 return 0;
 }

STRATEGO_MOVE_GEN_API void game_state_dealloc(const void* handle)
{
	GameState* state = (GameState*)handle;
	delete state;
}

STRATEGO_MOVE_GEN_API const piece* game_state_get_piece(const void* gamestate_handle, unsigned int square_id)
{
	GameState* state = (GameState*)gamestate_handle;
	return (square_id >= 100)? NULL : state->instance.pieces + square_id;
}

STRATEGO_MOVE_GEN_API const move* game_state_get_move_buffer(const void* gamestate_handle, unsigned int* size)
{
	GameState* state = (GameState*)gamestate_handle;
	
	if (state->player_to_move != none && !state->trackers.gen_called_flag) {
		state->move_buffer.size = 0;
		state->trackers.gen_called_flag = true;

		generate_moves(&state->instance, state->move_buffer.moves, &state->move_buffer.size, state->player_to_move == red_player);
	} else if (state->player_to_move == none)
		state->move_buffer.size = 0;

	*size = state->move_buffer.size;
	return state->move_buffer.moves;
}

STRATEGO_MOVE_GEN_API const move* get_move(const void* buffer_handle, unsigned int i)
{
	MoveBuffer* buffer = (MoveBuffer*)buffer_handle;
	return (i<buffer->size )?buffer->moves + i: nullptr;
}

STRATEGO_MOVE_GEN_API Side get_winner(const void* gamestate_handle)
{
	GameState* state = (GameState*)gamestate_handle;
	if (state->player_to_move == none)
		return none;

	if (state->trackers.red_flag > state->trackers.blue_flag)
		return red_player;

	if (state->trackers.red_flag < state->trackers.blue_flag)
		return blue_player;

	if (!state->trackers.gen_called_flag) {
		state->trackers.gen_called_flag = true;
		generate_moves(&state->instance, state->move_buffer.moves, &state->move_buffer.size, state->player_to_move == red_player);
	}
		
	
	if (state->move_buffer.size == 0) 
		return (state->player_to_move == red_player) ? blue_player : red_player;
	
	return none;
}

STRATEGO_MOVE_GEN_API Side game_state_get_side_to_move(const void* gamestate_handle)
{
	GameState* state = (GameState*)gamestate_handle;
	return state->player_to_move;
}

#undef STRATEGO_MOVE_GEN_API