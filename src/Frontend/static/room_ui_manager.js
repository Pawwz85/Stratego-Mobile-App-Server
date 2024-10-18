import {RoomLiveImage} from "../static/room_live_image.js"
import {appGlobalContext} from "../static/global_context.js"
import {FragmentManager, AwaitPhaseFragment, SetupFragment, GameplayPhaseFragment} from "../static/game_fragments.js"

export class RoomUIManager{
    constructor(roomLiveImage){
            appGlobalContext.chatModel = roomLiveImage.chatImage.chatModel;
            roomLiveImage.playerReadyStatusLiveImage.add_observer(appGlobalContext.seatWindowModel);
            this.roomLiveImage = roomLiveImage;
            this.fragmentManager = new FragmentManager(roomLiveImage.get_connection());
            roomLiveImage.gamePhaseLiveImage.add_observer(this);
            roomLiveImage.positionLiveImage.add_observer(this);
            roomLiveImage.userListImage.add_observer(appGlobalContext.table);
            roomLiveImage.userListImage.add_observer(this);

            appGlobalContext.red_clock = roomLiveImage.timersLiveImage.red_clock;
            appGlobalContext.blue_clock = roomLiveImage.timersLiveImage.blue_clock;

            this.currentUserRole = null;
            this.currentGamePhase = null;
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

    refresh_fragment(){
        let frag;
        const serverCon = this.roomLiveImage.get_connection();
        switch(this.currentGamePhase){

            case "awaiting": 
                frag = new AwaitPhaseFragment(serverCon);
                this.fragmentManager.setFragment(frag);
                break;
            
            case "setup":
                if (this.currentUserRole != "spectator" && this.currentUserRole)
                {
                    const color = (this.currentUserRole == "blue_player")? "blue" : "red";
                    frag = new SetupFragment(color, serverCon);
                    this.fragmentManager.setFragment(frag);
                }
                break;
            
            case "gameplay":
                    let color = (this.currentUserRole == "blue_player")? "blue" : undefined;
                    color = (this.currentUserRole == "red_player")? "red": color;
                    frag = new GameplayPhaseFragment(serverCon, color);
                    this.fragmentManager.setFragment(frag);
                break;

            case "finished":
                alert("Game finised");

        }
    }

    update_phase(phase){
        appGlobalContext.table.game_phase = phase;
        this.currentGamePhase = phase;
        appGlobalContext.table.notify_observers(); 
        this.refresh_fragment();
    }

    update(table_model){
        change = false;
        change = change || this.currentGamePhase != table_model.game_phase;
        change = change || this.currentUserRole != appGlobalContext.currentUser.boardrole;
        if(change){
            this.currentUserRole = appGlobalContext.currentUser.boardrole;
            this.currentGamePhase = table_model.game_phase;
            this.refresh_fragment();
        }
            

    }

}