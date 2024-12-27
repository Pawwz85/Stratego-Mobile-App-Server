import {BoardModel, BoardState, MoveGenerator, PieceType} from  "./board_model.js";
import { SeatSelectorWindowModel } from "./side_selector.js";
import { GeneralChatModel } from "./chat.js";
import {Clock} from "./clock.js"
import {RematchWindowModel} from "./rematch_window.js"
export class User{
    constructor(){
        this.profilePicture = null;
        this.username = "Player";
        this.boardrole = "spectator";
    }
}

// adapts protocol user to User object
function  user_adapter(user){
    return { 
             profilePicture: null,
             username: user.username,
             boardrole: user.role
            }
};

// adapter to user_list_live_image that delivers username to User map.
class UserService{
    constructor(){
        this.users = new Map();
        this.observers = [];
    }

    update_user_list(user_list){
        this.users.clear();

        for(let user of user_list){
            const new_entry = user_adapter(user);
            this.users.set(new_entry.username, new_entry);
        }
        this.notify_observers();
    }

    add_observer(o){
        this.observers.push(o);
        o.onUserServiceUpdate(this.users);
    }

    notify_observers(){
        for (let o of this.observers)
            o.onUserServiceUpdate(this.users);
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

        

        for(let user of user_list){
            
            if(user.role == "red_player"){
                this.red_player = user_adapter(user);
              
               // change = true;
            }
                
            if(user.role == "blue_player"){
                this.blue_player = user_adapter(user);
              //  change = true;
            }
            

            if(user.username == appGlobalContext.currentUser.username){
                appGlobalContext.currentUser.boardrole = user.role;
                console.log(user.role)
                appGlobalContext.notify_current_user_observer();
            }
                
        }
       // if(change)
        this.notify_observers();
    }

    update_position(position){
        let user_oriented_position = [];

        if(appGlobalContext.currentUser.boardrole == "blue_player")
            for(let i = 0; i < position.length; ++i)
                user_oriented_position.push([99 - position[i][0], position[i][1]]);
        else user_oriented_position = position;

        this.boardModel.boardstate.set_position(user_oriented_position);
        this.boardModel.set_selected_square_id(-1); // reset any marks
    }

    set_last_move(move){
        let user_oriented_move = null;
        if (move){
            if(appGlobalContext.currentUser.boardrole == "blue_player")
                user_oriented_move = {from: 99 - move.from, to: 99 - move.to};
            else
                user_oriented_move = move;
        }
        this.boardModel.boardstate.highlight_mask_manager.set_last_move(user_oriented_move);
    }

}

class AppGlobalContext{
    constructor(){
        this.currentUser = new User(); // Username is loaded by boot()
        this.roomId = "123",
        this.table = new TableModel();
        this.chatModel = new GeneralChatModel();
        this.seatWindowModel = new SeatSelectorWindowModel();
        this.userService = new UserService();

        this.rematchWindowModel = new RematchWindowModel();
        this.red_clock = new Clock(100);
        this.blue_clock = new Clock(100);
        this.userList = [];
        this.currentUserObserver = [];
        this.add_current_user_observer(this.rematchWindowModel);
    }
    update_ready_status(statuses){
        this.seatWindowModel.update_ready_status(statuses);
    }
    notify_current_user_observer(){
        for(let o of this.currentUserObserver)
            o.update_current_user(this.currentUser);
    }

    add_current_user_observer(observer){
        this.currentUserObserver.push(observer);
        observer.update_current_user(this.currentUser);
    }
}

export const appGlobalContext = new AppGlobalContext();
