import { Move } from "./board_model.js";
export class OnlineGameplayBoardController{
    constructor(serverConnection, boardModel, userColor = null){
        this.serverConnection = serverConnection; // for submitting moves
        this.mouse_index = null; // for highlighti
        this.boardModel = boardModel;
        this.userColor = userColor;
        this.to_server_cords = (i) => {return (userColor=="blue"? 99 - i: i)};
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
        
          const move = new Move(this.to_server_cords(this.boardModel.selected_sq_id), this.to_server_cords(sq))
          this.boardModel.submitMove(move)
          this.boardModel.selected_sq_id = -1
          this.boardModel.refresh_board_visuals()
          return
        }
        // We clicked our piece, so we select it
        if (square.piece?.color == this.userColor) {
          this.boardModel.selected_sq_id = sq
          this.boardModel.refresh_board_visuals()
          return
        }
    
        // We clicked random sq, unselect previous
        this.boardModel.selected_sq_id = -1
        this.boardModel.refresh_board_visuals()
      }

    handle_mouse_enter(sq){
        // if(this.boardModel.selected_sq_id != -1) return;
        // if(this.boardModel.boardstate.squares[sq].piece?.color === this.userColor){
        //     this.mouse_index = sq;
        //     this.boardModel.refresh_board_visuals(); // clear board to s               
        //     this.boardModel.boardstate.squares[sq].highlight = true;
        //     this.boardModel.boardstate.notify_observers();
        // }      
    }
    handle_mouse_leave(sq){
        // if(this.mouse_index == sq){
        //     this.mouse_index = null;
        //     this.boardModel.refresh_board_visuals();
        // }
    }
}