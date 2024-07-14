const PieceTypes = {
    FLAG: "flag",
    BOMB: "bomb",
    SCOUT: "scout",
    MINER: "miner",
    SERGEANT: "sergeant",
    LIEUTENANT: "lieutenant",
    CAPTAIN: "captain",
    MAJOR: "major",
    COLONEL: "colonel",
    GENERAL: "general",
    MARSHAL: "marshal",
    UNKNOWN: "unknown"
}

const Colors = {
    RED: "red",
    BLUE: "blue"
}

class Piece{
    constructor(color_, type_){
        this.color = color_;
        this.type = type_;
    }

    copy(){
        return new Piece(this.color, this.type);
    }
}

class Square{
    constructor(){
        this.index = 0;
        this.piece = null;
        this.draw_dot = false;
        this.highlight = false;
    }

    copy(){
        let clone = new Square();
        clone.index = this.index;
        clone.draw_dot = this.draw_dot;
        clone.highlight = this.highlight;
        if (this.piece != null)
            clone.piece = this.piece.copy();
        return clone;
    }
}

class BoardState {
    constructor(){
        this.squares = new Array(100);
        this.observers = [];
        this.reset();
    }

    reset(){
        for (let i = 0; i<100; ++i){
            this.squares[i] = new Square();
            this.squares[i].index = i;
        }
    }

    notify_observers(){
        for(let i = 0; i<this.observers.length; ++i){
            this.observers[i].set_state(this);
        }
    }

    set_position(index_piece_pairs){
        this.reset();
        for(let i = 0; i<index_piece_pairs.length; ++i){
            let index = index_piece_pairs[i][0];
            let piece = index_piece_pairs[i][1];
            this.squares[index].piece = piece;
        }
        this.notify_observers();
    }

    set_square(sq){
        this.squares[sq.index] = sq;
        this.notify_observers();
    }

    copy(){
        let clone = new BoardState();
        for(let i = 0; i<100; ++i)
            clone.squares[i] = this.squares[i].copy();
        return clone;
    }
}

class Move{
    constructor(from_, to_){
        this.from = from_;
        this.to = to_;
    }
}

// Note: this class is not yet completed. TODO: Work on this class once we can load state from server
class MoveGenerator{
    constructor(){
        this.state = null;
        this.lake_fields = [42, 43, 46, 47, 52, 53, 56, 57];
    }
    set_state(state_){
        this.state = state_;
    }  
    
    generate_moves(){
        if(this.state == null)
            return [];
        result = [];
        
        return result; 
    }

    is_move_valid(move){
        return false;
    }
    copy(){
        let clone = new MoveGenerator();
    }
}

 class BoardModel{
    constructor(move_gen, state){
        this.boardstate = state.copy(); // we create a copy of a state so we get rid of external dependencies also, it makes BoardModel
        this.move_gen = move_gen.copy(); // more customisable, as we can pass different implementation of state or move gen
        this.selected_sq_id = -1
    }
    execute_move(move){
        if (this.move_gen.is_move_valid){
            // Do something with move
            return true;
        }
        return false;
    }
    
    set_selected_square_id(id){
        this.selected_sq_id = id;
    }
 }
