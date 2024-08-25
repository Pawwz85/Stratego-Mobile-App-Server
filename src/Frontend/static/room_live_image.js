import { GeneralChatModel } from "./chat.js";
import {PieceType, Color, Piece} from "./board_model.js"
import { PieceEncoder } from "./PieceEncoder.js";
export class LiveChatImage{
    constructor(serverConnection, room_id){
        this.chatModel = new GeneralChatModel();
        this.orderedMessagesList = [];
        this.serverConnection = serverConnection;
        this.roomId = room_id;
    }

    add_message(orderedMessage){
        if (typeof orderedMessage.orderNumber != "number")
            throw new TypeError("Ordered Message did not had a order number");

        const result = [];
        let i = 0;

        for(i = 0; i<this.orderedMessagesList.length && this.orderedMessagesList[i].orderNumber < orderedMessage.orderNumber; ++i)
            result.push(this.orderedMessagesList[i]);
        
        result.push(orderedMessage);

        for(; i<this.orderedMessagesList.length; ++i)
            result.push(this.orderedMessagesList[i]);

        this.orderedMessagesList = result;
        this.chatModel.set_messages(this.orderedMessagesList);
    }

    __protocol_message_to_component_message(msg){
        return {
            orderNumber: msg.nr,
            username: msg.nickname,
            content: msg.message
        };
    }

    __from_untagged_messages(untaggedMessages){
        this.orderedMessagesList = untaggedMessages.filter(msg => msg ?? null != null);
        const orderedMessages = []
        console.log(this.orderedMessagesList)
        for(let i = 0; i<this.orderedMessagesList.length; ++i){
            this.orderedMessagesList[i].nr = i;
            orderedMessages.push(this.__protocol_message_to_component_message(this.orderedMessagesList[i]));
        }
        this.orderedMessagesList = orderedMessages;
        this.chatModel.set_messages(this.orderedMessagesList);
    }

    sync(){
        const chat_meta_request = {
            type: "get_chat_metadata",
            room_id: this.roomId
        };
        const chat_message_request = {
            type: "get_chat_messages",
            room_id: this.roomId,
            from: 0,
            to: 0
        }

        this.serverConnection.send_request(chat_meta_request, 10000).then(
            value => {
                if (value?.status != "success"){
                    console.log("Failed to fetch chat metadata");
                    console.log(value);
                    return;
                }
                chat_message_request.to = value?.chat_metadata?.size ?? 0;
                this.serverConnection.send_request(chat_message_request, 10000).then(
                    value => {
                        if (value?.status != "success"){
                            console.log("Failed to fetch chat messages");
                            console.log(value);
                            return;
                        }
                        this.__from_untagged_messages(value?.messages ?? []);
                    }
                )
            }
        );

    }

    handle_chat_event(event){
        if(typeof event?.nickname != "string" || typeof event?.message != "string" || typeof event?.nr != "number"){
            console.log("API produced unrecognizable response. Outdated client?");
            return;
        }

        if(event?.room_id != this.roomId){
            return; // room id did not match
        }

        const msg = this.__protocol_message_to_component_message(event);
        this.add_message(msg);
    }
}

class BoardLiveImage{

    constructor(serverConnection, room_id){
        this.orderNumber = -1;
        this.serverConnection = serverConnection;
        this.roomId = room_id;
        this.position = null;
        this.phase = "awaiting";
        this.observers = [];
    }

    notify_observers(){
        for(let obs of this.observers)
            obs.update(this);
    }

    add_observer(observer){
        this.observers.push(observer);
        observer.update(this); // instant refresh
    }

    handle_board_event(event){
        console.log(event)
        if( typeof event?.game_status != "string" || typeof event?.board != "object" || typeof event?.nr != "number"){
            console.log("API produced unrecognizable response. Outdated client?");
            console.log(event);
            return;
        }
        if (event.nr > this.orderNumber){
            this.orderNumber = event.nr;
            this.phase = event.game_status;
            this.position = event.board;
            this.notify_observers();
        }
    }

    sync(){
        const req_board = {
            type: "get_board",
            room_id: this.roomId
        }
        this.serverConnection.send_request(req_board, 10000).then(
            value => {
                if (value?.status != "success"){
                    console.log("Failed to get board");
                    console.log(value);
                    return;
                }
                this.handle_board_event(value);
            }

        )
    }
}

