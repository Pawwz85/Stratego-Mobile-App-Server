export class GeneralChatModel{
    constructor(){
        this.messages = [];
        this.messagesCount = 0;
        this.observers = [];
    }

    notify_observers(){
        for(let i = 0; i<this.observers.length; ++i)
            this.observers[i].update_chat(this);
    }

    add_message(msg){
        this.messages.push(msg);
        this.messagesCount = this.messages.length;
        this.notify_observers();
    }

    set_messages(new_messages){
        this.messages = new_messages;
        this.messagesCount =  this.messages.length;
        this.notify_observers();
    }

}
const spectator_colours = [
    `AliceBlue`,
    `AntiqueWhite`,
    `Aqua`,
    `Aquamarine`,
    `Azure`,
    `Beige`,
    `Bisque`,
    `BlanchedAlmond`,
    `BlueViolet`,
    `Brown`,
    `BurlyWood`,
    `CadetBlue`,
    `Chartreuse`,
    `Chocolate`,
    `Coral`,
    `CornflowerBlue`,
    `Cornsilk`,
    `Crimson`,
    `Cyan`,
    `DarkCyan`,
    `DarkGoldenRod`,
    `DarkGray`,
    `DarkGrey`,
    `DarkGreen`,
    `DarkKhaki`,
    `DarkMagenta`,
    `DarkOliveGreen`,
    `Darkorange`,
    `DarkOrchid`,
    `DarkSalmon`,
    `DarkSeaGreen`,
    `DarkSlateGray`,
    `DarkTurquoise`,
    `DarkViolet`,
    `DeepPink`,
    `DimGrey`,
    `FireBrick`,
    `FloralWhite`,
    `ForestGreen`,
    `Fuchsia`,
    `Gainsboro`,
    `GhostWhite`,
    `Gold`,
    `GoldenRod`,
    `Gray`,
    `Green`,
    `GreenYellow`,
    `HoneyDew`,
    `HotPink`,
    `IndianRed`,
    `Indigo`,
    `Ivory`,
    `Khaki`,
    `Lavender`,
    `LavenderBlush`,
    `LawnGreen`,
    `LemonChiffon`,
    `LightBlue`,
    `LightCoral`,
    `LightCyan`,
    `LightGoldenRodYellow`,
    `LightGray`,
    `LightGrey`,
    `LightGreen`,
    `LightPink`,
    `LightSalmon`,
    `LightSeaGreen`,
    `LightSkyBlue`,
    `LightSlateGray`,
    `LightSlateGrey`,
    `LightSteelBlue`,
    `LightYellow`,
    `Lime`,
    `LimeGreen`,
    `Linen`,
    `Magenta`,
    `Maroon`,
    `MediumAquaMarine`,
    `MediumOrchid`,
    `MediumPurple`,
    `MediumSeaGreen`,
    `MediumSlateBlue`,
    `MediumSpringGreen`,
    `MediumTurquoise`,
    `MediumVioletRed`,
    `MintCream`,
    `MistyRose`,
    `Moccasin`,
    `NavajoWhite`,
    `OldLace`,
    `Olive`,
    `OliveDrab`,
    `Orange`,
    `OrangeRed`,
    `Orchid`,
    `PaleGoldenRod`,
    `PaleGreen`,
    `PaleTurquoise`,
    `PaleVioletRed`,
    `PapayaWhip`,
    `PeachPuff`,
    `Peru`,
    `Pink`,
    `Plum`,
    `PowderBlue`,
    `Purple`,
    `RosyBrown`,
    `SaddleBrown`,
    `Salmon`,
    `SandyBrown`,
    `SeaGreen`,
    `SeaShell`,
    `Sienna`,
    `Silver`,
    `SkyBlue`,
    `SlateGray`,
    `Snow`,
    `SpringGreen`,
    `SteelBlue`,
    `Tan`,
    `Teal`,
    `Thistle`,
    `Tomato`,
    `Turquoise`,
    `Violet`,
    `Wheat`,
    `White`,
    `WhiteSmoke`,
    `Yellow`,
    `YellowGreen`,
  ]

class ChatUserColorService{
    constructor(userService){
        this.coloring = new Map(); // maps username to to chat color
        this.observers = [];
        userService.add_observer(this);
    }


