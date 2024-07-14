class Square{
    constructor(){
        this.index = 0;
        this.piece = null;
        this.draw_dot = false;
        this.highlight = false;
    }

    render(){
        return "<p>" + index + "</p>";
    }
}

class SquareRenderer{
    constructor(){
        this.board_map = this.get_default_board_map();
    }

    get_default_board_map(){
        let result = [];
        let color = "lime"

        const water_tiles = [42, 43, 46, 47, 52, 53, 56, 57]
        for (let i = 0 ; i<100; ++i){
            if (water_tiles.includes(i))
                color = "blue"
            else if (( (i%10) + Math.floor(i/10))%2 == 1)
                color = "green";
             else
                color = "lime";


            result.push("<rect width=\"100\" height=\"100\" stroke-width=\"0\" stroke=\"gray\" fill=\""+ color +"\"/>");
        }

        return result;
    }

    render_square(square){
        return this.board_map[square.index]
    }
}

class Board{
    constructor(){
        this.state = [];
        this.square_renderer = new SquareRenderer()
        for ( let i = 0; i<100; ++i){
            this.state.push(new Square());
        }

        for(let i = 0; i<100; ++i)
            this.state[i].index = i;

    }
    render_table(){
        const style = "border-spacing: 0;  border-collapse: collapse; display: block; "
        let result = "<table  cellpadding=\"0\" style=\""+ style + "\">\n"
        for (let i = 0; i<10; ++i){
            result += "<tr>"
                for (let j = 0; j<10; ++j){
                    let v = 10*i+ j
                    result += "<td><svg width=\"100\" height=\"100\" style=\"margin: 0; padding: 0; display: block;\">" + this.square_renderer.render_square(this.state[v]) + "</svg></td>"
                }
            result += "</tr>\n"
        }
        result += "</table>\n"
        return result
    }
}

let b = new Board()
console.log(b.render_table())