/*

*/
import { appGlobalContext } from "./global_context.js";
import { ServerConnection } from "./server_connection.js";
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

export class TextPageFormatter{
   constructor(columns_lengths){
        this.columnModel = this.__create_column_model();
        this.paragraphModel = this.__create_paragraph();
        this.paragraphs_start_line = [];
        this.space_between_cols = 2;

        this.__collumns = [];
        for(let i = 0; i< columns_lengths.length; ++i)
            this.__collumns.push(new this.columnModel(columns_lengths[i]));

   }

   /*
        Add a new section, by adding a new paragraph to each column. If you wish to skip content in given column, simple pass null as content
   */
   add_section(contents, paragraph_modifiers = null){
        let start_line = 0;
        if (this.paragraphs_start_line.length > 0){
            start_line = this.paragraphs_start_line[this.paragraphs_start_line.length - 1] + this.calculate_section_line_count(this.paragraphs_start_line.length - 1);
            this.paragraphs_start_line.push(start_line);
        } else{
            this.paragraphs_start_line.push(0); 
        } 


        if(paragraph_modifiers == null || typeof paragraph_modifiers == "undefined"){
            paragraph_modifiers = [];
            for(let i = 0; i< this.__collumns.length; ++i)
               paragraph_modifiers.push({});
        }

        for(let i = 0; i< this.__collumns.length; ++i)
            this.__collumns[i].add_paragraph(contents[i], paragraph_modifiers[i]);
   }

   get_section(section_id){
    let result = [];
    for(let col_id = 0; col_id < this.__collumns.length; col_id++){
         result.push(this.__collumns[col_id].paragraphs[section_id]);
    }
       
    return result;
   }

   get_column_start_index(col_index){
        let result = 0;
        let i = 0;
        while(col_index != i){
            result += this.space_between_cols;
            result += this.__collumns[i].chars_per_column;
            ++i;
        }
        return result;
   }

   get_column_length(col_index){
    return this.__collumns[col_index].chars_per_column;
   }

   get_total_width(){
      let  result = this.__collumns[0].chars_per_column;
      for(let i =0; i<this.__collumns.length; ++i){
        result += this.space_between_cols;
        result += this.__collumns[i].chars_per_column;
      }
      return result;
   }

   calculate_section_line_count(section_id){
        const section = this.get_section(section_id);
        let result = 0;
        for (let i = 0; i< section.length; ++i){
            if(section[i] != null && typeof section[i] != "undefined")
                result = Math.max(result, section[i].lines.length);
        } 
        return result;
   }

   clear(){
        this.paragraphs_start_line = [];
        for(let i = 0; i< this.__collumns.length; ++i)
            this.__collumns[i].clear();
   }

   get_column(index){
        return this.__collumns[index];
   }

   /*
        Extracts all separate lines and their positions 
   */
   get_text_chunks(){
        let result = [];
        for(let i = 0; i< this.paragraphs_start_line.length; ++i){
            let paragraphs = this.get_section(i);
            for (let j = 0; j<paragraphs.length; ++j) if (paragraphs[j] != null && !paragraphs[j].empty())
                for(let k = 0; k<paragraphs[j].lines.length; ++k){
                    const chunk = {
                        text : paragraphs[j].lines[k],
                        modifier : paragraphs[j].modifier,
                        line : k + this.paragraphs_start_line[i], // line index
                        col: j // collumn index
                    };
                    result.push(chunk);
                }
        }
        return result;
   }

   __create_column_model(){
    let textPageModel = this;
    return class{
        constructor(chars_per_column){
            this.chars_per_column = chars_per_column;
            this.paragraphs = [];
        }

        add_paragraph(paragraph_content, modifier){

            if (paragraph_content == null){
                this.paragraphs.push(null);
                return;
            }

            let paragraph = new textPageModel.paragraphModel(this.chars_per_column);
            paragraph.modifier = modifier;
            this.paragraphs.push(paragraph);
            paragraph.write_to_paragraph(paragraph_content);
        }

        clear(){
            this.paragraphs = [];
        }
    }
   }

   __create_paragraph(){
    return class {
        constructor(max_chars_per_line){
            this.lines = [""];
            this.modifier = {}; // any attributes that can modify rendering of a paragraph
            this.chars_per_column = max_chars_per_line;
        }
        
        __add_line(){
            this.lines.push("");
        }
         
        __write_word_to_paragraph(str){

            if (str.length >= this.chars_per_column){
                // edge case 1: str is too big to fit in single line
                if(this.lines[this.lines.length - 1] != "") this.__add_line();
                this.lines[this.lines.length - 1] = str.slice(0, this.chars_per_column);
                this.__write_word_to_paragraph(str.slice(this.chars_per_column));
                return;
            }

            let c_count = this.lines[this.lines.length - 1].length;

            if (c_count + str.length >= this.chars_per_column ){
                this.lines.push(str);
            } else {
                this.lines[this.lines.length - 1] =  this.lines[this.lines.length - 1] + " " + str;
            }
        }

        write_to_paragraph(str){
            let words = str.split(" ");
            for (let i = 0; i < words.length; ++i)
                this.__write_word_to_paragraph(words[i]);
        }
        
        get_content(){
            result = "";
            for(let i = 0; this.lines.length; ++i)
                result += this.lines[i] + "\n";
            return result;
        }

        empty(){
            return this.lines[0] == "" && this.lines.length > 1;
        }
    };
   }

}


