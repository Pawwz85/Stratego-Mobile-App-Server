import {io} from "https://cdn.socket.io/4.7.5/socket.io.esm.min.js"
import { appGlobalContext } from "./global_context.js";

/*
    This class is essentially deprecated as room_live_image creates cusum event handlers to sync room image, nevertheless 
    it is used EventHandler interface
*/
class EventHandler{
    constructor(){
    }

    handleWelcomeEvent(jsonPayload){
        console.log("Room welcome event received");
    }

    handleUserEvent(jsonPayload){
        console.log("User event received");
    }

    handleBoardEvent(jsonPayload){
        console.log("Board event received");
    }

    handleChatEvent(jsonPayload){
        console.log("Chat event received");
    }
    handleChatReset(jsonPayload){
        console.log("Chat reset");
    }
    handleRoomClosed(jsonPayload){
        console.log("Room closed");
    }
}

class GameNodeCommandManager{
    constructor(serverConnection){
        this.serverConnection = serverConnection;
        this.timeout_time = 10000;
    }

    exit_room(){
        const request = {
            type: "exit_room",
            room_id: appGlobalContext.roomId
        }
        return this.serverConnection.send_request(request, this.timeout_time);
    }

    resign(){
        const request = {
            type: "resign",
            room_id: appGlobalContext.roomId
        }
        return this.serverConnection.send_request(request, this.timeout_time);
    }

    claim_seat(color){
        const request = {
            type: "claim_seat",
            room_id: appGlobalContext.roomId,
            side: color
        }
        return this.serverConnection.send_request(request, this.timeout_time);
    }

    release_seat(){
        const request = {
            type: "release_seat",
            room_id: appGlobalContext.roomId,
        }
        return this.serverConnection.send_request(request, this.timeout_time);
    }

    set_ready(value){
        const request ={
            "type" : "set_ready",
            "value" : value ,
            "room_id": appGlobalContext.roomId
        } 
        return this.serverConnection.send_request(request, this.timeout_time);
    }

    send_message(msg){
        const request ={
            "type" : "send_chat_message",
            "message" : msg,
            "room_id": appGlobalContext.roomId
        } 
        return this.serverConnection.send_request(request, this.timeout_time);
    }

    send_setup(setup){
        const request ={
            "type" : "send_setup",
            "setup" : setup,
            "room_id": appGlobalContext.roomId
        } 
        return this.serverConnection.send_request(request, this.timeout_time);
    }

    send_move(move){
        const request ={
            "type" : "send_move",
            "move" : move,
            "room_id": appGlobalContext.roomId
        } 
        return this.serverConnection.send_request(request, this.timeout_time);
    }

    request_rematch(){
        const request ={
            "type" : "set_rematch_willingess",
            "setup" : move,
            "room_id": appGlobalContext.roomId
        } 
        return this.serverConnection.send_request(request, this.timeout_time);
    }

}
/*
    This class manages callbacks associates with given 
*/
class ServerRequestManager{
    constructor(){
        this.id_sequence = 0;
        this.requests = new Map(); // map from requests id to request metadata
        setInterval(() => this.__remove_old_entries(), 10000);
        
    }

    __register_request(request_id, callback, timeout_callback, timeout_time){
        const req_meta = {
            id: request_id,
            callback: callback,
            ontimeout: timeout_callback,
            timeout_date: Date.now() + timeout_time
        };
        this.requests.set(request_id, req_meta);
    }

    __remove_old_entries(){
        let old_keys = [];
        const now = Date.now();
        for(let key of this.requests.keys())
            if(now > this.requests.get(key).timeout_date)
                old_keys.push(key);
        
        for (let key of old_keys){
            let meta = this.requests.get(key);
            this.requests.delete(key);
            console.log(key);
            meta.ontimeout(new WebTransportError("Timed out"));
        }
    }

    __generate_id(){
        // id for stratego protocole doesn't need to be worldwide unique, it has to be unique in context of user session
        return ++this.id_sequence;
    }

    set_response(response){
        const meta = this.requests.get(response.response_id);
        if(meta){
            meta.callback(response);
            this.requests.delete(meta.id);
        }
    }

    send_request(req, timeout_time){
        const id = req.request_id ?? this.__generate_id();
        const promise = new Promise(
            (resolve, reject) => {
                this.__register_request(id, resolve, reject, timeout_time);
            }
        )

        const tagged_req = {...req};
        tagged_req.message_id = id;

        return [promise, tagged_req];
    }

}

export class ServerConnection{
    constructor(eventHandler){
        this.socket = io();
        this.requestManager = new ServerRequestManager();
        this.eventHandler = eventHandler;
        this.commandMannager = new GameNodeCommandManager(this);
      
        const con = this;  
        this.socket.on("room_welcome_event", jsonPayload => {con.eventHandler.handleWelcomeEvent(jsonPayload);});
        this.socket.on("room_user_event", jsonPayload => {con.eventHandler.handleUserEvent(jsonPayload); });
        this.socket.on("board_event", jsonPayload => {con.eventHandler.handleBoardEvent(jsonPayload); });
        this.socket.on("ready_event", jsonPayload => {con.eventHandler.handleReadyEvent(jsonPayload);});
        this.socket.on("chat_event", jsonPayload => {con.eventHandler.handleChatEvent(jsonPayload); console.log("chat ev");});
        this.socket.on("chat_reset", jsonPayload => {con.eventHandler.handleChatReset(jsonPayload);});
        this.socket.on("room_closed", jsonPayload => {con.eventHandler.handleRoomClosed(jsonPayload);});

        this.socket.on("response", jsonPayload => {con.requestManager.set_response(jsonPayload);
                console.log(jsonPayload)
        });
        // TODO: create mechanism to handle server responses
    }

    send_request(req, timeout_time){
        const tuple = this.requestManager.send_request(req, timeout_time);
        const promise = tuple[0];
        const tagged_req = tuple[1];
        this.socket.emit("request", tagged_req);
        return promise;
    }
   
    

}

