export class SimpleButtonWithText{
    constructor(text, passiveColor, onHoverColor){
        this.textContent = text;
        this.passiveColor = passiveColor ?? "#AA0000";
        this.onHoverColor = onHoverColor ?? "#BB3333";
        this.width = 100;
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
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        const textNode = document.createElementNS("http://www.w3.org/2000/svg", "text");

        group.setAttributeNS("http://www.w3.org/2000/svg", "viewBox", "0 0 100 100");
        rect.setAttribute("fill", this.passiveColor);
        rect.setAttribute("width", this.width);
        rect.setAttribute("height", this.height);
        
        if(this.clickable){
        rect.onmouseover = ev => {rect.setAttribute("fill", this.onHoverColor);};
        rect.onmouseout = ev => {rect.setAttribute("fill", this.passiveColor);}
        rect.onclick = ev => {this.onClick()};
        }

        textNode.textContent = this.textContent;
        textNode.setAttribute( "x", this.width/2 +"px");
        textNode.setAttribute( "y", this.height/2 + "px");
        textNode.setAttribute("fill", "white");
        textNode.setAttributeNS("http://www.w3.org/2000/svg", "dy", "-.8em");
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
    
}