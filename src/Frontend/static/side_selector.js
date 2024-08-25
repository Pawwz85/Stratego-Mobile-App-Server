import { appGlobalContext } from "./global_context.js";
import {ensure_await_window_stroke, SimpleButtonWithText, SimpleTogglerBuilder} from "./ui_primitives.js";
export class SideSelectorSeatModel{
  constructor(color){
    this.color = color;
    this.ownerUsername = null;
    
    this.blocked = false;
    this.ready = false;
    this.isUserOwner = false;

    this.onClaimSeat = ()=>{};
    this.onReleaseSeat = ()=>{};
    this.onReadyChange = (value) => {};
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

      this.isUserOwner = newUsername == appGlobalContext.currentUser.username;
      this.ownerUsername = newUsername;

      if(anyChange)
        this.notify_observers();
  }


  // seat can also listen on ready status
  update_ready_status(status){
    let value = false;
    if(this.color == "red") value = status.red_player;
    if(this.color == "blue") value = status.blue_player;

    if(value != this.ready)
     {
      this.ready = value;
      this.notify_observers();
     }

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

export class SideSelectorView{
  constructor(model){
    this.model = model;
    model.observers.push(this);
    this.element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.element.style.overflow = "visible";
    this.update(model);
  }

  __clear(){
    while((this.element.firstChild))
      this.element.firstChild?.remove();
  }

  refresh(){
    this.update(this.model);
  }

  __build_main_btn(model){
    const btn_pass_color = (model.color == "red") ? "#FF0000" : "#0000FF";
    const btn_hov_color = (model.color == "red") ? "#FF3F3F": "#3F3FFF";
    const is_free = model.ownerUsername == null;
    let btn_text = (model.isUserOwner) ? "Release" : "Claim";
    if(model.blocked) btn_text = "Loading..";
    
    const btn = new SimpleButtonWithText(btn_text, btn_pass_color, btn_hov_color);
    btn.clickable = (is_free || model.isUserOwner) && !model.blocked;
    btn.onClick = ()=> {
      if (is_free)
        model.onClaimSeat();
      else
      model.onReleaseSeat();

      model.block();
      setTimeout(() =>{
        model.unblock();
      }, 500);

    }
    return btn;
  }

  __ensure_ready_toggler_grad(){
    const grad_id = "ready-toggle-grad-" + this.model.color;
    if(!document.getElementById(grad_id)){
      const gradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient")
      gradient.setAttribute("id", grad_id);
      gradient.setAttributeNS(null, "x1", "0%");
      gradient.setAttributeNS(null, "y1", "0%");
      gradient.setAttributeNS(null, "y2", "0%");
      gradient.setAttributeNS(null, "x2", "100%");
      const stop1 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
      stop1.setAttribute("offset", "0%");
      stop1.setAttributeNS(null, "stop-color", "#ffffff")
      stop1.style.stopOpacity = "1"; 
      const stop2 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
      stop2.setAttribute("offset", "100%");
      stop2.setAttributeNS(null, "stop-color", this.model.color)
      stop2.style.stopOpacity = "1"; 
      gradient.appendChild(stop1)
      gradient.appendChild(stop2);
      const dev = document.createElementNS("http://www.w3.org/2000/svg", "defs")
      dev.appendChild(gradient)

      const defs = document.getElementById("svg-defs");
      defs.append(dev)
    }
  }

  __ensure_await_labels_grad(){
    const grad_id = "await-label-grad-" + this.model.color;
    const c1 = (this.model.color == "blue")? "purple": "red";
    const c2 =  (this.model.color == "blue")? "blue": "purple";
    if(!document.getElementById(grad_id)){
      const gradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient")
      gradient.setAttribute("id", grad_id);
      gradient.setAttributeNS(null, "x1", "0%");
      gradient.setAttributeNS(null, "y1", "0%");
      gradient.setAttributeNS(null, "y2", "0%");
      gradient.setAttributeNS(null, "x2", "100%");
      const stop1 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
      stop1.setAttribute("offset", "0%");
      stop1.setAttributeNS(null, "stop-color", c1)
      stop1.style.stopOpacity = "1"; 
      const stop2 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
      stop2.setAttribute("offset", "100%");
      stop2.setAttributeNS(null, "stop-color", c2)
      stop2.style.stopOpacity = "1"; 
      gradient.appendChild(stop1)
      gradient.appendChild(stop2);
      const dev = document.createElementNS("http://www.w3.org/2000/svg", "defs")
      dev.appendChild(gradient)

      const defs = document.getElementById("svg-defs");
      defs.append(dev)
    }
  }


  __build_ready_toggler(model){
    const builder = new SimpleTogglerBuilder();
    const grad_id = "ready-toggle-grad-" + this.model.color;
    
    this.__ensure_ready_toggler_grad();

    const passive_bar = {
      fill : "gray",
      rx: "5",
      ry: "5"
    }

    const active_bar = {
      fill : "url(#" + grad_id +")",
      rx: "5",
      ry: "5"
    }

    const passive_dot = {
      fill : "white"
    }

    const active_dot = {
      fill : this.model.color
    }

    const toggle = builder.set_active_state(active_bar, active_dot).set_passive_state(passive_bar, passive_dot).build();
    toggle.set_value(model.ready);
    toggle.onValueChange = (value) => {model.onReadyChange(value);};
    return toggle;
  }

  update(model){
    // Step 1. clear group
    this.__clear();

    // Step 2. Init sub components 

    const label_color = "url(#await-label-grad-" + this.model.color +")";
    this.__ensure_await_labels_grad();

    const btn = this.__build_main_btn(model);
    const toggle = this.__build_ready_toggler(model);

    const toggle_label =  document.createElementNS("http://www.w3.org/2000/svg", "text");
    toggle_label.textContent = "READY"

    const ready_title = document.createElementNS("http://www.w3.org/2000/svg", "text");
    ready_title.textContent = "READY";
    
  
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.textContent = model.color + " player" + ((model.ownerUsername)?": "+ model.ownerUsername: "");

    // Step 3. Set placement of those elements on the element

    ready_title.setAttribute("x", "50%");
    ready_title.setAttribute("y", "20%");
    ready_title.setAttributeNS(null, 'text-anchor', "middle");
    ready_title.setAttribute("fill", model.color)

    label.setAttribute("x", "50%");
    label.setAttribute("y", "40%");
    label.setAttributeNS(null, 'text-anchor', "middle");
    label.setAttribute("fill", label_color)

    toggle_label.setAttribute("fill", label_color)

    btn.width = 100;
    btn.height = 23;
    btn.element.setAttribute('y', "45%");
    
    btn.setSize(btn.width, btn.height);
  
    

    toggle_label.setAttribute("x", "25%");
    toggle_label.setAttribute("y", "90%");
    toggle_label.setAttribute("width", "25%");
    toggle_label.setAttribute("height", "10%");
    toggle_label.setAttributeNS(null, 'text-anchor', "middle");

    toggle.element.setAttribute("x", "75%");
    toggle.element.setAttribute("y", "80%");
    toggle.element.setAttribute("width", "25%");
    toggle.element.setAttribute("height", "10%");

    // Step 4. Insert relevant elements into element
    this.element.append(btn.element);
    this.element.append(label);


    if(model.isUserOwner){
      this.element.append(toggle.element);
      this.element.append(toggle_label);
    }

    if(model.ready)
      this.element.append(ready_title)

  }
  
}

export class SeatSelectorWindowModel{
  constructor(){
    this.redSeat = new SideSelectorSeatModel("red");
    this.blueSeat = new SideSelectorSeatModel("blue");
    this.onClaimSeat = color => {};
    this.onSeatRelease = color => {};
    this.onReadyChange = value => {};
    this.redSeat.onClaimSeat = () => {this.onClaimSeat("red");};
    this.blueSeat.onClaimSeat = () => {this.onClaimSeat("blue");};
    this.redSeat.onReleaseSeat = () => {this.onSeatRelease("red");};
    this.blueSeat.onReleaseSeat = () => {this.onSeatRelease("blue");};
    this.redSeat.onReadyChange = (value) => {this.onReadyChange(value)};
    this.blueSeat.onReadyChange = (value) => {this.onReadyChange(value)};
  }

  attachTableObservers(table){
    table.observers.push(this.redSeat);
    table.observers.push(this.blueSeat);

    table.notify_observers();
    this.redSeat.notify_observers();
    this.blueSeat.notify_observers();
  }

  update_ready_status(statuses){
    this.redSeat.update_ready_status(statuses)
    this.blueSeat.update_ready_status(statuses)
  }
}

export class SeatSelectorWindowView{
  constructor(model){
    this.redSeatView = new SideSelectorView(model.redSeat);
    this.blueSeatView = new SideSelectorView(model.blueSeat);
    this.window = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.__init_window();
  }

  __init_window(){
    this.window.setAttributeNS("http://www.w3.org/2000/svg", "viewBox", "0 0 100 100");
    let background = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    const stroke = "url(#await-window-stroke)";
    ensure_await_window_stroke();

    background.setAttribute("height", "100%");
    background.setAttribute("width", "100%");
    background.setAttribute("fill", "black");
    background.setAttribute("stroke", stroke);
    background.setAttribute("stroke-width", "1%");
    
    this.redSeatView.element.setAttribute("x", "5%");
    this.redSeatView.element.setAttribute("y", "20%");
    this.redSeatView.element.setAttribute("width", "40%");
    this.redSeatView.element.setAttribute("height", "80%");

    this.blueSeatView.element.setAttribute("x", "55%");
    this.blueSeatView.element.setAttribute("y", "20%");
    this.blueSeatView.element.setAttribute("width", "40%");
    this.blueSeatView.element.setAttribute("height", "80%");
    
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.textContent = "Player Info"
    label.style.fill = stroke;
    label.setAttribute("x", "50%");
    label.setAttribute("y", "20%");
    label.setAttribute("text-anchor", "middle");
    this.window.append(background);
    this.window.append(this.redSeatView.element);
    this.window.append(this.blueSeatView.element);
    this.window.append(label);

    this.__compose();
  }


  __compose(){
    const margin = 5.0;
    const seat_width = 30.0;
    const height = 80.0;

     this.redSeatView.element.setAttribute("x", (margin)+"%");
     this.blueSeatView.element.setAttribute("x", + (100 - margin - seat_width) +"%");

     this.redSeatView.element.setAttribute("y", margin+"%");
     this.blueSeatView.element.setAttribute("y", margin +"%");

     this.redSeatView.element.setAttribute("width", seat_width+"%");
     this.blueSeatView.element.setAttribute("width", seat_width+"%");


     this.redSeatView.element.setAttribute("height", height+"%");
     this.blueSeatView.element.setAttribute("height", height+"%");
  }

  setSize(width, height){
    this.window.style.width = width + "px";
    this.window.style.height = height + "px";
     
     
     //this.redSeatView.refresh();
    // this.blueSeatView.refresh();
  }
}