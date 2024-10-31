import {BoardModel, BoardState, MoveGenerator, PieceType, Piece, Color} from  "./board_model.js";
import { BoardView} from "./board_view.js"
import {SidePanelModel, SidePanelView} from  "../static/board_side_panel.js"
import {ChatFragment} from "../static/chat.js"
import {appGlobalContext} from "../static/global_context.js"
import {SeatSelectorWindowModel, SeatSelectorWindowView} from "../static/side_selector.js"
import {SelectorWithQuantityView, SelectorWithQuantityModel} from "../static/unit_selector.js"
import { ServerConnection } from "./server_connection.js";
import { extract_setup } from "./PieceEncoder.js";
import {OnlineGameplayBoardController} from "./gameplay_board_controller.js"
import { Clock, SimpleClock } from "./clock.js";

export const user_game_roles = {
    red_player: "red_player",
    blue_player: "blue_player",
    spectator: "spectator" 
}


class __SetupPhaseComponentsFactory{
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
    constructor(color){
        this.color = color;
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

export class AwaitPhaseFragment{
    constructor(serverConnection){
        this.serverConnection = serverConnection;
        this.boardView = new BoardView(); //only for aestetic reason
        this.chatFrag = new ChatFragment(appGlobalContext.chatModel);
        this.chatFrag.onSend = (msg) => serverConnection.commandMannager.send_message(msg);
        this.seatSelectorWindowModel = appGlobalContext.seatWindowModel;
        this.seatSelectorWindowView = new SeatSelectorWindowView(this.seatSelectorWindowModel); 
        this.seatSelectorWindowModel.onClaimSeat = color => {serverConnection.commandMannager.claim_seat(color);}
        this.seatSelectorWindowModel.onSeatRelease = _ => {serverConnection.commandMannager.release_seat();}
        this.seatSelectorWindowModel.onReadyChange = value => {serverConnection.commandMannager.set_ready(value);}
        this.fragmentElement = document.createElement("div");

        this.onCreate();
    }


    onCreate(){
        this.fragmentElement.append(this.boardView.boardElement);
        this.fragmentElement.append(this.chatFrag.chatWrapper);
        this.fragmentElement.append(this.seatSelectorWindowView.window);
        this.seatSelectorWindowModel.attachTableObservers(appGlobalContext.table);
        this.chatFrag.setSize(300, 375);
    }
    onDestroy(){}

    onHide(){
        this.fragmentElement.style.display = "none";
    }

    onFocus(){
        this.fragmentElement.style.display = "block";
        this.boardView.set_controller(this.boardController);
    }

    resize_fragment(page_size_x, page_size_y){
        let board_size = Math.floor(page_size_x * 0.66);
        this.boardView.set_size(board_size);

        this.chatFrag.setSize(Math.floor(0.33 * page_size_x), board_size);
        this.chatFrag.chatWrapper.style.position = "absolute";
        this.chatFrag.chatWrapper.style.left = Math.floor(page_size_x * 0.75) + "px";
        this.chatFrag.chatWrapper.style.top = "8px";

        this.seatSelectorWindowView.window.style.position = "absolute";
        const windowX = Math.floor(page_size_x/2);
        const windowY = Math.floor(page_size_y/5);
        this.seatSelectorWindowView.setSize(windowX, windowY);
        this.seatSelectorWindowView.window.style.left = (board_size - windowX)/2 + "px";
        this.seatSelectorWindowView.window.style.top = (board_size - windowY)/2 + "px";
    }
}

export class SetupFragment{
    constructor(color, serverConnection){
        this.onSetupSend = setup => serverConnection.commandMannager.send_setup(setup);
        this.boardModel = new BoardModel(new MoveGenerator(), new BoardState());
        this.boardView = new BoardView();
        this.chatFrag = new ChatFragment(appGlobalContext.chatModel);
        this.setupClock = new SimpleClock();

        // Both red and blue clock have the same behaviour now, so it doesn't matter with one we choose to track here
        appGlobalContext.red_clock.observers.push(this.setupClock); 

        this.chatFrag.onSend = (msg) => serverConnection.commandMannager.send_message(msg);
        this.boardModel.boardstate.observers.push(this.boardView);

        let compFact = new __SetupPhaseComponentsFactory(color);
        this.unitSelectorModel = compFact.create_unit_selector_model(this.boardModel);
        this.unitSelectorView = compFact.create_unit_selector_view(this.boardView, this.unitSelectorModel);
        this.boardController = compFact.create_board_controller(this.boardModel, this.unitSelectorModel);
        this.fragmentElement = document.createElement("div");
        
        const send_setup = () => {
            const setup = extract_setup(this.boardModel, color==Color.BLUE);
            console.log(setup);
            serverConnection.commandMannager.send_setup(setup);
        }

        this.boardSidePanelModel = compFact.create_board_side_panel_model(function(){}, send_setup)
        this.boardSidePanelView = compFact.create_board_side_panel_view(this.boardSidePanelModel);

        

        this.userColor = color;

        this.onCreate();
    }

    onCreate(){
        this.fragmentElement.append(this.setupClock.element);
        this.fragmentElement.append(this.boardView.boardElement);
        this.fragmentElement.append(this.unitSelectorView.viewElement);
        this.fragmentElement.append(this.chatFrag.chatWrapper);
        this.fragmentElement.append(this.boardSidePanelView.element);

        this.chatFrag.setSize(300, 375);
    }

    onDestroy(){}

    onHide(){
        this.fragmentElement.style.display = "none";
    }

    onFocus(){
        this.fragmentElement.style.display = "block";
        this.boardView.set_controller(this.boardController);
    }

    resize_fragment(page_size_x, page_size_y){
        let board_size = Math.floor(page_size_x * 0.66);
        this.boardView.set_size(board_size);
        
        this.boardView.boardElement.style.position = "absolute";
        this.boardView.boardElement.style.top = Math.floor(page_size_y * 0.1) + "px";

        this.unitSelectorView.set_size(board_size);
        this.unitSelectorView.viewElement.style.position = "absolute";
        this.unitSelectorView.viewElement.style.top = Math.floor(page_size_y * 0.1 + page_size_x * 0.66) + "px";

        this.chatFrag.setSize(Math.floor(0.33 * page_size_x), board_size);
        this.chatFrag.chatWrapper.style.position = "absolute";
        this.chatFrag.chatWrapper.style.left = Math.floor(page_size_x * 0.75) + "px";
        this.chatFrag.chatWrapper.style.top = Math.floor(page_size_y * 0.1) + "px";

        this.boardSidePanelView.setSize(Math.floor(page_size_x * 0.03), board_size);
        this.boardSidePanelView.element.style.position = "absolute";
        this.boardSidePanelView.element.style.left = Math.floor(page_size_x * 0.68) + "px";
        this.boardSidePanelView.element.style.top = Math.floor(page_size_y * 0.1) + "px";

        this.setupClock.element.style.position = "absolute";
        this.setupClock.element.style.left = Math.floor(page_size_x * 0.66 * 0.815) + "px";
        this.setupClock.element.style.top = Math.floor(page_size_y * 0) + "px";
        this.setupClock.element.style.width = Math.floor(page_size_x * 0.066 * 2) + "px";

      
    }

    set_player_color(color){
        this.userColor = color;
        let compFact = new __SetupPhaseComponentsFactory();
        compFact.color = color;
        this.boardView.set_controller(compFact.create_board_controller(this.boardModel, this.unitSelectorModel));
    }

}

export class GameplayPhaseFragment{
    constructor(serverConnection, userColor){
        // TODO: implement this class and decouple general mess that are those ducking fragments
        this.boardModel = appGlobalContext.table.boardModel;
    
        this.boardView = new BoardView();
        this.chatFrag = new ChatFragment(appGlobalContext.chatModel);
        this.upperClock = new SimpleClock();
        this.lowerClock = new SimpleClock();
        

        this.boardView.set_model(this.boardModel);

        this.chatFrag.onSend = (msg) => serverConnection.commandMannager.send_message(msg);
        this.boardModel.submitMove = (move) => serverConnection.commandMannager.send_move(move);
        this.boardModel.boardstate.observers.push(this.boardView);
        this.boardModel.boardstate.notify_observers();

        this.boardController = new OnlineGameplayBoardController(serverConnection, this.boardModel, userColor);
        this.boardView.set_controller(this.boardController);

        if (userColor=="blue"){
            appGlobalContext.red_clock.observers.push(this.upperClock);
            appGlobalContext.blue_clock.observers.push(this.lowerClock);
        } else {
            appGlobalContext.red_clock.observers.push(this.lowerClock);
            appGlobalContext.blue_clock.observers.push(this.upperClock);
        }

        this.fragmentElement = document.createElement("div");

        this.onCreate();
    }

    onCreate(){
        this.fragmentElement.append(this.upperClock.element);
        this.fragmentElement.append(this.boardView.boardElement);
        this.fragmentElement.append(this.lowerClock.element);
        this.fragmentElement.append(this.chatFrag.chatWrapper);


        this.chatFrag.setSize(300, 375);
    }

    onDestroy(){}

    onHide(){
        this.fragmentElement.style.display = "none";
    }

    onFocus(){
        this.fragmentElement.style.display = "block";
        this.boardView.set_controller(this.boardController);
    }
    
    resize_fragment(page_size_x, page_size_y){

        let board_size = Math.floor(page_size_x * 0.66);
        this.boardView.set_size(board_size);
        this.chatFrag.setSize(Math.floor(0.33 * page_size_x), board_size);
        this.chatFrag.chatWrapper.style.position = "absolute";
        this.chatFrag.chatWrapper.style.left = Math.floor(page_size_x * 0.95) + "px";
        this.chatFrag.chatWrapper.style.top = Math.floor(page_size_y * 0.1) + "px";

        this.boardView.boardElement.style.position = "absolute";
        this.boardView.boardElement.style.top = Math.floor(page_size_y * 0.1) + "px";

        this.upperClock.element.style.position = "absolute";
        this.upperClock.element.style.left = Math.floor(page_size_x * 0.66 * 0.815) + "px";
        this.upperClock.element.style.top = Math.floor(page_size_y * 0) + "px";
        this.upperClock.element.style.width = Math.floor(page_size_x * 0.066 * 2) + "px";

        this.lowerClock.element.style.position = "absolute";
        this.lowerClock.element.style.left = Math.floor(page_size_x * 0.66 * 0.815) + "px";
        this.lowerClock.element.style.top =   Math.floor(page_size_y * 0.74) + "px";
        this.lowerClock.element.style.width = Math.floor(page_size_x * 0.066 * 2) + "px";

        // this.boardSidePanelView.setSize(Math.floor(page_size_x * 0.03), board_size);
        // this.boardSidePanelView.element.style.position = "absolute";
        // this.boardSidePanelView.element.style.left = Math.floor(page_size_x * 0.68) + "px";
        // this.boardSidePanelView.element.style.top = "8px";
    }
}

export class FragmentManager{
    constructor(serverConnection){
        this.fragmentWrapper = document.createElement("div");
        console.log(serverConnection);
        this.currentFragment = new AwaitPhaseFragment(serverConnection);
        this.fragmentCatalog = new Map();

        this.page_size_x = 750;
        this.page_size_y = 750;

        this.fragmentWrapper.append(this.currentFragment.fragmentElement);
        this.currentFragment.resize_fragment(this.page_size_x, this.page_size_y);

    }

    setFragment(frag){
        console.log("Focus...")
        this.currentFragment.onHide();
        this.currentFragment.fragmentElement.remove();
        this.currentFragment = frag;
        this.fragmentWrapper.append(this.currentFragment.fragmentElement);
        this.currentFragment.resize_fragment(this.page_size_x, this.page_size_y);
        this.currentFragment.onFocus();
    }

    setFragmentById(id){
        const frag = this.fragmentCatalog.get(id);
        if(frag)
            this.setFragment(frag);
    }

    
}