class GamePhaseLiveImage{
    constructor(boardLiveImage){
        this.game_phase = null;
        this.phase_observers = [];
        boardLiveImage.add_observer(this);
    }

    update(boardLiveImage){
        const new_value = boardLiveImage.phase;
        console.log(new_value, "phase")
        if( new_value != this.game_phase){
            this.game_phase = new_value;
            this.notify_observers();
        }
    }

    add_observer(observer){
        this.phase_observers.push(observer);
        observer.update_phase(this.game_phase);
    }

    notify_observers(){
        for (let obs of this.phase_observers)
            obs.update_phase(this.game_phase);
    }
}
class BoardPositionLiveImage{
    constructor(boardLiveImage){
        this.position = []; // position is compatibible with set_position() method of board_state
        this.position_observers = [];

        this.token_decoter = new PieceEncoder();
        boardLiveImage.add_observer(this);
    }

    add_observer(observer){
        this.position_observers.push(observer);
        observer.update_position(this.position);
    }

    notify_observers(){
        for (let obs of this.position_observers)
            obs.update_position(this.position);
    }



    __parse_position(boardArray){
        let result = [];
        console.log(boardArray)
        if (!boardArray) return result;

        for(let i = 0; i < boardArray.length; ++i) if(boardArray[i] != null){

            const type = this.token_decoter.decode_token(boardArray[i]?.type);
            const color = (boardArray[i]?.side == "red")? Color.RED : Color.BLUE

            result.push([i, new Piece(color, type)]);
        }
        console.log(result);
        return result;
    }

    update(boardLiveImage){
        const new_pos = this.__parse_position(boardLiveImage.position);
        console.log(new_pos)
        const are_pos_different = (pos1, pos2) => {
            if(pos1.length != pos2.length)
                return true;

            pos1.sort((a, b) => {return a[0] - b[0]}); // sort ascending by index
            pos2.sort((a, b) => {return a[0] - b[0]});

            for(let i = 0; i< pos1.length; ++i){
                const p1 = pos1[i][1];
                const p2 = pos2[i][1];
                if (pos1[i][0] != pos2[i][0] ||
                    p1?.color != p2?.color   ||
                    p1?.type != p2?.type 
                )
                    return true;
            }
            return false;
        }

        if(are_pos_different(new_pos, this.position)){
            this.position = new_pos;
            this.notify_observers();
        }

    }
}

class UserListOrderedOperationsList{
    constructor(userList, serverConnection, roomId){
        this.userList = userList;
        this.operations = [];
        this.reference = [];
        this.referenceOrderNumber = -1;
        this.serverConnection = serverConnection;
        this.roomId = roomId;
    }

    __refresh_list_image(){
        let result = [];
        let sync = false;
        for(let user of this.reference)
            result.push({...user});

        for(let op of this.operations){
            switch(op.op){
                case "modify":
                    let user = result.find(user => {return user.username == op.username;});
                    if (user) {for(let property in op.fields) if (op.fields.hasOwnProperty(property))
                        user[property] = op.fields[property];} else
                    sync = true;
                    break;
                case "add":
                    result.push(op.fields);
                    break;
                
                case "delete":
                    result = result.filter(user => { return user.username != op.username});
                    break;
            }
        };

        if(!sync)
            this.userList.set(result);
         else
            this.sync()

    }

    add_operation(op){
        this.operations.push(op);
        this.operations.sort((a,b) => {
            return a.orderNumber - b.orderNumber;
        })
   
        this.__refresh_list_image()
    }

    handle_user_event(event){
        if(typeof event?.nr != "number" || typeof event?.op != "string"){
                console.log("API produced unrecognizable response. Outdated client?");
                console.log(event);
                return;
        }

        if(event.nr <= this.referenceOrderNumber)
            return; // event is obsolete

        const operation = {
            op: event.op,
            fields: event.fields,
            username: event.nickname,
            orderNumber: event.nr
        }
        this.add_operation(operation);

    }

