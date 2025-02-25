
import {BoardSegmentModel, BoardSegmentView} from "./BoardSegment.js"
import {ChatFragment} from "./chat.js"
import { appGlobalContext, TableModel, User } from "./global_context.js"
import { RematchWindowView } from "./rematch_window.js";
import { RoomLiveImage } from "./room_live_image.js";
import { SeatSelectorWindowView } from "./side_selector.js";
import {SetupSubmitionWindow} from "./setup.js"



export class UserInterfaceModel {
    constructor(room){
        this.board_segment_model = new BoardSegmentModel(room.get_connection());
        this.user_role = this.board_segment_model.user_role;
        this.phase = this.board_segment_model.game_phase;
        this.view = null
        this.server_connection = room.get_connection();
        room.gamePhaseLiveImage.add_observer(this);

        appGlobalContext.currentUserObserver.push(this);
        this.update_current_user(appGlobalContext.currentUser);
        this.update_phase(room.gamePhaseLiveImage.game_phase);
    }

    notify_view(){
        this.view?.update_ui(this);
    }

    update_phase(phase) {
        console.log(phase)
        if(this.phase != phase) {
            this.phase = phase;
            this.board_segment_model.set_game_phase(phase);
            this.notify_view();
        }
    }

    update_current_user_role(role){
        if(this.user_role != role){
            this.user_role = role;
            this.board_segment_model.set_user_role(role);
            this.notify_view();
        }
    }
    
    update_current_user(user){
        this.update_current_user_role(user.boardrole);
    }

    update_position(position){
        let user_oriented_position = [];
        console.log(position)
        if(appGlobalContext.currentUser.boardrole == "blue_player")
            for(let i = 0; i < position.length; ++i)
                user_oriented_position.push([99 - position[i][0], position[i][1]]);
        else user_oriented_position = position;

        console.log(user_oriented_position)
        appGlobalContext.table.boardModel.boardstate.set_position(user_oriented_position);
        appGlobalContext.table.boardModel.set_selected_square_id(-1); // reset any marks
        this.refresh_fragment();
    }



    update_user_list(user_list){
        appGlobalContext.table.update_user_list(user_list);
        this.currentUserRole = appGlobalContext.currentUser.boardrole
    }
    
}

export class UserInterfaceView {

    constructor(model, page_x, page_y){
        this.board_segment_view = new BoardSegmentView(model.board_segment_model, 500, 500);
        this.chat_fragment = new ChatFragment(appGlobalContext.chatModel, appGlobalContext.userService);
        this.side_selector_window = new SeatSelectorWindowView(appGlobalContext.seatWindowModel);
        this.rematch_window = new RematchWindowView(appGlobalContext.rematchWindowModel);
        this.setup_submit_window = new SetupSubmitionWindow(appGlobalContext.submitSetupWindowModel);
        this.element = document.createElement("div");

        this.chat_fragment.onSend = (msg => model.server_connection.commandMannager.send_message(msg));

        model.view = this;

        this.__create_element();
        this.update_ui(model);
        this.__resize(page_x, page_y);

    }

    update_ui(model) {
       
        this.rematch_window.element.style.display = "none";
        this.side_selector_window.window.style.display = "none";
        this.setup_submit_window.window.style.display = "none";
        switch(model.phase){
            case "awaiting":
                this.side_selector_window.window.style.display = "block";
                break;
            case "finished":
                this.rematch_window.element.style.display = "block";
                break;

            case "setup": 
                this.setup_submit_window.update(this.setup_submit_window.button);
            case "gameplay":
            default: 
                break;
        }

    }

    __create_element(){
        this.element.appendChild(this.board_segment_view.element);
        this.element.appendChild(this.chat_fragment.chatWrapper);
        this.element.appendChild(this.side_selector_window.window);
        this.element.appendChild(this.rematch_window.element);
        this.element.appendChild(this.setup_submit_window.window);
    }

    __resize(page_x, page_y){
        
        const board_seg_x = Math.floor(0.66* page_x);
        const chat_offset_x = board_seg_x;
        const board_offset_x = 0;

        this.board_segment_view.resize(board_seg_x, page_y);
        
        const board_layout = this.board_segment_view.get_board_layout();
        const popup_window_x = Math.floor(0.66* board_seg_x);
        const popup_window_y = Math.floor(0.33* board_seg_x);
        this.chat_fragment.setSize(page_x - board_seg_x, board_layout.size);


        // Problem we need to get placement of the board, encapsulated by board segment 
        this.side_selector_window.setSize(popup_window_x, popup_window_y);
        this.rematch_window.setSize(popup_window_x, popup_window_y); 
        this.setup_submit_window.setSize(popup_window_x/3, popup_window_y/3);
        this.side_selector_window.window.style.position = "absolute";
        this.rematch_window.element.style.position = "absolute";
        this.chat_fragment.chatWrapper.style.position = "absolute";
        this.board_segment_view.element.style.position = "absolute";
        this.setup_submit_window.window.style.position = "absolute";


        this.board_segment_view.element.style.left = board_offset_x + "px";        
        this.board_segment_view.element.style.top = "0px";  
        this.chat_fragment.chatWrapper.style.left = chat_offset_x + "px";        
        this.chat_fragment.chatWrapper.style.top = board_layout.offset_y + "px";

        this.side_selector_window.window.style.left = Math.floor(board_offset_x + board_layout.offset_x + (board_layout.size - popup_window_x)/2) + "px";
        this.side_selector_window.window.style.top = Math.floor(board_layout.offset_y + (board_layout.size - popup_window_y)/2) + "px";
        this.rematch_window.element.style.left = Math.floor(board_offset_x + board_layout.offset_x + (board_layout.size - popup_window_x)/2) + "px";
        this.rematch_window.element.style.top = Math.floor(board_layout.offset_y + (board_layout.size - popup_window_y)/2) + "px";
        this.setup_submit_window.window.style.left = Math.floor(board_offset_x + board_layout.offset_x + (board_layout.size - popup_window_x/3)/2) + "px";
        this.setup_submit_window.window.style.top = Math.floor(board_layout.offset_y + (board_layout.size - popup_window_y/3)/2) + "px";
    }
} 
