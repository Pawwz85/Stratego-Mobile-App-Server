import { appGlobalContext } from "./global_context.js";
import {SimpleButtonWithText} from "./ui_primitives.js";
export class SideSelectorSeatModel{
  constructor(color){
    this.color = color;
    this.ownerUsername = null;
    this.blocked = false;
    this.onClaimSeat = ()=>{};
    this.onReleaseSeat = ()=>{};
    this.observers = []
  
  }

  // SideSelectorSeatModel is valid table observer
  update(table){
      let owner = null;
      let anyChange = false;
      
      if(this.color == "red")
        owner = table.red_player;
      
      if(this.color == "blue")
        owner = table.blue_player;
      
      const newUsername = owner?.username ?? null;
      anyChange = anyChange || newUsername != this.ownerUsername;

      this.ownerUsername = newUsername;
      if(anyChange)
        this.notify_observers();
  }

  block(){
    if(!this.blocked){
      this.blocked = true;
      this.notify_observers();
    }
  }

  unblock(){
    if(this.blocked){
      this.blocked = false;
      this.notify_observers();
    }
  }

  notify_observers(){
    for (let obs of this.observers)
      obs.update(this);
  }

}

export class SideSelectorSeatView{
  constructor(model, color, onHoverColor){
    this.model = model;
    this.width = 100;
    this.height = 20;
    this.color = color ?? model.color;
    this.onHoverColor = onHoverColor ?? this.color;

    this.element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.model.observers.push(this);
    this.refresh();
  }

  __clear(){
    while(this.element.firstChild)
      this.element.firstChild.remove();
  }

  __create_rect(){
    let result = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    result.setAttribute( "width", this.width);
    result.setAttribute( "height", this.height);
    result.setAttribute( "fill", this.color);
    return result;
  }

  __render_button(text, on_click = null){
    const passiveColor = this.color;
    const hoverColor = this.onHoverColor;
    let result = new SimpleButtonWithText(text, passiveColor, hoverColor);
    if(on_click){
          result.onClick = on_click;
    } else{
      result.clickable = false;
    }

    result.setSize(this.width, this.height);
    return result.element;
  }

  __render_owned_by_other_player(){
    const username = (this.model.ownerUsername == "CLAIM")? "" : this.model.ownerUsername;

    return this.__render_button(this.model.ownerUsername);
  }

  __render_owned_by_user(){
    const username = (this.model.ownerUsername == "CLAIM")? "" : this.model.ownerUsername;
    const callback = () =>{
      this.model.onReleaseSeat();
      this.model.block();
      setTimeout(()=>{this.model.unblock();}, 500);

    }
    return this.__render_button("RELEASE", callback);
  }
  __render_owned_by_nobody(){
    const callback = ev => {
      this.model.onClaimSeat();
      this.model.block();
      setTimeout(()=>{this.model.unblock();}, 500);
    }
    return this.__render_button("CLAIM", callback);
  }

  __render_blocked(){
    // TODO: replace loading with animated circle
    return this.__render_button("LOADING...");
  }

  update(model){
    this.__clear();

    let renderer = this.__render_owned_by_nobody;
    const currentUser = appGlobalContext?.currentUser?.username ?? null;

    if(model.ownerUsername != null && model.ownerUsername != currentUser) renderer = this.__render_owned_by_other_player;
    if(model.ownerUsername == null) renderer = this.__render_owned_by_nobody;
    if(model.ownerUsername == currentUser) renderer = this.__render_owned_by_user;
    if(model.blocked) renderer = this.__render_blocked;
    
    renderer = renderer.bind(this);

    this.element.append(renderer());
  }

  setSize(width, height){
    this.width = width;
    this.height = height;
    this.refresh();
  }

  refresh(){
    this.update(this.model);
  }
}

class ReadyButton{
  constructor(){
    this.button = new SimpleButtonWithText("START");

    this.readyValue = false;

    this.on_ready = () => {}
    this.on_not_ready = () => {}

    this.primary_color = "#007700";
    this.secondary_color = "#33AA33";
  }

  refresh(){
    this.button.passiveColor = this.primary_color;
    this.button.onHoverColor = this.secondary_color;

    this.button.refresh();
  }
}

export class SeatSelectorWindowModel{
  constructor(){
    this.redSeat = new SideSelectorSeatModel("red");
    this.blueSeat = new SideSelectorSeatModel("blue");
    this.onClaimSeat = color => {};
    this.onSeatRelease = color => {};
    this.redSeat.onClaimSeat = () => {this.onClaimSeat("red");};
    this.blueSeat.onClaimSeat = () => {this.onClaimSeat("blue");};
    this.redSeat.onReleaseSeat = () => {this.onSeatRelease("red");};
    this.blueSeat.onReleaseSeat = () => {this.onSeatRelease("blue");};
  }

  attachTableObservers(table){
    table.observers.push(this.redSeat);
    table.observers.push(this.blueSeat);

    table.notify_observers();
    this.redSeat.notify_observers();
    this.blueSeat.notify_observers();
  }
}

export class SeatSelectorWindowView{
  constructor(model){
    this.redSeatView = new SideSelectorSeatView(model.redSeat, "#AA0000", "#BB3333");
    this.blueSeatView = new SideSelectorSeatView(model.blueSeat, "#0000AA", "#3333BB");
    this.window = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.__init_window();
  }

  __init_window(){
    this.window.setAttributeNS("http://www.w3.org/2000/svg", "viewBox", "0 0 100 100");
    let background = document.createElementNS("http://www.w3.org/2000/svg", "rect");

    background.setAttribute("height", "100%");
    background.setAttribute("width", "100%");
    background.setAttribute("fill", "white");
    background.setAttribute("stroke", "black");
    background.setAttribute("stroke-width", "4%");
    this.redSeatView.element.setAttribute("y", "10%");
    this.blueSeatView.element.setAttribute("y", "50%");
    
    this.window.append(background);
    this.window.append(this.redSeatView.element);
    this.window.append(this.blueSeatView.element);
  }

  setSize(width, height){
    this.window.style.width = width + "px";
    this.window.style.height = height + "px";

    this.redSeatView.element.setAttribute("x", +width*0.1+"px");
    this.blueSeatView.element.setAttribute("x", +width*0.1+"px");
    this.redSeatView.width = this.blueSeatView.width = width * 0.8;
    this.redSeatView.height = this.blueSeatView.height = height / 3;
    this.redSeatView.refresh();
    this.blueSeatView.refresh();
  }
}