    sync(){
        const request = {
            type: "get_room_users",
            room_id: this.roomId
        }

        this.serverConnection.send_request(request, 10000).then(value => {
            if (value?.status != "success"){
                console.log("Failed to get user list");
                console.log(value);
                return;
            }
            this.userList.set(value.user_list);
            this.reference = value.user_list;

            this.referenceOrderNumber = value.nr;
            this.operations = [];
        })
    }
}

class UserListLiveImage{

    constructor(serverConnection, roomId){
        this.__operationList = new UserListOrderedOperationsList(this, serverConnection, roomId);
        this.__operationList.userList = this;
        this.user_list = [];
        this.user_list_observers = []
    }

    notify_observers(){
        for(let observer of this.user_list_observers){
            observer.update_user_list(this.user_list);
        }
    }

    add_observer(observer){
        this.user_list_observers.push(observer);
        observer.update_user_list(this.user_list);
    }

    sync(){
        this.__operationList.sync();
    }

    set(user_list){
        this.user_list = user_list;
        this.notify_observers();
    }

    handle_user_event(event){
        this.__operationList.handle_user_event(event);
    }

}

class PlayerReadyStatusLiveImage{
    constructor(serverConnection, roomId){
        this.serverConnection = serverConnection;
        this.roomId = roomId;
        this.is_red_player_ready = false;
        this.is_blue_player_ready = false;
        this.observers = []
    }

    handleReadyEvent(event){
        if(typeof event?.value != "boolean" || typeof event?.side != "string"){
            console.log("API produced unrecognizable response. Outdated client?");
            console.log(event);
            return;
        }
        console.log("ready_event", event)
        if(event.side == "red"){
            this.is_red_player_ready = event.value;
        }

        if(event.side == "blue"){
            this.is_blue_player_ready = event.value;
        }

        this.notify_observers()
    }

    sync(){
        const request = {
            type: "get_ready",
            room_id: this.roomId
        }
        const tmp = this;
        this.serverConnection.send_request(request, 10000).then(
            value => {
                if (typeof value?.red_player != "boolean" || typeof value?.blue_player != "boolean" || value?.status != "success"){
                    console.log("Failed to get player ready status");
                    console.log(value);
                    return;
                }
                this.is_red_player_ready = value.red_player;
                this.is_blue_player_ready = value.blue_player;
                tmp.notify_observers()
            }
        )

    }

    add_observer(observer){
        const tmp = this;
        const msg = {
            red_player: tmp.is_red_player_ready,
            blue_player: tmp.is_blue_player_ready
        };
        this.observers.push(observer);
        observer.update_ready_status(msg);
    }

    notify_observers(){
        const tmp = this;
        const msg = {
            red_player: tmp.is_red_player_ready,
            blue_player: tmp.is_blue_player_ready
        }
   
        for(let ob of this.observers){
           ob.update_ready_status(msg)
        }
            
    }
}

export class RoomLiveImage{
    constructor(serverConnection, roomId){
        this.connection = serverConnection;
        this.chatImage = new LiveChatImage(serverConnection, roomId);
        this.userListImage = new UserListLiveImage(serverConnection, roomId);
        this.playerReadyStatusLiveImage = new PlayerReadyStatusLiveImage(serverConnection, roomId);
        this.boardLiveImage = new BoardLiveImage(serverConnection, roomId); 
        this.positionLiveImage = new BoardPositionLiveImage(this.boardLiveImage);
        this.gamePhaseLiveImage = new GamePhaseLiveImage(this.boardLiveImage);    
    }

    sync(){
        this.userListImage.sync();
        this.playerReadyStatusLiveImage.sync();
        this.chatImage.sync();
        this.boardLiveImage.sync(); // explicitly sync position and gamephase
    }

    get_event_handler(){
        return {
            handleWelcomeEvent: (json) => {},
            handleUserEvent: (json) => this.userListImage.handle_user_event(json),
            handleBoardEvent: (json) => this.boardLiveImage.handle_board_event(json),
            handleChatEvent: (json) => this.chatImage.handle_chat_event(json),
            handleChatReset: (json) => {},
            handleReadyEvent: (json) => this.playerReadyStatusLiveImage.handleReadyEvent(json),
            handleRoomClosed: (json) => {alert("Room was closed by server")}
        }
    }

    get_connection(){
        return this.connection;
    }

}