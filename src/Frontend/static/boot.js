console.log("JS client loaded.");

import {appGlobalContext} from "../static/global_context.js"
import { RoomLiveImage } from "./room_live_image.js";
import {RoomUIManager} from "../static/room_ui_manager.js"
import {ServerConnection} from "../static/server_connection.js"

export function append_game_to_element(element_id){

    appGlobalContext.roomId = document.getElementById("boot_info_room_id").textContent;
    appGlobalContext.currentUser.username = document.getElementById("boot_info_username").textContent;

    let element = document.getElementById(element_id);
    const serverConnection = new ServerConnection(null);
    const roomLiveImage = new RoomLiveImage(serverConnection, appGlobalContext.roomId);
    serverConnection.eventHandler = roomLiveImage.get_event_handler();

    const roomUIManager = new RoomUIManager(roomLiveImage);

    element.append(roomUIManager.fragmentManager.fragmentWrapper);

    roomLiveImage.sync();
}