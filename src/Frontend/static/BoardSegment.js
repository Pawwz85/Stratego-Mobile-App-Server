import {appGlobalContext} from "./global_context.js"
import {OnlineGameplayBoardController} from "./gameplay_board_controller.js"
import {SelectorWithQuantityModel, SelectorWithQuantityView} from "./unit_selector.js"
import {SidePanelModel, SidePanelView} from "./board_side_panel.js"
import {BoardModel, MoveGenerator, BoardState, PieceType, Color, Piece} from "./board_model.js"
import {BoardView} from "./board_view.js"
import { extract_setup } from "./PieceEncoder.js";
import { SimpleClock } from "./clock.js"
import {SetupPhaseComponentsFactory, check_if_setup_is_valid} from "./setup.js"
/*
    Board Segment is a class that is representing a Board and its controllers. 
    This class is result of decoupling the code smell that were GameFragments. 
*/


// copied from old game fragments code, it could be reused here

// TODO: implement class BoardSegmentView
export class BoardSegmentModel {
    constructor(serverConnection){
        this.game_phase = null; // null, "awaiting", "setup", "gameplay" or "finished"
        this.user_role = "spectator"; // "spectator", "red_player" or "blue_player"
        this.boardModel = new BoardModel(new MoveGenerator(), new BoardState());
        this.unitSelectorModel = new SelectorWithQuantityModel(12);
        this.sidePanelModel = null;
        this.serverConnection = serverConnection;
        this.boardController = null;
        this.observer = null; // this class should have at max 1 observer (probably a view)
        

        this.send_setup = () => {

            if (this.game_phase != "setup" || this.user_role == "spectator")
                return;

            
            const setup = extract_setup(this.boardModel, this.user_role=="blue_player");
            console.log(setup)
            if(check_if_setup_is_valid(this.boardModel.boardstate))
                serverConnection.commandMannager.send_setup(setup);
        }

        this.__setupPhaseComponentsFactory = new SetupPhaseComponentsFactory("red", this.send_setup);
        this.sidePanelModel = this.__setupPhaseComponentsFactory.create_board_side_panel_model(this.send_setup, function(){});
    
    }

    notify_observers() {
            this.observer?.on_board_segment_update(this);
    }

    __refresh_board_model(){
         /*
            Check if board model should be synchronised with server or not.
        */
        if (["awaiting", "gameplay", "finished"].includes(this.game_phase)) {
            this.boardModel = appGlobalContext.table.boardModel;
        } else {
            this.boardModel = new BoardModel(new MoveGenerator(), new BoardState());
        }

    }

    __refresh_board_controller(){
        //console.log(this.game_phase, this.user_role)
        // this method should be called after refreshing boardModel       
        if (this.user_role == "spectator"){
            this.boardController = null;
            return;
        }
           

        if (["awaiting", "finished"].includes(this.game_phase) || this.game_phase == null){
            this.boardController = null;
            return;
        }
            

        if (this.game_phase == "setup"){
            this.unitSelectorModel = this.__setupPhaseComponentsFactory?.create_unit_selector_model();
            this.boardController   = this.__setupPhaseComponentsFactory?.create_board_controller(this.boardModel, this.unitSelectorModel);
            return;
        }

        if (this.game_phase == "gameplay"){
            const user_color = (this.user_role == "red_player")? "red": "blue";
            this.boardController = new OnlineGameplayBoardController(this.serverConnection, this.boardModel, user_color);
            return;
        }
    }

    __refresh_setup_components_factory(){
        if (this.game_phase != "setup" || this.user_role == "spectator"){
            this.__setupPhaseComponentsFactory = new SetupPhaseComponentsFactory("red", this.send_setup);
            return;
        }

        const pieces_color = (this.user_role == "red_player")? "red": "blue";
        this.__setupPhaseComponentsFactory = new SetupPhaseComponentsFactory(pieces_color, this.send_setup);
    }

