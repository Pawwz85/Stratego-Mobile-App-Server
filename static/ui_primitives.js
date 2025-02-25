
export const defaultSimpleButtonConfig = {
    id: undefined,
    text: "Click Me!", // Text
    width: 100, // Width as percentage, use it to modify width/height ratio
    height: 20, // Height as as percentage, use it to modify width/height ratio
    rx: 0,
    ry: 0,
    passiveColor: "#AA0000",
    onHoverColor: "#BB3333",
    text_fill: "white",
    textHeight: 0.1 // text height as fraction button height and canvas maximum height (100)
  };


export class SimpleButtonWithText{
    constructor(config){
        this.clickable = true;
        this.onClick = () => {};
        this.element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this.configure(config);
    }

    configure(config) {
        this.config = {...defaultSimpleButtonConfig, ...config};
        this.textContent = this.config.text;
        this.passiveColor = this.config.passiveColor;
        this.onHoverColor = this.config.onHoverColor;
        this.width = this.config.width;
        this.height = this.config.height;
        this.textHeight = this.config.textHeight;
        this.textFill = this.config.text_fill;
        
        if (typeof (this.config.id) != "undefined")
            this.element.setAttribute("id", this.config.id);
        else 
            this.element.removeAttribute("id");
        
        this.refresh();
    }

    __clear(){
        while(this.element.firstChild)
          this.element.firstChild.remove();
      }
    
    __init_button(){
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        const textNode = document.createElementNS("http://www.w3.org/2000/svg", "text");
        group.setAttributeNS("http://www.w3.org/2000/svg", "viewBox", "0 0 100 100");
        rect.setAttribute("fill", this.config.passiveColor);
        rect.setAttribute("width", this.config.width  + "%");
        rect.setAttribute("height", this.config.height + "%");
        rect.setAttribute("rx", this.config.rx);
        rect.setAttribute("ry", this.config.ry);

        if(this.clickable){
        rect.onmouseover = ev => {rect.setAttribute("fill", this.config.onHoverColor);};
        rect.onmouseout = ev => {rect.setAttribute("fill", this.config.passiveColor);}
        rect.onclick = ev => {this.onClick()};
        }



        textNode.textContent = this.config.text;
        textNode.setAttribute( "x", this.config.width/2 +"%");
        textNode.setAttribute( "y", (this.config.height - this.config.textHeight)/2 + "%");
        textNode.setAttribute("fill", this.config.text_fill);
        textNode.setAttributeNS(null, "dy", ".4em");
        textNode.setAttributeNS(null, "text-anchor", "middle");
        textNode.setAttribute("unselectable", "on");
        textNode.style.pointerEvents = "none";
        textNode.style.userSelect = "none";


        group.append(rect);
        group.append(textNode);
        this.element.append(group);
    }

    refresh(){
        this.__clear();
        this.__init_button();
    }

    setSize(width, height){
        this.element.style.width = width;
        this.height = height;
        this.refresh();
    }
}


/*
    A small helper class
*/
class __SimpleTogglerState{
    constructor(progress = 0.2, bar_style = {}, circle_style = {}){
        this.__progress = progress;

        this.g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        this.g.setAttributeNS("http://www.w3.org/2000/svg", "viewBox", "0 0  100 100");
        
        this.__init(bar_style, circle_style);
    }

    __init(bar_style, circle_style){
       const bar = document.createElementNS("http://www.w3.org/2000/svg", "rect");
       const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
       const p = 0.95; 
       bar.setAttributeNS(null, 'width', "100%");
       bar.setAttributeNS(null, 'height', 100*p+"%");
       bar.setAttributeNS(null, "y", 100 * (1-p)/2 + "%"); 

       circle.setAttributeNS(null, "r", "33%"); 
       circle.setAttributeNS(null, "cx", 100 * (this.__progress) + "%"); 
       circle.setAttributeNS(null, "cy",  "50%"); 

       for (let prop in bar_style) if (bar_style.hasOwnProperty(prop)){
        try {
            bar.style[prop] =  bar_style[prop];
        } catch (error) {}
       }
        

       for (let prop in circle_style) if (circle_style.hasOwnProperty(prop)) try {
            circle.style[prop] = circle_style[prop]
       } catch(_) {}
        
        

       this.g.append(bar);
       this.g.append(circle);
    }
}

export class SimpleTogglerBuilder{
    constructor(){
        this.passive_bar = {};
        this.passive_dot = {};
        this.active_bar = {};
        this.active_dot = {};
    }

    set_passive_state(bar_props = {}, dot_prop = {}){
        this.passive_bar = bar_props;
        this.passive_dot = dot_prop;
        return this;
    }

    set_active_state(bar_props = {}, dot_prop = {}){
        this.active_bar = bar_props;
        this.active_dot = dot_prop;
        return this;
    }

