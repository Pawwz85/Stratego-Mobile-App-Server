import {BoardModel, BoardState, MoveGenerator, PieceType} from  "./board_model.js";
import { SeatSelectorWindowModel } from "./side_selector.js";
import { GeneralChatModel } from "./chat.js";
import {Clock} from "./clock.js"
export class User{
    constructor(){
        this.profilePicture = null;
        this.username = "Player";
        this.boardrole = "spectator";
    }
}
export class TableModel{
    constructor(){
        this.red_player = null;
        this.blue_player = null;
        this.game_phase = null;
        this.boardModel = new BoardModel(new MoveGenerator(), new BoardState());
        this.observers = [];
    }

    notify_observers(){
        for(let obs of this.observers)
            obs.update(this);
    }

    update_user_list(user_list){
        //let change = false;

        appGlobalContext.currentUser.boardrole = "spectator";
        this.red_player = this.blue_player = null;

        const user_adapter = user => {return {profilePicture: null, username: user.username, boardrole: user.role}};

        for(let user of user_list){
            
            if(user.role == "red_player"){
                this.red_player = user_adapter(user);
              
               // change = true;
            }
                
            if(user.role == "blue_player"){
                this.blue_player = user_adapter(user);
              //  change = true;
            }
            

            if(user.username == appGlobalContext.currentUser.username)
                appGlobalContext.currentUser.boardrole = user.role;
        }
       // if(change)
        this.notify_observers();
    }

}

class AppGlobalContext{
    constructor(){
        this.currentUser = new User(); // TODO: find a way to initialise this by a server
        this.roomId = "123",
        this.table = new TableModel();
        this.chatModel = new GeneralChatModel();
        this.seatWindowModel = new SeatSelectorWindowModel();
        this.red_clock = new Clock(100);
        this.blue_clock = new Clock(100);
        this.userList = [];
    }
    update_ready_status(statuses){
        this.seatWindowModel.update_ready_status(statuses);
    }
}

export const appGlobalContext = new AppGlobalContext();
