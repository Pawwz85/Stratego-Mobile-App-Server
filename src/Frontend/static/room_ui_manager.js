import {RoomLiveImage} from "../static/room_live_image.js"
import {appGlobalContext} from "../static/global_context.js"
import {FragmentManager, AwaitPhaseFragment, SetupFragment, GameplayPhaseFragment} from "../static/game_fragments.js"

export class RoomUIManager{
    constructor(roomLiveImage){
            appGlobalContext.chatModel = roomLiveImage.chatImage.chatModel;
            this.roomLiveImage = roomLiveImage;
            this.fragmentManager = new FragmentManager(roomLiveImage.get_connection());
            roomLiveImage.gamePhaseLiveImage.add_observer(this);
            roomLiveImage.positionLiveImage.add_observer(this);
            roomLiveImage.userListImage.add_observer(appGlobalContext.table);
            roomLiveImage.userListImage.add_observer(this);

            this.currentUserRole = null;
            this.currentGamePhase = null;
        }

    update_position(position){
        let user_oriented_position = [];

        if(appGlobalContext.currentUser.boardrole == "blue_player")
            for(let i = 0; i < position.length; ++i)
                user_oriented_position.push([99 - position[i][0], position[i][1]]);

        appGlobalContext.table.boardModel.boardstate.set_position(user_oriented_position);
        appGlobalContext.table.boardModel.set_selected_square_id(-1); // reset any marks
    }

    update_user_list(user_list){

    }

    refresh_fragment(){
        let frag;
        switch(this.currentGamePhase){

            case "awaiting": 
                frag = new AwaitPhaseFragment();
                this.fragmentManager.setFragment(frag);
                break;
            
            case "setup":
                if (this.currentUserRole != "spectator")
                {
                    const color = (boardrole == "blue_player")? "blue" : "red";
                    frag = new SetupFragment(color);
                    this.fragmentManager.setFragment(frag);
                }
                break;
            
            case "gameplay":
                    const color = (boardrole == "blue_player")? "blue" : "red";
                    frag = new GameplayPhaseFragment();
                    this.fragmentManager.setFragment(frag);
                break;

            case "finished":
                alert("Game finised");

        }
    }

    update_phase(phase){
        appGlobalContext.table.game_phase = phase;
        appGlobalContext.table.notify_observers(); 
    }

    update(table_model){
        change = false;
        change = change || this.currentGamePhase == table_model.game_phase;
        change = change || this.currentUserRole == appGlobalContext.currentUser.boardrole;
        if(change)
            this.refresh_fragment();

    }

}