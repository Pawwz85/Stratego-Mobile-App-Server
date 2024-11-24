import {SelectorWithQuantityModel, SelectorWithQuantityView} from "./unit_selector.js"
import {SidePanelModel, SidePanelView} from "./board_side_panel.js"
import {PieceType, Piece} from "./board_model.js"



export function check_if_setup_is_valid(setup){
    /*
        This function expects setup, presented in user oriented perpective. (That means from perspective from user, 0 is in
        top-left corner).

        This function checks if setup contained in 'setup' state is acceptable by server rules. 
    */

    let result = true;

    // Rule 1, pieces must be positioned in region [60-99]
    for (let i = 0; i< 60; ++i)
        result &&= (setup.squares[i].piece == null);

    for (let i = 60; i< 100; ++i)
        result &&= (setup.squares[i].piece != null); 

    if (!result)
        return false;

    // Rule 2, count pieces by their types
    
    let counter = new Map();
    counter.set(PieceType.FLAG, 1);
    counter.set(PieceType.BOMB, 6);
    counter.set(PieceType.SPY, 1);
    counter.set(PieceType.SCOUT, 8);
    counter.set(PieceType.MINER, 5);
    counter.set(PieceType.SERGEANT, 4);
    counter.set(PieceType.LIEUTENANT, 4);
    counter.set(PieceType.CAPTAIN, 4);
    counter.set(PieceType.MAJOR, 3);
    counter.set(PieceType.COLONEL, 2);
    counter.set(PieceType.GENERAL, 1);
    counter.set(PieceType.MARSHAL, 1);
    counter.set(PieceType.UNKNOWN, 0);
 
    for(let i = 60; i< 100; ++i){
        let piece_type = setup.squares[i].piece.type ?? PieceType.UNKNOWN;
        let current_value = counter.get(piece_type) ?? 0;
        counter.set(piece_type, current_value - 1);
    }
    
    for(let key of counter.keys()){
        result &&= (counter.get(key)??1) == 0;
    }

    return result;
}

export class SetupPhaseComponentsFactory{
    /*
        I am convinced that nobody actually likes factory patterns, but in this case there are 2 reasons why 
        this (probably) single use class exist:
        - The first, less important one, having an UI fragment class with initialization that long would break SOLID,  
          as no one would know which methods are contructor helper functions and actual class methods, leading to splitting
          logic of the class into 2 separate layers: contstruction and functional one
        - The main reason is to prevent dublication of a components, promoting component reuse between fragments. Before the code
          was refactored from its fragment, components such as BoardView or BoardModel were created allongside other fragment's 
          components and then glued together to be used only in such fragment and being impossible to reuse in other fragments.  

    */
    constructor(color, trySendSetup){
        this.color = color;
        this.trySendSetup = trySendSetup;
    }

    create_unit_selector_model(){
        let model = new SelectorWithQuantityModel(12);
        model.set_item_count(0, 1); // flag
        model.set_item_count(1, 6); // bomb
        model.set_item_count(2, 1); // spy
        model.set_item_count(3, 8); // scout
        model.set_item_count(4, 5); // miner
        model.set_item_count(5, 4); // sergeant
        model.set_item_count(6, 4); // lieutenant
        model.set_item_count(7, 4); // captain
        model.set_item_count(8, 3); // major
        model.set_item_count(9, 2); // colonel
        model.set_item_count(10, 1); // general
        model.set_item_count(11, 1); // marschal
        return model;
    }

    create_unit_selector_view(boardView, unitSelectorModel){
        let result = new SelectorWithQuantityView(unitSelectorModel);

        for (let i = 0; i<unitSelectorModel.items.length; ++i)
            result.set_item_renderer(i, this.__create_renderer_for_selector_index(i, boardView));

        result.refresh(); // refresh view using new renderers
        return result;
    }

    __put_piece_back_to_selector(piece, pieceSelectorModel){
        let index = null;
        switch(piece.type){
            case PieceType.FLAG: index = 0; break;
            case PieceType.BOMB: index = 1; break;
            case PieceType.SPY: index = 2; break;
            case PieceType.SCOUT: index = 3; break;
            case PieceType.MINER: index = 4; break;
            case PieceType.SERGEANT: index = 5; break; 
            case PieceType.LIEUTENANT: index = 6; break;
            case PieceType.CAPTAIN: index = 7; break;
            case PieceType.MAJOR: index = 8; break;
            case PieceType.COLONEL: index = 9; break;
            case PieceType.GENERAL: index = 10; break;
            case PieceType.MARSHAL: index = 11; break; 
            default: index = null; break;
        };
        if (index != null)
            pieceSelectorModel.set_item_count(index, pieceSelectorModel.items[index] + 1);
        return index;
    }