    build(){
        const passive_state = new __SimpleTogglerState(0.05, this.passive_bar, this.passive_dot);
        const active_state = new __SimpleTogglerState(0.95, this.active_bar, this.active_dot);
        return new UIToggle(passive_state, active_state);
    }
}

class UIToggle{
    constructor(state1, state2){
        this.__value = false;
        this.untoggled_state = state1;
        this.toggled_state = state2;
        this.onValueChange = (value) => {};

        this.element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this.element.style.overflow = "visible"
        this.element.onclick = () => {this.onValueChange(!this.__value)};
        this.redraw();
    }

    __clear(){
            while(this.element.firstChild)
              this.element.firstChild.remove();
    }

    set_value(val){
        this.__value = val;
        this.redraw();
    }

    get_value(){
        return this.__value;
    }

    redraw(){
        this.__clear();
        if(this.__value)
            this.element.append(this.toggled_state.g)
         else 
            this.element.append(this.untoggled_state.g);
        
    }
}

export function ensure_window_stroke(){
    const grad_id = "default-window-stroke";
    const c1 = "red";
    const c2 = "white";
    const c3 =  "blue";
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
      stop2.setAttribute("offset", "50%");
      stop2.setAttributeNS(null, "stop-color", c2);
      stop2.style.stopOpacity = "1"; 
      const stop3 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
      stop3.setAttribute("offset", "100%");
      stop3.setAttributeNS(null, "stop-color", c3)
      stop3.style.stopOpacity = "1"; 
      gradient.appendChild(stop1)
      gradient.appendChild(stop2);
      gradient.appendChild(stop3);
      const dev = document.createElementNS("http://www.w3.org/2000/svg", "defs")
      dev.appendChild(gradient)

      const defs = document.getElementById("svg-defs");
      defs.append(dev)
    }
  }

  export class GradientBuilder{
    constructor(){
        this.__grad_id = null;
        this.__x1 = null;
        this.__y1 = null;
        this.__x2 = null;
        this.__y2 = null;

        this.critical_points = []; // object with fields offset, and color
    }

    reset(){
        this.__grad_id = null;
        this.__x1 = null;
        this.__y1 = null;
        this.__x2 = null;
        this.__y2 = null;
        this.critical_points = [];
    }

    set_start(x, y){
        if (this.__x1 != null || this.__y1 != null)
            throw new Error("Step already taken");
        this.__x1 = x;
        this.__y1 = y;
        return this;
    }

    set_end(x, y){
        if (this.__x2 != null || this.__y2 != null)
            throw new Error("Step already taken");
        this.__x2 = x;
        this.__y2 = y;
        return this;
    }

    add_critical_point(offset, color){
        this.critical_points.push({
            color: color,
            offset: offset
        });
        return this;
    }

    __create_id(){
        let id = "grad_" + this.__x1 + "_" + this.__y1 + this.__x2 + "_" + this.__y2;

        for (let p of this.critical_points){
            id = id + "_" + p.color + "_" + p.offset;
        }

        id = id.replaceAll(/[^0-9a-zA-Z]/g, ''); // remove %s and other special chars

        this.__grad_id = id;

    }
    
    __ensure_gradient(){
        if(!document.getElementById(this.__grad_id)){
            const gradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
            gradient.setAttribute("id", this.__grad_id);
            gradient.setAttributeNS(null, "x1", this.__x1);
            gradient.setAttributeNS(null, "y1", this.__y1);
            gradient.setAttributeNS(null, "y2", this.__y2);
            gradient.setAttributeNS(null, "x2", this.__x2);

            for (let p of this.critical_points) {
                let stop = document.createElementNS("http://www.w3.org/2000/svg", "stop");
                stop.setAttribute("offset", p.offset);
                stop.setAttributeNS(null, "stop-color", p.color);
                stop.style.stopOpacity = "1"; 
                gradient.appendChild(stop);
            }
            
            const dev = document.createElementNS("http://www.w3.org/2000/svg", "defs")
            dev.appendChild(gradient)
            const defs = document.getElementById("svg-defs");
            defs.append(dev)
        }
    }

    build(){
        
        this.__create_id();

        this.__ensure_gradient();
        return "url(#" + this.__grad_id + ")";

    }

  }

  /*
    Expectes a list of valid "stop_color" arguments for an SVG stop.
    Returns a url to gradient.
  */
export function SVGHorizontalGradient(color_list){
    const builder = new GradientBuilder();
    builder.set_start("0%", "0%").set_end("100%", "0%");
    const n = color_list.length;
    for (let i =0 ; i<n; ++i){
        builder.add_critical_point(Math.floor(i/(n-1)*100) +"%", color_list[i]);
    }
    return builder.build();
}

export function SVGVerticalGradient(color_list){
    const builder = new GradientBuilder();
    builder.set_start("0%", "0%").set_end("0%", "100%");
    const n = color_list.length;
    for (let i =0 ; i<n; ++i){
        builder.add_critical_point(Math.floor(i/(n-1)*100) +"%", color_list[i]);
    }
    return builder.build();
}