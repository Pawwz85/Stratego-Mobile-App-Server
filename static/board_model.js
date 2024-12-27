export var PieceType

;(function(PieceType) {
  PieceType[(PieceType["FLAG"] = 0)] = "FLAG"
  PieceType[(PieceType["BOMB"] = 1)] = "BOMB"
  PieceType[(PieceType["SPY"] = 2)] = "SPY"
  PieceType[(PieceType["SCOUT"] = 3)] = "SCOUT"
  PieceType[(PieceType["MINER"] = 4)] = "MINER"
  PieceType[(PieceType["SERGEANT"] = 5)] = "SERGEANT"
  PieceType[(PieceType["LIEUTENANT"] = 6)] = "LIEUTENANT"
  PieceType[(PieceType["CAPTAIN"] = 7)] = "CAPTAIN"
  PieceType[(PieceType["MAJOR"] = 8)] = "MAJOR"
  PieceType[(PieceType["COLONEL"] = 9)] = "COLONEL"
  PieceType[(PieceType["GENERAL"] = 10)] = "GENERAL"
  PieceType[(PieceType["MARSHAL"] = 11)] = "MARSHAL"
  PieceType[(PieceType["UNKNOWN"] = 12)] = "UNKNOWN"
})(PieceType || (PieceType = {}))

export var Color = {
  RED: "red",
  BLUE: "blue"
}

export class Piece {
  constructor(color, type_) {
    this.color = color
    this.type = type_
  }

  copy() {
    return new Piece(this.color, this.type)
  }
}

export class Square {
  constructor() {
    this.index = 0
    this.piece = null
    this.draw_dot = false
    this.highlight = false
  }

  copy() {
    let clone = new Square()
    clone.index = this.index
    clone.draw_dot = this.draw_dot
    clone.highlight = this.highlight
    if (this.piece != null) clone.piece = this.piece.copy()
    return clone
  }
}

export class BoardStateHiglightMask{
  constructor(state){
    this.__state = state;
    this.last_move = null;
  }

  __apply(){
    for (let i = 0; i < 100; ++i) 
      this.__state.squares[i].highlight = false;

    if (this.last_move) {

      this.__state.squares[this.last_move.from].highlight = true;
      this.__state.squares[this.last_move.to].highlight = true;
    }

    this.__state.notify_observers();
  }

  set_last_move(move){
    this.last_move = move
    this.__apply();
  }

}

export class BoardState {
  constructor() {
    this.squares = new Array(100);
    this.observers = [];
    this.temporal_observer = null;
    this.highlight_mask_manager = new  BoardStateHiglightMask(this);
    this.reset()
  }

  reset() {
    for (let i = 0; i < 100; ++i) {
      this.squares[i] = new Square()
      this.squares[i].index = i
    }
    this.highlight_mask_manager.__apply();
  }

  notify_observers() {
    for (let i = 0; i < this.observers.length; ++i) {
      this.observers[i].set_state(this)
    }
    this.temporal_observer?.set_state(this);
  }

  set_position(index_piece_pairs) {
    this.reset()
    for (let i = 0; i < index_piece_pairs.length; ++i) {
      let index = index_piece_pairs[i][0]
      let piece = index_piece_pairs[i][1]
      this.squares[index].piece = piece
    }
  
    this.notify_observers()
  }

  // This class allows to sidestep higlight mask manager api
  set_square(sq) {
    this.squares[sq.index] = sq
    this.notify_observers()
  }

  copy() {
    let clone = new BoardState()
    for (let i = 0; i < 100; ++i) clone.squares[i] = this.squares[i].copy()
    return clone
  }
}

export class Move {
  constructor(from_, to_) {
    this.from = from_
    this.to = to_
  }
}

export class MoveGenerator {
  constructor() {
    this.state = null
    this.lake_fields = [42, 43, 46, 47, 52, 53, 56, 57]
  }
  set_state(state_) {
    this.state = state_
  }

  generate_moves_for_piece(sq_id) {
    const piece = this.state?.squares[sq_id].piece

    if (!piece) return []

    const pieceColor = piece.color
    if ([PieceType.BOMB, PieceType.FLAG].includes(piece.type)) return []

    const result = []

    if (piece.type != PieceType.SCOUT) {
      const offsets = [-10, -1, 1, 10]
      const result = []
      for (let off of offsets) {
        let move = new Move(sq_id, sq_id + off)
        if (this.is_move_valid(move))
           result.push(move)
      }
      return result
    } else {
      const offsets = [-10, -1, 1, 10]
      let result = []
      for (let off of offsets)
        for (let i = 1; sq_id + i * off >= 0 && sq_id + i * off < 100; ++i) {
          
          let sq = sq_id + i * off
          if (this.lake_fields.indexOf(sq) != -1) break
      
          let enemy = this.state?.squares[sq].piece ?? null

          if (enemy == null) {
            result.push(new Move(sq_id, sq))
            continue
          }

          if (enemy.color == piece.color) break

     

          result.push(new Move(sq_id, sq))
          break // enemy piece
        }
      return result
    }
    return []
  }

