
enum PieceType{
    FLAG,
    BOMB,
    SPY,
    SCOUT,
    MINER,
    SERGEANT,
    LIEUTENANT,
    CAPTAIN,
    MAJOR,
    COLONEL,
    GENERAL,
    MARSHAL,
    UNKNOWN
}

enum Color{
    RED,
    BLUE
}

class Piece{
    public readonly color: Color
    public readonly type: PieceType
    constructor(color: Color, type_ : PieceType){
        this.color = color;
        this.type = type_;
    }

    copy(){
        return new Piece(this.color, this.type);
    }
}

class Square{
    public index : number;
    public piece : Piece | null;
    public draw_dot : boolean;
    public highlight : boolean;

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

interface BoardStateObserver{
    set_state(state: BoardState): void
}

class BoardState {

    public squares: Array<Square>;
    public observers: Array<BoardStateObserver>;

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

    set_square(sq: Square){
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
    public readonly from: number;
    public readonly to: number;

    constructor(from_: number, to_: number){
        this.from = from_;
        this.to = to_;
    }
}

// Note: this class is not yet completed. TODO: Work on this class once we can load state from server
class MoveGenerator{
    public state: BoardState | null;
    public lake_fields: Array<number>;
    constructor(){
        this.state = null;
        this.lake_fields = [42, 43, 46, 47, 52, 53, 56, 57];
    }
    set_state(state_ : BoardState | null){
        this.state = state_;
    }  
    
    generate_moves_for_piece(sq_id : number){
        const piece = this.state?.squares[sq_id].piece;

        if(!piece)
            return [];

        const pieceColor = piece.color;
        if ([PieceType.BOMB, PieceType.FLAG].includes(piece.type))
            return [];

        const result = [];
        if(piece.type != PieceType.SCOUT){
            const offsets = [-10, -1, 1, 10];
            const result : Array<Move> = [];
            for( let off of offsets){
                let move = new Move(sq_id, sq_id + off);
                if(this.is_move_valid(move))
                    result.push(move);
            }
            return result;
        } else{
            const offsets = [-10, -1, 1, 10];
            let result : Array<Move> = [];
            for( let off of offsets)
                for(let i = 1; sq_id + i*off >= 0 && sq_id + i*off < 100; ++i){
                    let sq = sq_id + i*off;
                    let enemy = this.state?.squares[sq].piece ?? null;

                    if(enemy == null){
                        result.push(new Move(sq_id, sq));
                        continue;
                    }
                    
                    if(enemy.color == piece.color)
                        break;
                    
                    if(this.lake_fields.includes(sq))
                        break;

                    result.push(new Move(sq_id, sq));
                    break; // enemy piece
                }
            return result;
        }
        return [];
    }

    generate_moves(){
        if(this.state == null)
            return [];
        const result : Array<Number> = [];
        
        return result; 
    }

    is_move_valid(move : Move){
        if (move.from < 0 || move.from > 99 || move.to < 0 || move.to > 99 || this.lake_fields.includes(move.to) ) 
            return false;

        const piece = this.state?.squares[move.from].piece ?? null;

        if(!piece) return false;

        if(piece.type == PieceType.BOMB || piece.type == PieceType.FLAG)
            return false;

        if(piece.type != PieceType.SCOUT){
            const deltaY = Math.abs(Math.floor(move.from/10) - Math.floor(move.to/10));
            const deltaX = Math.abs(move.from%10 - move.to%10);
            if(deltaX + deltaY != 1)
                return false;

            const enemy = this.state?.squares[move.to].piece ?? null;
            return enemy?.color != piece.color;
        } else{
            const deltaY = Math.abs(Math.floor(move.from/10) - Math.floor(move.to/10));
            const deltaX = Math.abs(move.from%10 - move.to%10);

            if(deltaX != 0 && deltaY != 0)
                return false;

            if(deltaX == 0 && deltaY == 0)
                return false;

            let sq = move.from + 10*deltaY + deltaX;
            while (sq >= 0 && sq < 100 && !this.lake_fields.includes(sq) ){
                let enemy = this.state?.squares[sq].piece ?? null;
                if(!enemy){
                    if(sq == move.to){
                        sq +=  10*deltaY + deltaX;
                        continue;
                    } else return true;
                    
                }

                return sq == move.to && enemy.color != piece.color;
            }
        }
        return false;
    }
    copy(){
        let clone = new MoveGenerator();
        return clone;
    }
}
 
/*
    Bord Model dedicated for gameplay phase
*/
 class BoardModel{
    public boardstate : BoardState;
    public move_gen : MoveGenerator;
    public selected_sq_id : number;
    public userColor: Color | null;
    public submitMove : (m :Move) => any;

    constructor(move_gen : MoveGenerator, state : BoardState){
        this.boardstate = state.copy(); // we create a copy of a state so we get rid of external dependencies also, it makes BoardModel
        this.move_gen = move_gen.copy(); // more customisable, as we can pass different implementation of state or move gen
        this.selected_sq_id = -1; // square selected by player
        this.userColor = null; // Color of the user, controlls the bord controller generated by model
        this.submitMove = move => {}; // callback used by board controller

    }
    
    set_selected_square_id(id: number){

        if(this.selected_sq_id == id)
            return;

        this.selected_sq_id = id;
    }

    refresh_board_visuals(){
        for(let i = 0; i<this.boardstate.squares.length; ++i){
            this.boardstate.squares[i].highlight = (i == this.selected_sq_id);
            this.boardstate.squares[i].draw_dot = false;
        }

        if(this.selected_sq_id < this.boardstate.squares.length && this.selected_sq_id >= 0){
            const legal_moves = this.move_gen.generate_moves_for_piece(this.selected_sq_id);
            for (let move of legal_moves)
                this.boardstate.squares[move.to].draw_dot = true;
        }

        this.boardstate.notify_observers();
    }
 }

 class GameplayBoardController{
    public boardModel: BoardModel;
    constructor(boardModel: BoardModel){
        this.boardModel = boardModel;
    }

    handle_sq_click(sq: number){

        // We clicked already selected square, so we unselect it
        if (sq == this.boardModel.selected_sq_id){
            this.boardModel.selected_sq_id = -1;
            this.boardModel.refresh_board_visuals();
            return;
        }

        const square = this.boardModel.boardstate.squares[sq];

        // We clicked dot, so we are submitting move
        if(square.draw_dot){
            const move = new Move(this.boardModel.selected_sq_id, sq);
            this.boardModel.submitMove(move);
            this.boardModel.selected_sq_id = -1;
            this.boardModel.refresh_board_visuals();
            return;
        }

        // We clicked our piece, so we select it
        if(square.piece?.color == this.boardModel.userColor){
            this.boardModel.selected_sq_id = sq;
            this.boardModel.refresh_board_visuals();
            return;
        }

        // We clicked random sq, unselect previous
        this.boardModel.selected_sq_id = -1;
        this.boardModel.refresh_board_visuals();
    }
 }