    set_game_phase(game_phase){
        if(!["awaiting", "setup", "gameplay", "finished"].includes(game_phase) && game_phase != null)
            throw new Error("Illegal game phase value");

        this.game_phase = game_phase;
        this.__refresh_setup_components_factory();
        this.__refresh_board_model();
        this.__refresh_board_controller();
        this.notify_observers();
    }

    set_user_role(role){
        if (!["spectator", "red_player", "blue_player"].includes(role))
            throw new Error("Illegal role value");

        this.user_role = role;
        this.__refresh_setup_components_factory();
        this.__refresh_board_controller();
        this.notify_observers();
    }   
}

// TODO: implement this class
export class BoardSegmentView {
    constructor(segmentModel, width, height){
        this.model = segmentModel;
        this.element = document.createElement("div");
        segmentModel.observer = this;
        this.__board_view = null;
        this.__unit_selector_view = null;
        this.__boardSidePanelView = null; 
        this.__upper_clock = new SimpleClock();
        this.__lower_clock = new SimpleClock();
        this.__width  = width;
        this.__height = height;
        
        this.__board_layout = {
            size: 0,
            offset_x: 0,
            offset_y: 0
        }

        this.refresh();       
    }

    __clear(){
        while(this.element.firstChild)
            this.element.firstChild.remove();
    }

    __update_active_components(phase){
        this.__unit_selector_view.viewElement.style.display = "block";
        this.__boardSidePanelView.element.style.display = "block";
        this.__board_view.boardElement.style.display = "block";
        this.__lower_clock.element.style.display = "block";
        this.__upper_clock.element.style.display = "block";
       
        if(phase != "setup"){
            this.__unit_selector_view.viewElement.style.display = "none";
            this.__boardSidePanelView.element.style.display = "none";
        } else{
            // unit selecetor will collide with lower clock, so hide this clock in setup phase
            this.__lower_clock.element.style.display = "none";
        }
    }

    refresh(){
        this.on_board_segment_update(this.model);
    }

    on_board_segment_update(seg_model){
        this.__clear();

        this.__board_view = new BoardView();
        this.__unit_selector_view = seg_model.__setupPhaseComponentsFactory.create_unit_selector_view(this.__board_view, seg_model.unitSelectorModel);
        this.__boardSidePanelView = seg_model.__setupPhaseComponentsFactory.create_board_side_panel_view(seg_model.sidePanelModel);

        this.__board_view.set_controller(seg_model.boardController);
        seg_model.boardModel.boardstate.temporal_observer = this.__board_view;
        seg_model.boardModel.boardstate.notify_observers();

        // remove occurences of those observers from global context clocks 
        appGlobalContext.blue_clock.remove_observer(this.__lower_clock);
        appGlobalContext.blue_clock.remove_observer(this.__upper_clock);
        appGlobalContext.red_clock.remove_observer(this.__lower_clock);
        appGlobalContext.red_clock.remove_observer(this.__upper_clock);

        if (seg_model.user_role == "blue_player"){
            appGlobalContext.blue_clock.observers.push(this.__lower_clock);
            appGlobalContext.red_clock.observers.push(this.__upper_clock);
        } else {
            appGlobalContext.blue_clock.observers.push(this.__upper_clock);
            appGlobalContext.red_clock.observers.push(this.__lower_clock);
        }

        appGlobalContext.blue_clock.notify_observers();
        appGlobalContext.red_clock.notify_observers();

        this.__update_active_components(seg_model.game_phase);

        this.element.appendChild(this.__board_view.boardElement);
        this.element.appendChild(this.__unit_selector_view.viewElement);
        this.element.appendChild(this.__boardSidePanelView.element);
        this.element.appendChild(this.__lower_clock.element);
        this.element.appendChild(this.__upper_clock.element);
        this.resize(this.__width, this.__height);

    }