    __create_piece_from_selector_index(index){
        let type = null;
        switch(index){
            case 0: type = PieceType.FLAG; break;
            case 1: type = PieceType.BOMB; break;
            case 2: type = PieceType.SPY; break;
            case 3: type = PieceType.SCOUT; break;
            case 4: type = PieceType.MINER; break;
            case 5: type = PieceType.SERGEANT; break; 
            case 6: type = PieceType.LIEUTENANT; break;
            case 7: type = PieceType.CAPTAIN; break;
            case 8: type = PieceType.MAJOR; break;
            case 9: type = PieceType.COLONEL; break;
            case 10: type = PieceType.GENERAL; break;
            case 11: type = PieceType.MARSHAL; break; 
        }
        console.log(this.color)
        return (type != null)? new Piece(this.color.toLowerCase(), type): null;
    }

    __create_renderer_for_selector_index(index, boardView){
        const type = this.__create_piece_from_selector_index(index).type;
        const renderer = {
            render(item_count){
                let item_card = document.createElementNS("http://www.w3.org/2000/svg", "svg");   
                item_card.setAttribute("viewBox", "0 0 100 100");
                item_card.setAttribute("fill", "white");
                if (item_count > 0){
                    let piece = boardView.renderer.render_piece(type);
                    for(let i = 0; i<piece.length; ++i)
                        item_card.append(piece[i]);
                }
              
                return item_card;
            },
        
            render_with_count(item_count, show_inactive_cnt){
                return this.render(item_count);
                /*let card = this.render(item_count);
                
                if(!show_inactive_cnt && item_count <= 0)
                    return card;
        
                let text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                text.textContent = "" +(item_count>0)?item_count:"0";
        
                text.setAttribute("x", "90%");
                text.setAttribute("y", "90%");
                card.append(text);
                return card;*/
            }
        }
        return renderer;
    }

    create_board_controller(boardModel, unitSelectorModel){
        let frag = this;
        let board_controller = {
            mouse_index : null,
            handle_sq_click(sq){
                if(sq < 60) return;
                let refresh = false;
                let piece_index = null;
                console.log("clicked sq " + sq);
                let empty_selector = unitSelectorModel.selected_item == null;
                if (boardModel.boardstate.squares[sq].piece != null){
                    piece_index = frag.__put_piece_back_to_selector(boardModel.boardstate.squares[sq].piece, unitSelectorModel);
                    boardModel.boardstate.squares[sq].piece = null;
                    refresh = true;
                }

                if(!empty_selector && piece_index != unitSelectorModel.selected_item){
                    let current_item = unitSelectorModel.selected_item;
                    let piece = frag.__create_piece_from_selector_index(unitSelectorModel.drop_selected_item());
                    boardModel.boardstate.squares[sq].piece = piece;
                    unitSelectorModel.try_select_item(current_item); // for smother usage

                    if(unitSelectorModel.selected_item == null && piece_index != null)
                        unitSelectorModel.try_select_item(piece_index);

                    refresh = true;
                }
                
                if(empty_selector && piece_index != null){
                    unitSelectorModel.try_select_item(piece_index); // automatically set selected item if picked up item from board
                    refresh = true;
                }


                if(refresh){
                     boardModel.boardstate.notify_observers();
                     frag.trySendSetup();
                }      
            },
            handle_mouse_enter(sq){
                if(sq < 60 || unitSelectorModel.selected_item == null) return;
                    
                if(this.mouse_index != sq){
                    this.mouse_index = sq;
                    for(let i = 0; i<100; ++i)
                        boardModel.boardstate.squares[i].highlight = false;
                    boardModel.boardstate.squares[sq].highlight = true;
                    boardModel.boardstate.notify_observers(); // TODO: implement  
                }
              
            },
            handle_mouse_leave(sq){
                if(this.mouse_index == sq){
                    this.mouse_index = null;
                    boardModel.boardstate.squares[sq].highlight = false;
                    boardModel.boardstate.notify_observers(); // TODO: implement  
                }
            }
        }
        return board_controller;
    }
    create_board_side_panel_model(onSubmit, onHelp){
        let model = new SidePanelModel();
        model.addAction(onHelp);
        model.addAction(onSubmit);
        return model;
    }

    create_board_side_panel_view(board_side_panel_model){
        let view = new SidePanelView(board_side_panel_model);

        return view;
    }
}