export class ChatView{
    constructor(chat_model){
        this.chat_model = chat_model
        this.chat_model.observers.push(this);
        this.page_formatter = new TextPageFormatter([12, 32]);
        this.current_line = 0;
        this.lines_per_display = 20;
        this.vertical_padding = 2;
        this.__group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        this.__box = null; // set by create_element();
        this.element = this.create_element();
        this.set_size(300, 375);
        this.initialize_controlls();
        this.refresh();
    }

    render_text_chunk(chunk){
        let text_node = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text_node.textContent = chunk.text;
        
        // TODO: apply any modifiers here

        text_node.setAttribute("y", (100*(chunk.line + this.vertical_padding - this.current_line)/(this.lines_per_display + 2*this.vertical_padding))+"%");
        text_node.setAttribute("x", (100*this.page_formatter.get_column_start_index(chunk.col)/this.page_formatter.get_total_width() + 6)+"%");
        let text_length = 100 * (chunk.text.length / this.page_formatter.get_total_width());
        text_node.setAttribute("textLength", Math.floor(text_length)+"%");
        text_node.setAttribute("lengthAdjust", "spacingAndGlyphs");
        return text_node;
    }

    create_element(){
        let result = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        let square = document.createElementNS("http://www.w3.org/2000/svg", "rect");

        square.setAttribute("fill", "white");
        square.setAttribute("rx", 50);
        square.setAttribute("ry", 50);
        square.style.strokeWidth = "3";
        square.style.stroke = "black";
        result.append(square);
        result.append(this.__group);
        this.__box = square;
        return result;
    }

    initialize_controlls(){
        let clamp =  (x, down_bound, upper_bound) => { if(down_bound>x) return down_bound; if(upper_bound<x) return upper_bound; else return x; };
        this.element.onwheel = ev => {
            let before = this.current_line;
            let off = Math.sign(ev.deltaY)
            this.current_line += off;

            if (this.current_line<0) 
                this.current_line = 0; 

            if (this.__get_chunks_in_display().length > 0)
                this.refresh();
            else
                this.current_line = this.current_line;
        }
    }

    __get_chunks_in_display(){
        let max_line = this.current_line + this.lines_per_display;
        let chunks = this.page_formatter.get_text_chunks().filter(
            (chunk) => {
                return chunk.line < max_line && this.current_line <= chunk.line; 
            }
        );
        return chunks;
    }

    update_chat(model){
        // TODO: update chat element
        this.page_formatter.clear();
        // fit messages to formatter
        for(let i = 0; i < this.chat_model.messages.length; ++i){
            let msg = this.chat_model.messages[i];
            this.page_formatter.add_section([msg.username, msg.content], null);
        }  

        let max_line = this.current_line + this.lines_per_display;
        let chunks = this.__get_chunks_in_display();
        
        this.__group.remove();
        this.__group = document.createElementNS("http://www.w3.org/2000/svg", "svg");

        this.element.append(this.__group);
        for(let i = 0; i<chunks.length; ++i){
            this.__group.append(this.render_text_chunk(chunks[i]));
        }

    }

    set_size(width, height){

        this.__box.setAttribute("width", width);
        this.__box.setAttribute("height", height);
        this.element.setAttribute("width", width);
        this.element.setAttribute("height", height);
        this.element.setAttribute("viewBox", "0 0 " + width +" " + height);
        this.width = width;
        this.height = height;
        this.refresh();

    }
    refresh(){
        this.update_chat(this.chat_model);
    }
}

export class ChatFactory{
    create_chat_view(chat_model){
        return new ChatView(chat_model);
    }

    create_chat_text_area(){
        let result = document.createElement("textarea");
        return result;
    }

    create_send_button(chat_text_area , onSubmit = null){
        let result = document.createElement("button");
        result.textContent = "Send";
        
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
    constructor(chat_model){
        let chatFact = new ChatFactory();
        this.chatModel = chat_model;
        this.chatView = new ChatView(this.chatModel);
        this.chat_text_area = chatFact.create_chat_text_area();
        this.chat_button = chatFact.create_send_button(this.chat_text_area);
        this.chatWrapper = this.__create_element();
        this.onSend = (msg) => {};
        this.onCreate();
        }

    __create_element(){
        let result = document.createElement("div");
        return result;
    }
    onCreate(){    
        this.chatWrapper.append(this.chatView.element);
        this.chatWrapper.append(this.chat_text_area);
        this.chatWrapper.append(this.chat_button);

        this.chatView.current_line = 0;

        this.chat_button.onclick = ev => {
            let text_value = this.chat_text_area.value;
            console.log("click", text_value);
            if(text_value != ""){
                this.onSend(text_value);
            }
                
            this.chat_text_area.value = "";
        }

    }
    
    onFocus(){
        this.chatWrapper.style.display = "block";
    }

    onHide(){
        this.chatWrapper.style.display = "none";
    }

    setSize(width, height){
        this.chatView.set_size(width, Math.floor(0.87 * height));
        
        this.chat_text_area.style.position = "absolute";
        this.chat_text_area.style.left = "0px";
        this.chat_text_area.style.top = this.chatView.height + Math.floor(height/20) + "px";
        this.chat_text_area.style.width = Math.floor(0.8 * width) + "px";
        this.chat_text_area.style.height = Math.floor(0.07 * height) + "px";

        this.chat_button.style.position = "absolute";
        this.chat_button.style.height = this.chat_text_area.style.height ;
        this.chat_button.style.left = parseInt(this.chat_text_area.style.width) + Math.floor(width/20) + "px";
        this.chat_button.style.top = this.chat_text_area.style.top;
    }

}