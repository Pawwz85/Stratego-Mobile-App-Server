import "./board_model";

interface SidePanelModelObserver{
    update(model: SidePanelModel): void;
}

class SidePanelModel{
    public actions : Array<()=> void>;
    public colors : Array<string>;
    public observers : Array<SidePanelModelObserver>;
    public passiveColor = "white";
    public encourageColor = "gray";
    public specialColor = "green";

    constructor(){
        this.actions = [];
        this.colors = []
        this.observers = [];
    }

    addAction(action: any){
       this.actions.push(action);
       this.colors.push(this.passiveColor);
       this.notifyObservers();
    }

    mark(index: number){
        if (this.colors[index] !=  this.encourageColor){
            this.colors[index] = this.encourageColor;
           this.notifyObservers();
       } 
    }

    markAsSpecial(index: number){
        if (this.colors[index] !=  this.specialColor){
            this.colors[index] = this.specialColor;
            this.notifyObservers();
        }  
    }

    unmark(index: number){
        if (this.colors[index] != this.passiveColor){
            this.colors[index] = this.passiveColor;
            this.notifyObservers();
        }
    }

    clearMarks(){
        let refresh = false;
        for(let i= 0; i < this.colors.length; ++i ){
            let color = this.colors[i];
            refresh = refresh || color != this.passiveColor;
            this.colors[i] = this.passiveColor;
        }
        if(refresh)
            this.notifyObservers();
    }

    changeColorPalet(passiveColor : string, encourageColor : string, specialColor : string){
        const helperMap = new Map();
        helperMap.set(this.passiveColor, passiveColor);
        helperMap.set(this.encourageColor, encourageColor);
        helperMap.set(this.specialColor, specialColor);

        for (let i = 0; i<this.colors.length; ++i)
            this.colors[i] = helperMap.get(this.colors[i]);

        this.notifyObservers();
    }

    notifyObservers(){
        for(let obs of this.observers)
            obs.update(this);
    }
}

interface __SidePanelViewItemRenderer {
    render(color: string, action : () => void): HTMLElement;
}

class SidePanelView implements SidePanelModelObserver{
    private model : SidePanelModel;
    public item_renderers : Array<__SidePanelViewItemRenderer>;
    public element: HTMLElement;
    
    constructor(model : SidePanelModel){
        this.model = model;
        this.model.observers.push(this);
        this.item_renderers = [];
        this.element = document.createElement("div"); // I know there 
        this.refresh();
        this.setSize(50, 100); // pre-arrange items in arbitrary shape
    }

    update(model: SidePanelModel){
        while(model.actions.length > this.item_renderers.length){
            this.item_renderers.push(this.__create_null_item_renderer());
        };
        
        while(this.element.firstChild)
            this.element.firstChild.remove();

        for(let i = 0; i < model.actions.length; ++i){
            let el = this.item_renderers[i].render(model.colors[i], model.actions[i]);
            el.addEventListener("mouseenter", ev => {model.mark(i); });
            el.addEventListener("mouseleave", ev => {model.unmark(i);});
            this.element.append(el);
        }

    }

    setSize(width : number, height : number){
        this.element.style.width = width + "px";
        this.element.style.height = height + "px";
    }

    refresh(){
        this.update(this.model);
    }

    __create_null_item_renderer(){
        const result : __SidePanelViewItemRenderer = {
            render(color, action){
                const result = document.createElement("button");
                result.addEventListener("click", action);
                result.style.background = color;
                result.value = "click me";
                return result;
            }
        }
        return result;
    }
   
}
