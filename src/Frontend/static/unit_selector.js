export class SelectorWithQuantityModel{

    constructor(size){
        this.selected_item = null;
        this.items = new Array(size);
        this.observers = [];

        for(let i = 0; i < this.items.length; ++i)
            this.items[i] = 1;
    }

    set_item_count(item_index, item_count){
        this.items[item_index] = item_count;
        this.notify_observes();
    }

    put_down_selected_item(){
        if (this.selected_item != null){
            this.selected_item = null;
            this.notify_observes();
        }
    }

    drop_selected_item(){
        let result = this.selected_item;
        if (this.selected_item != null){
            this.items[this.selected_item] -= 1;
            this.selected_item = null;
            this.notify_observes();
        }
        return result;
    }

    try_select_item(item_index){
        if(this.items[item_index] > 0){
            this.selected_item = item_index;
            this.notify_observes();
        }
    }

    select_first_available(){
        for (let i = 0; i<this.items.length; ++i)
            if(this.items[i] > 0){
                this.selected_item = i;
                this.notify_observes();
                return
            }
    }

    notify_observes(){
        for(let i = 0; i< this.observers.length; ++i)
            this.observers[i].update(this);
    }
}

export class SelectorWithQuantityItemRenderer{

    // Expect svg as string
    constructor(str_active_item_svg, str_inactive_item_svg){
        this.active_item_svg = str_active_item_svg;
        this.inactive_item_svg = str_inactive_item_svg;
    }

    render(item_count){
        let item_svg = (item_count > 0)? this.active_item_svg : this.inactive_item_svg;    
        item_svg = document.createRange().createContextualFragment(item_svg).firstChild;
        let item_card = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        
        item_card.setAttribute("viewBox", "0 0 100 100");
        item_card.append(item_svg);
        return item_card;
    }

    render_with_count(item_count, show_inactive_cnt){
        let card = this.render(item_count);
        
        if(!show_inactive_cnt && item_count <= 0)
            return card;

        let text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.textContent = "" +(item_count>0)?item_count:"0";

        text.setAttribute("x", "90%");
        text.setAttribute("y", "90%");
        card.append(text);
        return card;
    }
}    


export class SelectorWithQuantityView{
    constructor(model){
        this.model = model;
        model.observers.push(this);
        this.__renderers = new Array(model.items.length);
        this.__null_item_renderer = new SelectorWithQuantityItemRenderer(
            "<svg><rect width=\"50\" height=\"50\" fill=\"red\"> </rect></svg>",
            "<svg><rect width=\"50\" height=\"50\" fill=\"red\"> </rect></svg>"
        )
        this.__selected_item_view = null; // shortcut to node of a view, it will be set by __create_view_element
        this.__items_views = new Array(model.items.length); //array of shortcuts; each will be set by __create_view_element
        this.__component_width = 1000;
        this.__component_height = 100;


        for (let i = 0; i< this.__renderers.length; ++i)
            this.__renderers[i] = new SelectorWithQuantityItemRenderer(
                "<svg><rect width=\"50\" height=\"50\" fill=\"green\"> </rect></svg>",
                "<svg><rect width=\"50\" height=\"50\" fill=\"gray\"> </rect></svg>"
            )
        this.viewElement = this.__create_view_element();
        this.refresh();

    }
    __create_view_element(){
        let wrapper = document.createElementNS("http://www.w3.org/2000/svg","svg");
        wrapper.setAttribute("viewBox", "0 0 1000 100");
        wrapper.setAttribute("width", this.__component_width);
        for (let i = 0; i<this.model.items.length; ++i){
            this.__items_views[i] = this.__renderers[i].render_with_count(this.model.items[i], true);
            wrapper.append(this.__items_views[i]);
        }
        this.__selected_item_view = (this.model.selected_item == null)? this.__null_item_renderer.render(1) : this.__renderers[this.model.selected_item].render(1);
        return wrapper; 
    }

    set_item_renderer(index, renderer){
        if (index != null)
            this.__renderers[index] = renderer;
        else
            this.__null_item_renderer = renderer;
    }

    set_size(width){
        this.__component_width = width;
        this.viewElement.setAttribute("width", this.__component_width +"px");  
      }

    update(model){
      
        if (model.selected_item == null){
            this.__selected_item_view.replaceWith(this.__null_item_renderer.render(1));
        } else {
            this.__selected_item_view.replaceWith( this.__renderers[this.model.selected_item].render(1));
        }

        this.__selected_item_view.onclick = (ev => model.put_down_selected_item());

        for (let i = 0; i<model.items.length; ++i){
            let new_view = this.__renderers[i].render_with_count(model.items[i], true);
            this.__items_views[i].replaceWith(new_view);
            this.__items_views[i] = new_view;
            this.__items_views[i].setAttribute("x", i*Math.floor(1000/model.items.length)+"px");
            this.__items_views[i].setAttribute("width", Math.floor(1000/model.items.length) + "px");
            this.__items_views[i].setAttribute("height", 100 + "px");
            this.__items_views[i].onclick = ev => { model.try_select_item(i);
                    console.log("Item " + i + " was clicked.");
                    };
          
        }

    }

    refresh(){
    this.update(this.model);
   } 
}

export class SelectorWithQuantityTemplateBasedView extends SelectorWithQuantityView{

    __create_view_element(){
        let wrapper = document.createElementNS("http://www.w3.org/2000/svg","svg");
        wrapper.setAttribute("viewBox", "0 0 1000 100");
        wrapper.setAttribute("width", this.__component_width);
        for (let i = 0; i<this.model.items.length; ++i){
            this.__items_views[i] = this.__renderers[i].render_with_count(this.model.items[i], true);
            wrapper.append(this.__items_views[i]);
        }
        this.__selected_item_view = (this.model.selected_item == null)? this.__null_item_renderer.render(1) : this.__renderers[this.model.selected_item].render(1);
        return wrapper; 
    }

    __create_view_element(){
        var parser = new DOMParser();
        let templ = document.querySelector("#tmpl_unit_selector").cloneNode(true);
        templ = parser.parseFromString(templ.innerHTML, "text/html");

        const wrapper = templ.getElementById("tmpl_unit_selector_wrapper");
        this.__inner_container = templ.getElementById("tmpl_unit_selector_container");
        this.__selected_square_wrapper = templ.getElementById("tmpl_unit_selector_selected_square").cloneNode(true);
        this.__square_wrapper = templ.getElementById("tmpl_unit_selector_not_selected_square").cloneNode(true);

        wrapper.remove();

        let card = null;

        for (let i = 0; i<this.model.items.length; ++i){
            this.__items_views[i] = this.__renderers[i].render_with_count(this.model.items[i], true);
            card = this.__square_wrapper.cloneNode(false);
            card.append(this.__items_views[i]);
            this.__inner_container.append(card);
        }
        this.__selected_item_view = (this.model.selected_item == null)? this.__null_item_renderer.render(1) : this.__renderers[this.model.selected_item].render(1);
        return wrapper; 
    }

    set_size(width){
        this.__component_width = width;
        this.viewElement.style.width = this.__component_width +"px";  
      }

      update(model){

        try{
            for(let i = 0; i < this.model.items.length; ++i) {
                this.__items_views[i].parentNode.className = (this.model.selected_item == i)? 
                                                        this.__selected_square_wrapper.className:
                                                        this.__square_wrapper.className  
            }
        } catch (e) {
            console.log(e)
        }
        super.update(model);
      }
}