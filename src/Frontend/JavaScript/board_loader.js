class DebugBoardController{
    constructor(){

    }
    handle_sq_click(index){
        console.log("Square " + index +" was clicked.");
     }
}
class BoardLoader{

    constructor(model, view, controller){
        this.model = model;
        this.view = view;
        this.controller = controller;

        this.view.set_controller(this.controller);
        this.view.set_model(this.model);
    };

    append_board_to_element(element_id){
       let element = document.getElementById(element_id);
       element.append(this.view.boardElement);
    }
}
