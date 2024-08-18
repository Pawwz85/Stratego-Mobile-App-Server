describe("PieceType(Enum)", function() {
    it("Consists of members: FLAG, BOMB, SPY, SCOUT, MINER, SERGEANT, LIEUTENANT, CAPTAIN, MAJOR, COLONEL, GENERAL, MARSHAL, and UNKNOWN", function() {
      expect(PieceType.hasOwnProperty("FLAG")).toBeTruthy();
      expect(PieceType.hasOwnProperty("BOMB")).toBeTruthy();
      expect(PieceType.hasOwnProperty("SPY")).toBeTruthy();
      expect(PieceType.hasOwnProperty("SCOUT")).toBeTruthy();
      expect(PieceType.hasOwnProperty("MINER")).toBeTruthy();
      expect(PieceType.hasOwnProperty("SERGEANT")).toBeTruthy();
      expect(PieceType.hasOwnProperty("LIEUTENANT")).toBeTruthy();
      expect(PieceType.hasOwnProperty("CAPTAIN")).toBeTruthy();
      expect(PieceType.hasOwnProperty("MAJOR")).toBeTruthy();
      expect(PieceType.hasOwnProperty("COLONEL")).toBeTruthy();
      expect(PieceType.hasOwnProperty("GENERAL")).toBeTruthy();
      expect(PieceType.hasOwnProperty("MARSHAL")).toBeTruthy();
      expect(PieceType.hasOwnProperty("UNKNOWN")).toBeTruthy();
    });
  });

  describe("Color(Enum)", function(){
    it("Consists of members: RED and Blue", function(){
        expect(Color.hasOwnProperty("BLUE")).toBeTruthy();
        expect(Color.hasOwnProperty("RED")).toBeTruthy();
    })
  })

  describe('Piece', () => {
    let piece;
  
    beforeEach(() => {
      piece = new Piece(Color.RED, PieceType.LIEUTENANT);
    });
  
    it('should create a piece with a color and type', () => {
      expect(piece.color).toEqual(Color.RED);
      expect(piece.type).toEqual(PieceType.LIEUTENANT);
    });
  
    it('should copy the piece and preserve its properties', () => {
      const copiedPiece = piece.copy();
      expect(copiedPiece).not.toBe(piece);
      expect(copiedPiece.color).toEqual(Color.RED);
      expect(copiedPiece.type).toEqual(PieceType.LIEUTENANT);
    });
  });

  describe('Square', () => {
    let square;
  
    beforeEach(() => {
      square = new Square();
    });
  
    it('should create a square with default properties', () => {
      expect(square.index).toEqual(0);
      expect(square.piece).toBeNull();
      expect(square.draw_dot).toBeFalsy();
      expect(square.highlight).toBeFalsy();
    });
  
    it('should copy a square and preserve its properties', () => {
      square.index = 42;
      square.piece = new Piece(Color.RED, PieceType.GENERAL);
      square.draw_dot = true;
      square.highlight = false;
      const copiedSquare = square.copy();
      expect(copiedSquare).not.toBe(square);
      expect(copiedSquare.index).toEqual(42);
      expect(copiedSquare.piece).not.toBeNull();
      expect(copiedSquare.piece.color).toEqual(Color.RED);
      expect(copiedSquare.piece.type).toEqual(PieceType.GENERAL);
      expect(copiedSquare.draw_dot).toBeTruthy();
      expect(copiedSquare.highlight).toBeFalsy();
    });

    it('should copy a square and perform a deep copy for the piece property', () => {
        const piece = new Piece(Color.RED, PieceType.GENERAL);
        piece.draw_dot = true;
        piece.highlight = false;
        square.piece = piece;
        const copiedSquare = square.copy();
        expect(copiedSquare).not.toBe(square);
        expect(copiedSquare.piece).not.toBeNull();
        expect(copiedSquare.piece).not.toBe(square.piece);
      });
  });

  describe("BoardState", function(){
    let boardState;

    const is_empty = boardState => {
      for (let i = 0; i < boardState.squares.length; ++i){
        let sq = boardState.squares[i];
        if(sq.piece != null)
          return false;
      }
      return true;
    }

    beforeEach(function(){
      boardState = new BoardState();
      boardState.squares[99].piece = new Piece(Color.RED, PieceType.FLAG);
      boardState.squares[0].piece = new Piece(Color.BLUE, PieceType.FLAG);
    })

    it("can be cleared using reset() method", function(){
      boardState.reset();
      expect(is_empty(boardState)).toBe(true);
    })

    it("it can be assigning position, using array of pairs [square_index, piece] using set_position() method", function(){
      boardState.reset();
      state = [
        [0, new Piece(Color.RED, PieceType.FLAG)],
        [99, new Piece(Color.BLUE, PieceType.FLAG)],
        [50, new Piece(Color.BLUE, PieceType.BOMB)]
      ];

      boardState.set_position(state);

      for(let i = 0; i< 100; ++i)
        switch(i){
          case 0:
            expect(boardState.squares[i].piece?.color == Color.RED && boardState.squares[i].piece?.type == PieceType.FLAG).toBe(true);
            break;
          case 50:
            expect(boardState.squares[i].piece?.color == Color.BLUE && boardState.squares[i].piece?.type == PieceType.BOMB).toBe(true);
            break;
          case 99:
            expect(boardState.squares[i].piece?.color == Color.BLUE && boardState.squares[i].piece?.type == PieceType.FLAG).toBe(true);
            break;
          default:
            expect(boardState.squares[i].piece).toBe(null);
            break;
        }
    } 
    )
    
    it("it implements observer design pattern and will execute method 'set_state(boardstate) of all its observers'", function(){
      let was_observed_called = false;
      observer = {
        set_state(boardstate){
          was_observed_called = true;
        }
      }
      boardState.observers.push(observer);
      boardState.notify_observers();
      expect(was_observed_called).toBeTruthy();
    })

    it("can be deep copied using 'copy() method'", function(){
      const copy = boardState.copy();

      expect(copy).not.toBe(boardState);

      for( let i = 0; i<copy.squares.length; ++i){
        expect(boardState.squares[i]).not.toBe(copy.squares[i]);

        if(copy.squares[i].piece == null)
          expect(boardState.squares[i].piece).toBeNull();
        else{
          expect(boardState.squares[i].piece).not.toBe(copy.squares[i].piece);
          expect(boardState.squares[i].piece.color).toEqual(copy.squares[i].piece.color);
          expect(boardState.squares[i].piece.type).toEqual(copy.squares[i].piece.type);
        }
      }
        

    })

  });

  describe("BoardModel", function(){
    it("accepts move generator and boards state and copies them", function(){
      const move_gen = new MoveGenerator();
      const state = new BoardState();
      const move_gen_spy = spyOn(move_gen, "copy");
      const state_spy = spyOn(state, "copy");
      const model = new BoardModel(move_gen, state);
      
      expect(move_gen_spy).toHaveBeenCalled();
      expect(state_spy).toHaveBeenCalled();
    })

    it("'set_selected_square_id()' invoke refresh_board_visuals only if value of selected_square_id changed", function(){
      const model = new BoardModel(new MoveGenerator(),  new BoardState());

      const visual_spy = spyOn(model, "refresh_board_visuals");

      model.selected_sq_id = 7;

      model.set_selected_square_id(7);
      expect(visual_spy).not.toHaveBeenCalled();
      model.set_selected_square_id(99);
      expect(visual_spy).toHaveBeenCalled();
      expect(model.selected_sq_id).toEqual(99);
    })
  })