    get_color_for_role(role){
        
        let result = "gray;"
        if (role == "red_player"){
            result = "#ff0000";
        } else if (role == "blue_player"){
            return "#0000ff";
        } else {
            const index = Math.floor(Math.random()* spectator_colours.length);
            result = spectator_colours[index];
        }
        return result;
    }

    onUserServiceUpdate(users){
        const next_colouring = []

        for (let username of users.keys()){
            const role = users.get(username).boardrole ?? "spectator"; 
            let colour = (role == "spectator")?(this.coloring.get(username) ?? this.get_color_for_role(role)): this.get_color_for_role(role);
            
            if (role == "spectator" && (colour == "#ff0000" || colour == "#0000ff"))
                colour = this.get_color_for_role(role);
            
            next_colouring.push({username: username, colour: colour})       
        }
        

        this.coloring.clear();

        for(let c of next_colouring)
            this.coloring.set(c.username, c.colour);
        
        this.notify_observers();

    }

    add_observer(o){
        this.observers.push(o);
        o.onNewColourSchema(this.coloring);
    }

    notify_observers(){
        for (let o of this.observers)
            o.onNewColourSchema(this.coloring);
    }

}

export class ChatView{
    constructor(chat_model, chatUserColorService){
        this.chat_model = chat_model
        this.colouring = new Map();
        this.chat_model.observers.push(this);
        chatUserColorService.add_observer(this);
        this.chat = document.getElementById("chat_window")
    }

    clear_messages(){
        let msg_box = document.getElementById("chat_messages");

        while((msg_box.firstChild))
            msg_box.firstChild?.remove();
    }
    /*
      <span class="text-green-400 italic">Spectator</span>
      <p class="text-sm text-gray-300">
        Watching the game closely! Excited to see who wins.
      </p>
      */
    update_chat(model){
        this.clear_messages();

        const msgs = model.messages;
        let msg_box = document.getElementById("chat_messages");
        for (let msg of msgs){
            let item = document.createElement("article");
            let username = document.createElement("span");
            let msg_body = document.createElement("p");

            username.setAttribute("class", "text-bold italic");
            username.style.webkitTextFillColor = this.colouring.get(msg.username) ?? "gray";
            username.textContent = msg.username;

            msg_body.setAttribute("class", "text-sm text-gray-300 ");
            msg_body.textContent = msg.content;

            item.setAttribute("class", "flex flex-col text-wrap");
            item.append(username);
            item.append(msg_body);
            msg_box.append(item);
        }
    }

    refresh(){
        this.update_chat(this.chat_model);
    }

    onNewColourSchema(coloring){
        this.colouring = coloring;
        this.refresh();
    }
}

export class ChatFactory{
    create_chat_view(chat_model, user_color_service){
        return new ChatView(chat_model, user_color_service);
    }

    create_chat_text_area(){
        return document.getElementById("chat_text_input");
    }

    create_send_button(chat_text_area , onSubmit = null){
        let result = document.getElementById("chat_submit_btn");
        
        if (onSubmit == null)
            onSubmit = str => {};

        result.onclick = ev => {
            let value = chat_text_area.value;
            onSubmit(value);
            chat_text_area.value = "";
        }
        return result;
    }
}


export class ChatFragment{
    constructor(chat_model, userService){
        let chatFact = new ChatFactory();
        this.chatModel = chat_model;
        this.onSend = (msg) => {};

        let chat_view = chatFact.create_chat_view(this.chatModel, new ChatUserColorService(userService))
        this.chatWrapper = this.__create_element();
       
        chatFact.create_send_button(chatFact.create_chat_text_area(), (msg) => {this.onSend(msg)});
        chat_view.clear_messages();
        this.onCreate();
        }

    __create_element(){
        let result = document.createElement("div");
        return result;
    }
    onCreate(){    

        // move chat_window in chat hierarchy
        let chat = document.getElementById("chat_window");
        chat.remove();
        this.chatWrapper.append(chat);
        
    }
    
    onFocus(){
        this.chatWrapper.style.display = "block";
    }

    onHide(){
        this.chatWrapper.style.display = "none";
    }

    setSize(width, height){

        this.chatWrapper.style.left = "0px";
        //this.chatWrapper.style.top = this.chatView.height + Math.floor(height/20) + "px";
        this.chatWrapper.style.width = Math.floor(width) + "px";
        this.chatWrapper.style.height = Math.floor(height) + "px";

    }
    

}