import { appGlobalContext, User } from "./global_context.js";
import {SimpleTogglerBuilder, SVGHorizontalGradient} from "./ui_primitives.js";
/*

*/

// TODO: connect toggle to rematch functionality 
export class RematchWindowModel {

    constructor(){
        this.winner = null; // winner of a game
        this.isRedWillingForRematch = false;
        this.isBlueWillingForRematch = false;
        this.isUserPlayer = false;
        this.isUserWillingToRematch  = false; 
        this.observers = [];

        this.onUserRematchWillingnessChange = value => {};
    }

    notify_observers(){
        
        for (let o of this.observers)
            o.update(this);
    }

    // RematchWindowModel is valid WinnerLiveImage observer
    update_winner(winner){
        this.winner = winner;
        this.notify_observers();
    }

    // RematchWindowModel is valid RematchWillingnessLiveImage observer
    update_rematch_status(rematch_willingness){
        this.isRedWillingForRematch = false;
        this.isBlueWillingForRematch = false;
        for( let side of rematch_willingness){
            if (side == "red")
                this.isRedWillingForRematch = true;
            if (side == "blue")
                this.isBlueWillingForRematch = true;
        }
        this.update_current_user(appGlobalContext.currentUser);
        this.notify_observers();
    }

    update_current_user(user){
        
        this.isUserPlayer = false;

        if(user.boardrole == "red_player"){
            this.isUserPlayer = true;
            this.isUserWillingToRematch = this.isRedWillingForRematch;
        }
            

        if(user.boardrole == "blue_player"){
            this.isUserPlayer = true;
            this.isUserWillingToRematch = this.isBlueWillingForRematch;
        }
        console.log(this, user)
        this.notify_observers();

    }
}

const defaultRematchWindowConfig = {
    window_stroke: SVGHorizontalGradient(["red", "white", "blue"]),
    window_stroke_width: "1%",
    window_fill: "black",
    
    label_x: "50%",
    label_y: "20%",
    label_fill: SVGHorizontalGradient(["red", "blue"]),

    red_player_label_x: "25%",
    red_player_label_y: "30%",
    red_player_label_text: "Red Player",
    red_player_label_fill: SVGHorizontalGradient(["red", "purple"]),

    blue_player_label_x: "75%",
    blue_player_label_y: "30%",
    blue_player_label_text: "Blue Player",
    blue_player_label_fill: SVGHorizontalGradient(["purple", "blue"]),

    red_player_rematch_status_label_x: "25%",
    red_player_rematch_status_label_y: "45%",
    red_player_rematch_status_label_text: "Wants Rematch",
    red_player_rematch_status_label_fill: SVGHorizontalGradient(["red", "purple"]),

    blue_player_rematch_status_label_x: "75%",
    blue_player_rematch_status_label_y: "45%",
    blue_player_rematch_status_label_text: "Wants Rematch",
    blue_player_rematch_status_label_fill: SVGHorizontalGradient(["purple", "blue"]),

    toggle_label_x: "35%",
    toggle_label_y: "75%",
    toggle_label_fill: SVGHorizontalGradient(["red", "blue"]),
    toggle_label_text: "Rematch?",

    toggle_x: "55%",
    toggle_y: "67.75%",
    toggle_width: "10%",
    toggle_height: "5%",
    toggle_passive_bar_fill: "gray",
    toggle_active_bar_fill: SVGHorizontalGradient(["#ffffff", "gray"]),
    toggle_passive_dot_fill:  "white",
    toggle_active_dot_fill: "gray",
}

export class RematchWindowView {
    constructor(rematchWindowModel, config = defaultRematchWindowConfig) {
        this.config = {...defaultRematchWindowConfig, ...config};
        this.model = rematchWindowModel;
        rematchWindowModel.observers.push(this);
        this.element =  null;
        
        this.__background = this.__init_background();
        this.__init_window();
        this.refresh();
    }

    __clear(){
        while((this.element.firstChild))
          this.element.firstChild?.remove();
      }
    
    __init_window(){
        this.element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        
        //this.element.style.overflow = "visible";
        this.element.setAttributeNS(null, "viewBox", "0 0 100 100");

    }

    __init_background(){
        const background = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        const stroke = "url(#default-window-stroke)"; 
        background.setAttribute("height", "100%");
        background.setAttribute("width", "100%");
        background.setAttribute("fill", this.config.window_fill);
        background.setAttribute("stroke", this.config.window_stroke);
        background.setAttribute("stroke-width", this.config.window_stroke_width);
        return background;
    }

