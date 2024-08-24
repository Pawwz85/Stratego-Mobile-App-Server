export class SimpleButtonWithText{
    constructor(text, passiveColor, onHoverColor){
        this.textContent = text;
        this.passiveColor = passiveColor ?? "#AA0000";
        this.onHoverColor = onHoverColor ?? "#BB3333";
        this.width = 100;
        this.height = 20;
        this.textHeight = 0.1;
        this.clickable = true;
        this.onClick = () => {};
        this.element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  
        this.__init_button();

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
        rect.setAttribute("fill", this.passiveColor);
        rect.setAttribute("width", this.width );
        rect.setAttribute("height", this.height);
        
        if(this.clickable){
        rect.onmouseover = ev => {rect.setAttribute("fill", this.onHoverColor);};
        rect.onmouseout = ev => {rect.setAttribute("fill", this.passiveColor);}
        rect.onclick = ev => {this.onClick()};
        }



        textNode.textContent = this.textContent;
        textNode.setAttribute( "x", this.width/2 +"px");
        textNode.setAttribute( "y", (this.height - this.textHeight)/2 + "px");
        textNode.setAttribute("fill", "white");
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
        this.width = width;
        this.height = height;
        this.refresh();
    }
}

class SimpleIconButton{
    constructor(passiveIcon, onHoverIcon){
        this.passiveIcon = passiveIcon;
        this.onHoverIcon = onHoverIcon;
        this.width = 20;
        this.height = 20;
        this.clickable = true;
        this.onClick = () => {};
        this.element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  
        this.__init_button();
    }
    
    __clear(){
        while(this.element.firstChild)
          this.element.firstChild.remove();
      }
    
    __init_button(){

        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        const icon1  = this.passiveIcon.cloneNode();
        const icon2  = this.onHoverIcon.cloneNode();

        g.setAttributeNS("http://www.w3.org/2000/svg", "viewBox", "0 0 100 100");
        if(this.clickable){
            g.onmouseover = ev =>{
                icon1.style.display = "none";
                icon2.style.display = "block";
            };
            g.onmousedown = ev => {
                icon1.style.display = "block";
                icon2.style.display = "none";
            }
            this.clickable();
        }

        g.append(icon1);
        g.append(icon2);

        this.element.append(g)
    }

    refresh(){
        this.__clear();
        this.__init_button();
    }

    setSize(width, height){
        this.width = width;
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
        console.log(bar_style, circle_style)
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
        console.log(this.__value)
        this.__clear();
        if(this.__value)
            this.element.append(this.toggled_state.g)
         else 
            this.element.append(this.untoggled_state.g);
        
    }
}