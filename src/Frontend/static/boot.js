console.log("JS client loaded.");

import {appGlobalContext} from "./global_context.js"
import { RoomLiveImage } from "./room_live_image.js";
import {RoomUIManager} from "../static/room_ui_manager.js"
import {ServerConnection} from "./server_connection.js"
import { UserInterfaceModel, UserInterfaceView } from "./user_interface.js";

function bind_globals_to_room(room){
    const serverConnection = room.get_connection();
    
    const roomLiveImage = room;
    roomLiveImage.positionLiveImage.add_observer(appGlobalContext.table);    
    roomLiveImage.userListImage.add_observer(appGlobalContext.table);
    roomLiveImage.playerReadyStatusLiveImage.add_observer(appGlobalContext.seatWindowModel);
    roomLiveImage.winnerLiveImage.add_observer(appGlobalContext.rematchWindowModel);
    roomLiveImage.rematchWillingnessLiveImage.add_observer(appGlobalContext.rematchWindowModel);
    serverConnection.eventHandler = roomLiveImage.get_event_handler();

    appGlobalContext.blue_clock = roomLiveImage.timersLiveImage.blue_clock;
    appGlobalContext.red_clock = roomLiveImage.timersLiveImage.red_clock;
    appGlobalContext.table.boardModel.submitMove = move => {serverConnection.commandMannager.send_move(move);};
    appGlobalContext.seatWindowModel.onClaimSeat = color => {serverConnection.commandMannager.claim_seat(color);};
    appGlobalContext.seatWindowModel.onSeatRelease = _ => {serverConnection.commandMannager.release_seat();};
    appGlobalContext.seatWindowModel.onReadyChange = value => {serverConnection.commandMannager.set_ready(value);};
    appGlobalContext.rematchWindowModel.onUserRematchWillingnessChange = value => {serverConnection.commandMannager.request_rematch(value)};
}
export function append_game_to_element(element_id){

    appGlobalContext.roomId = document.getElementById("boot_info_room_id").textContent;
    appGlobalContext.currentUser.username = document.getElementById("boot_info_username").textContent;
    appGlobalContext.seatWindowModel.attachTableObservers(appGlobalContext.table);


    let element = document.getElementById(element_id);
    const serverConnection = new ServerConnection(null);
    
    const roomLiveImage = new RoomLiveImage(serverConnection, appGlobalContext.roomId);
    
    bind_globals_to_room(roomLiveImage);
    roomLiveImage.chatImage.chatModel.observers = appGlobalContext.chatModel.observers;

    const UI = new UserInterfaceModel(roomLiveImage);
    const UIView = new UserInterfaceView(UI, 700, 700);
 
    //const roomUIManager = new RoomUIManager(roomLiveImage);

    element.append(UIView.element);

    roomLiveImage.sync(); // comment this off if you want test UI, otherwise phase & role would be fetch from server
}