  generate_moves() {
    if (this.state == null) return []
    const result = []

    return result
  }

  is_move_valid(move) {
    if (
      move.from < 0 ||
      move.from > 99 ||
      move.to < 0 ||
      move.to > 99 ||
      this.lake_fields.includes(move.to)
    )
      return false

    const piece = this.state?.squares[move.from].piece ?? null

    if (!piece) return false

    if (piece.type == PieceType.BOMB || piece.type == PieceType.FLAG)
      return false

    if (piece.type != PieceType.SCOUT) {
      const deltaY = Math.abs(
        Math.floor(move.from / 10) - Math.floor(move.to / 10)
      )
      const deltaX = Math.abs((move.from % 10) - (move.to % 10))
      if (deltaX + deltaY != 1) return false

      const enemy = this.state?.squares[move.to].piece ?? null
      return enemy?.color != piece.color
    } else {
      const deltaY = Math.abs(
        Math.floor(move.from / 10) - Math.floor(move.to / 10)
      )
      const deltaX = Math.abs((move.from % 10) - (move.to % 10))

      if (deltaX != 0 && deltaY != 0) return false

      if (deltaX == 0 && deltaY == 0) return false

      let sq = move.from + 10 * deltaY + deltaX
      
      while (sq >= 0 && sq < 100){

        console.log(sq)
        if (this.lake_fields.indexOf(sq) != -1)
          return false;

        let enemy = this.state?.squares[sq].piece ?? null
        if (!enemy) {
          if (sq == move.to) {
            sq += 10 * deltaY + deltaX
            continue
          } else return true
        }

        return sq == move.to && enemy.color != piece.color
      }
    }
    return false
  }
  copy() {
    let clone = new MoveGenerator()
    return clone
  }
}

/*
    Bord Model dedicated for gameplay phase
*/
export class BoardModel {
  constructor(move_gen, state) {
    this.boardstate = state.copy() // we create a copy of a state so we get rid of external dependencies also, it makes BoardModel
    this.move_gen = move_gen.copy() // more customisable, as we can pass different implementation of state or move gen
    this.selected_sq_id = -1 // square selected by player
    this.userColor = null // Color of the user, controlls the bord controller generated by model
    this.submitMove = move => {} // callback used by board controller
  }

  set_selected_square_id(id) {
    if (this.selected_sq_id == id) return;

    this.selected_sq_id = id;
    this.refresh_board_visuals();
  }

  refresh_board_visuals() {
    for (let i = 0; i < this.boardstate.squares.length; ++i) {
      this.boardstate.squares[i].highlight = i == this.selected_sq_id
      this.boardstate.squares[i].draw_dot = false
    }

    if (
      this.selected_sq_id < this.boardstate.squares.length &&
      this.selected_sq_id >= 0
    ) {
      this.move_gen.set_state(this.boardstate);
      const legal_moves = this.move_gen.generate_moves_for_piece(
        this.selected_sq_id
      )

      for (let move of legal_moves)
        this.boardstate.squares[move.to].draw_dot = true
    }

    this.boardstate.notify_observers()
  }
}

export class GameplayBoardController {
  constructor(boardModel) {
    this.boardModel = boardModel
  }

  handle_sq_click(sq) {
    // We clicked already selected square, so we unselect it
    if (sq == this.boardModel.selected_sq_id) {
      this.boardModel.selected_sq_id = -1
      this.boardModel.refresh_board_visuals()
      return
    }

    const square = this.boardModel.boardstate.squares[sq]

    // We clicked dot, so we are submitting move
    if (square.draw_dot) {
      const move = new Move(this.boardModel.selected_sq_id, sq)
      this.boardModel.submitMove(move)
      this.boardModel.selected_sq_id = -1
      this.boardModel.refresh_board_visuals()
      return
    }

    // We clicked our piece, so we select it
    if (square.piece?.color == this.boardModel.userColor) {
      this.boardModel.selected_sq_id = sq
      this.boardModel.refresh_board_visuals()
      return
    }

    // We clicked random sq, unselect previous
    this.boardModel.selected_sq_id = -1
    this.boardModel.refresh_board_visuals()
  }
}
