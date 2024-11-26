import { appGlobalContext } from "./global_context.js";
import {SVGHorizontalGradient, SimpleButtonWithText, SimpleTogglerBuilder} from "./ui_primitives.js";
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
      console.log(this, appGlobalContext)
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

const defaultSideSelectorViewConfig = {
  btn_width: 100,
  btn_height: 25,
  btn_x: "15%",
  btn_y: "50%",
  btn_text_if_user_owner: "Release",
  btn_text_if_user_not_owner: "Claim",
  btn_text_loading: "Loading..",
  btn_passive_color: "#777777",
  btn_hover_color: "#AAAAAA",
  btn_blocked_color: "gray",
  btn_config: {rx: "8", ry:"8", height:"40"},

  toggle_x: "55%",
  toggle_y: "82.5%",
  toggle_width: "25%",
  toggle_height: "10%",
  toggle_passive_bar: {fill: "gray"},
  toggle_active_bar:  {fill: SVGHorizontalGradient(["#ffffff", "gray"])},
  toggle_passive_dot: {fill: "white"},
  toggle_active_dot:  {fill: "gray"},

  toggle_label_x: "25%",
  toggle_label_y: "90%",
  toggle_label_width: "25%",
  toggle_label_height: "10%",
  toggle_label_fill: "gray",
 
  label_x: "50%",
  label_y: "40%",
  label_fill: "gray",

  ready_title_x: "50%",
  ready_title_y: "20%",
  ready_title_fill: "gray"
}

const defaultSideSelectorViewConfigForRed = {
  ...defaultSideSelectorViewConfig,
  btn_passive_color: "#FF0000",
  btn_hover_color: "#FF3F3F",


  toggle_passive_bar: {fill: "gray"},
  toggle_active_bar:  {fill: SVGHorizontalGradient(["#ffffff", "red"])},
  toggle_passive_dot: {fill: "white"},
  toggle_active_dot:  {fill: "red"},
  
  toggle_label_fill: SVGHorizontalGradient(["red", "purple"]),
  label_fill: SVGHorizontalGradient(["red", "purple"]),
  ready_title_fill: "red"
}

const defaultSideSelectorViewConfigForBlue = {
  ...defaultSideSelectorViewConfig,
  btn_passive_color: "#0000FF",
  btn_hover_color: "#3F3FFF",

  toggle_passive_bar: {fill: "gray"},
  toggle_active_bar:  {fill: SVGHorizontalGradient(["#ffffff", "blue"])},
  toggle_passive_dot: {fill: "white"},
  toggle_active_dot:  {fill: "blue"},
  
  toggle_label_fill: SVGHorizontalGradient(["purple", "blue"]),
  label_fill: SVGHorizontalGradient(["purple", "blue"]),
  ready_title_fill: "blue"
}