    //TODO: refactor this function
    update(rematchWindowModel){
        console.log(rematchWindowModel)
        // step 1. clear element and init blakc background
        this.__clear();


        //step 2. Create individual elements
        const win_status = document.createElementNS("http://www.w3.org/2000/svg", "text");
        const red_player_label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        const blue_player_label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        const red_player_rematch_status = document.createElementNS("http://www.w3.org/2000/svg", "text");
        const blue_player_rematch_status = document.createElementNS("http://www.w3.org/2000/svg", "text");
        const rematch_toggle_label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        const rematch_toggle = this.__build_toggler(rematchWindowModel);
        // TODO: create rematch button here

        // step 3. Initialise their properties

        // 3.1 - gradients
        win_status.style.fill = this.config.label_fill;
        red_player_label.style.fill = this.config.red_player_label_fill;
        red_player_rematch_status.style.fill = this.config.red_player_rematch_status_label_fill;
        blue_player_label.style.fill = this.config.blue_player_label_fill;
        blue_player_rematch_status.style.fill = this.config.blue_player_rematch_status_label_fill;
        rematch_toggle_label.style.fill = this.config.toggle_label_fill;

        //3.2 - text content
        let winner_status = "";
        if(rematchWindowModel.winner == null){
            winner_status = "Tie";
        } else {
            // TODO: query seat model to get player username
            winner_status = rematchWindowModel.winner + "  won";
        }

        win_status.textContent = winner_status;
        red_player_label.textContent = this.config.red_player_label_text; // TODO: query seat model to get player
        blue_player_label.textContent = this.config.blue_player_label_text;// TODO: query seat model to get player
        red_player_rematch_status.textContent = this.config.red_player_rematch_status_label_text;
        blue_player_rematch_status.textContent = this.config.blue_player_rematch_status_label_text;
        rematch_toggle_label.textContent = this.config.toggle_label_text;

        //step 4. Arrange those elements
        win_status.setAttributeNS(null, "x", this.config.label_x);
        win_status.setAttributeNS(null, "y", this.config.label_y);
        win_status.setAttributeNS(null, 'text-anchor', "middle");

        red_player_label.setAttributeNS(null, "x", this.config.red_player_label_x);
        red_player_label.setAttributeNS(null, "y", this.config.red_player_label_y);
        //red_player_label.setAttributeNS(null, "textLength", "25%");
        //red_player_label.setAttributeNS(null, "lengthAdjust", "spacingAndGlyphs");
        red_player_label.setAttributeNS(null, 'text-anchor', "middle");

        blue_player_label.setAttributeNS(null, "x", this.config.blue_player_label_x);
        blue_player_label.setAttributeNS(null, "y", this.config.blue_player_label_y);
        blue_player_label.setAttributeNS(null, 'text-anchor', "middle");

        red_player_rematch_status.setAttributeNS(null, "x", this.config.red_player_rematch_status_label_x);
        red_player_rematch_status.setAttributeNS(null, "y", this.config.blue_player_rematch_status_label_y);
        //red_player_rematch_status.setAttributeNS(null, "textLength", "12.5%");
        //red_player_rematch_status.setAttributeNS(null, "lengthAdjust", "spacingAndGlyphs");
        red_player_rematch_status.setAttributeNS(null, 'text-anchor', "middle");

        blue_player_rematch_status.setAttributeNS(null, "x", this.config.blue_player_rematch_status_label_x);
        blue_player_rematch_status.setAttributeNS(null, "y", this.config.blue_player_rematch_status_label_y);
        blue_player_rematch_status.setAttributeNS(null, 'text-anchor', "middle");

        rematch_toggle_label.setAttributeNS(null, "x", this.config.toggle_label_x);
        rematch_toggle_label.setAttributeNS(null, "y", this.config.toggle_label_y);
        rematch_toggle_label.setAttributeNS(null, 'text-anchor', "middle");

        rematch_toggle.element.setAttributeNS(null, "x", this.config.toggle_x);
        rematch_toggle.element.setAttributeNS(null, "y", this.config.toggle_y);
        rematch_toggle.element.setAttributeNS(null, "width", this.config.toggle_width);
        rematch_toggle.element.setAttributeNS(null, "height", this.config.toggle_height);
        // Step 5. Hide remath_status if players are not willing to rematch

        if(!rematchWindowModel.isBlueWillingForRematch)
            blue_player_rematch_status.style.display = "none";

        if(!rematchWindowModel.isRedWillingForRematch)
            red_player_rematch_status.style.display = "none";
        

        // step 5. Append new elements to window
        this.element.appendChild(this.__background);
        this.element.appendChild(win_status);
        this.element.appendChild(red_player_label);
        this.element.appendChild(blue_player_label);
        this.element.appendChild(red_player_rematch_status);
        this.element.appendChild(blue_player_rematch_status);

        if(rematchWindowModel.isUserPlayer){
            this.element.appendChild(rematch_toggle_label);
            this.element.appendChild(rematch_toggle.element);
        }
        
    }

    refresh(){
        this.update(this.model);
    }

    setSize(width, height){
        this.element.style.width = width + "px";
        this.element.style.height = height + "px";
        const vievBox = "0 0 " + width + " " + height;
        this.element.setAttributeNS(null, "viewBox", vievBox); // No idea why this is neccessary here, but not in seat selector
      }
    
      __build_toggler(model){
        const builder = new SimpleTogglerBuilder();
        const grad_id = this._purple_blue_grad;
        
        const passive_bar = {
          fill : this.config.toggle_passive_bar_fill,
          rx: "5",
          ry: "5"
        }
    
        const active_bar = {
          fill : this.config.toggle_active_bar_fill,
          rx: "5",
          ry: "5"
        }
    
        const passive_dot = {
          fill : this.config.toggle_passive_dot_fill
        }
    
        const active_dot = {
          fill : this.config.toggle_active_dot_fill
        }
    
        const toggle = builder.set_active_state(active_bar, active_dot).set_passive_state(passive_bar, passive_dot).build();
        toggle.set_value(model.isUserWillingToRematch);
        toggle.onValueChange = model.onUserRematchWillingnessChange;
        return toggle;
      }
}