    __get_layout(page_x, page_y){
        const clock_ratio = 0.4 // Ratio of clock_height / clock_width
        const side_panel_ratio = 2.5; // ratio of side panel height/width
        const board_ratio = 0.75; // Ratio of board_width/page_x
        const horizontal_offset = 0.05; // Ration (ofset between side panel and board right edge) / page_x
        const vertical_offset = 0.005 ; // Ofset between UI elements (ratio of page_y)
        const clock_width = 0.2 * board_ratio // Ratio of clock_width/page_x
        const clock_height = clock_width * page_x * clock_ratio / page_y;
        const clock_off = board_ratio - clock_width;
        const side_panel_width = 1 - board_ratio - horizontal_offset;
        const side_panel_height = side_panel_ratio*side_panel_width * page_x / page_y; // ratio of side_panel_width/page_x
        return {
        page_x: page_x,
        page_y: page_y,
        clock_ratio: clock_ratio, 
        side_panel_ratio: side_panel_ratio,
        board_ratio: board_ratio, 
        horizontal_offset: horizontal_offset,
        vertical_offset: vertical_offset,
        clock_width: clock_width,
        clock_height: clock_height,
        clock_off: clock_off,
        side_panel_width: side_panel_width,
        side_panel_height: side_panel_height
        }
    }

    __resize_children(layout){
        this.__board_view.set_size(layout.board_ratio*layout.page_x);
        this.__unit_selector_view.set_size(Math.floor(layout.board_ratio*layout.page_x));
        this.__boardSidePanelView.setSize(Math.floor(layout.side_panel_width*layout.page_x, layout.side_panel_height * layout.page_y));
        this.__lower_clock.element.style.width = this.__upper_clock.element.style.width = Math.floor(layout.clock_width*layout.page_x) + "px";
        this.__lower_clock.element.style.height = this.__upper_clock.element.style.height = Math.floor(layout.clock_height*layout.page_y) + "px";
    }

    __recalculate_board_layout(layout){
      this.__board_layout.offset_x = 0;
      this.__board_layout.offset_y = Math.floor((layout.vertical_offset + layout.clock_height) * layout.page_y);
      this.__board_layout.size = Math.floor(layout.board_ratio*layout.page_x);
    }

    __set_children_position(layout){
        this.__board_view.boardElement.style.position = "absolute";
        this.__unit_selector_view.viewElement.style.position = "absolute";
        this.__boardSidePanelView.element.style.position = "absolute";
        this.__lower_clock.element.style.position = "absolute";
        this.__upper_clock.element.style.position = "absolute";

        this.__upper_clock.element.style.left =  Math.floor(this.__board_layout.offset_x + layout.clock_off*layout.page_x) + "px";
        this.__upper_clock.element.style.top = "0px";

        let current_height = (layout.vertical_offset + layout.clock_height) * layout.page_y;
        this.__boardSidePanelView.element.style.left = Math.floor((layout.board_ratio + layout.horizontal_offset)*layout.page_x) + "px";
        this.__boardSidePanelView.element.style.top = Math.floor(current_height) + "px"; 

        this.__board_view.boardElement.style.left = this.__board_layout.offset_x + "px";
        this.__board_view.boardElement.style.top = this.__board_layout.offset_y + "px"; 

        current_height += layout.board_ratio*layout.page_x  + layout.vertical_offset*layout.page_y;
        this.__lower_clock.element.style.left = Math.floor(this.__board_layout.offset_x + layout.clock_off*layout.page_x) + "px";
        this.__lower_clock.element.style.top = Math.floor(current_height) + "px";

        this.__unit_selector_view.viewElement.style.left = "0px";
        this.__unit_selector_view.viewElement.style.top = Math.floor(current_height) + "px";
    }

    resize(page_x, page_y){
        this.__width  = page_x;
        this.__height = page_y;
        const layout = this.__get_layout(page_x, page_y);
        this.__resize_children(layout);
        this.__recalculate_board_layout(layout);
        this.__set_children_position(layout);
    }

    get_board_layout(){
        return { ...this.__board_layout };
    }
}