export class SideSelectorView{
  constructor(model, config = defaultSideSelectorViewConfig){
    this.model = model;
    this.config = {...defaultSideSelectorViewConfig, ...config};
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
    const is_free = model.ownerUsername == null;
    let btn_text = (model.isUserOwner) ? this.config.btn_text_if_user_owner : this.config.btn_text_if_user_not_owner;
    if(model.blocked) btn_text = "Loading..";
    
    const btn_config_from_config = this.config.btn_config;
    const btn_cnfg = {
      ...defaultSideSelectorViewConfig.btn_config,
      ...btn_config_from_config,
      text: btn_text,
      passiveColor: (is_free || model.isUserOwner)? this.config.btn_passive_color : this.config.btn_blocked_color,
      onHoverColor: (is_free || model.isUserOwner)? this.config.btn_hover_color: this.config.btn_blocked_color,
    }

    const btn = new SimpleButtonWithText(btn_cnfg);
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

  __build_ready_toggler(model){
    const builder = new SimpleTogglerBuilder();    
    const config = this.config;

    const passive_bar = {
      ...defaultSideSelectorViewConfig.passive_bar,
      ...config.toggle_passive_bar,
      rx: "5",
      ry: "5"
    }

    const active_bar = {
      ...defaultSideSelectorViewConfig.actiive_bar,
      ...config.toggle_active_bar,
      rx: "5",
      ry: "5"
    }

    const passive_dot = {
      ...defaultSideSelectorViewConfig.toggle_passive_dot,
      ...config.toggle_passive_dot
    }

    const active_dot = {
      ...defaultSideSelectorViewConfig.toggle_active_dot,
      ...config.toggle_active_dot
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
    const label_color = this.config.label_fill;

    const btn = this.__build_main_btn(model);
    const toggle = this.__build_ready_toggler(model);

    const toggle_label =  document.createElementNS("http://www.w3.org/2000/svg", "text");
    toggle_label.textContent = "READY"

    const ready_title = document.createElementNS("http://www.w3.org/2000/svg", "text");
    ready_title.textContent = "READY";
    
  
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.textContent = model.ownerUsername?model.ownerUsername: "";

    // Step 3. Set placement of those elements on the element

    ready_title.setAttribute("x", this.config.ready_title_x);
    ready_title.setAttribute("y", this.config.ready_title_y);
    ready_title.setAttributeNS(null, 'text-anchor', "middle");
    ready_title.setAttribute("fill", this.config.ready_title_fill);

    label.setAttribute("x", this.config.label_x);
    label.setAttribute("y", this.config.label_y);
    label.setAttributeNS(null, 'text-anchor', "middle");
    label.setAttribute("fill", this.config.label_fill)

    btn.width = this.config.btn_width;
    btn.height = this.config.btn_height;
    btn.element.setAttribute('y', this.config.btn_y);
    btn.element.setAttribute('x', this.config.btn_x);
    btn.setSize(btn.width, btn.height);
  
 
    toggle_label.setAttribute("x", this.config.toggle_label_x);
    toggle_label.setAttribute("y", this.config.toggle_label_y);
    toggle_label.setAttribute("width", this.config.toggle_label_width);
    toggle_label.setAttribute("height", this.config.toggle_label_height);
    toggle_label.setAttribute("fill", this.config.toggle_label_fill);
    toggle_label.setAttributeNS(null, 'text-anchor', "middle");

    toggle.element.setAttribute("x", this.config.toggle_x);
    toggle.element.setAttribute("y", this.config.toggle_y);
    toggle.element.setAttribute("width", this.config.toggle_width);
    toggle.element.setAttribute("height", this.config.toggle_height);

    // Step 4. Insert relevant elements into element
    
    this.element.append(label);
    this.element.append(btn.element);

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

const defaultSideSelectorWindowConfig = {
  win_rx: 10,
  win_ry: 10,

  stroke: null,
  stroke_width: "0%",
  background_fill: "black",
  red_seat_x: "5%",
  blue_seat_x: "65%",
  seat_y: "5%",
  seat_width:  "30%",
  seat_height: "80%",
  label: "Player Info",
  label_fill: "#C084FC",
  label_x: "50%",
  label_y: "10%",
  red_seat_view_config: {},
  blue_seat_view_config: {},
}

export class SeatSelectorWindowView{
  constructor(model, config = defaultSideSelectorWindowConfig){
    this.config = {...defaultSideSelectorWindowConfig, ...config};
    this.redSeatView = new SideSelectorView(model.redSeat, {...defaultSideSelectorViewConfigForRed, ...config.red_seat_view_config});
    this.blueSeatView = new SideSelectorView(model.blueSeat, {...defaultSideSelectorViewConfigForBlue, ...config.blue_seat_view_config});
    this.window = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.__init_window();
  }

  __init_window(){
    this.window.setAttributeNS("http://www.w3.org/2000/svg", "viewBox", "0 0 100 100");
    let background = document.createElementNS("http://www.w3.org/2000/svg", "rect");

    background.setAttribute("height", "100%");
    background.setAttribute("width", "100%");
    background.setAttribute("fill", this.config.background_fill);
    background.setAttribute("stroke", this.config.stroke);
    background.setAttribute("stroke-width", this.config.stroke_width);
    background.setAttribute("rx", this.config.win_rx);
    background.setAttribute("ry", this.config.win_ry);

    this.redSeatView.element.setAttribute("x", this.config.red_seat_x);
    this.redSeatView.element.setAttribute("y", this.config.seat_y);
    this.redSeatView.element.setAttribute("width", this.config.seat_width);
    this.redSeatView.element.setAttribute("height", this.config.seat_height);

    this.blueSeatView.element.setAttribute("x", this.config.blue_seat_x);
    this.blueSeatView.element.setAttribute("y", this.config.seat_y);
    this.blueSeatView.element.setAttribute("width", this.config.seat_width);
    this.blueSeatView.element.setAttribute("height", this.config.seat_height);

    
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.textContent = this.config.label;
    label.style.fill = this.config.label_fill;
    label.setAttribute("x", this.config.label_x);
    label.setAttribute("y", this.config.label_y);
    label.setAttribute("text-anchor", "middle");
    this.window.append(background);
    this.window.append(this.redSeatView.element);
    this.window.append(this.blueSeatView.element);
    this.window.append(label);

    this.__compose();
  }


  __compose(){/*
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
     this.blueSeatView.element.setAttribute("height", height+"%");*/
  }

  setSize(width, height){
    this.window.style.width = width + "px";
    this.window.style.height = height + "px";
     
     
     //this.redSeatView.refresh();
    // this.blueSeatView.refresh();
  }
}