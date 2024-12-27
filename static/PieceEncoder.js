import { PieceType, Piece } from "./board_model.js";

export class PieceEncoder{
    constructor(){
        this.token_decoter = new Map();
        this.token_decoter.set("?", PieceType.UNKNOWN);
        this.token_decoter.set("S", PieceType.SPY);
        this.token_decoter.set("F", PieceType.FLAG);
        this.token_decoter.set("B", PieceType.BOMB);
        this.token_decoter.set("2", PieceType.SCOUT);
        this.token_decoter.set("3", PieceType.MINER);
        this.token_decoter.set("4", PieceType.SERGEANT);
        this.token_decoter.set("5", PieceType.LIEUTENANT);
        this.token_decoter.set("6", PieceType.CAPTAIN);
        this.token_decoter.set("7", PieceType.MAJOR);
        this.token_decoter.set("8", PieceType.COLONEL);
        this.token_decoter.set("9", PieceType.GENERAL);
        this.token_decoter.set("10", PieceType.MARSHAL);

        this.piece_encoder = new Map();
        for(let k of this.token_decoter.keys())
            this.piece_encoder.set(this.token_decoter.get(k), k);
    }

    decode_token(token){
        return this.token_decoter.get(token);
    }

    encode_piece(piece){
        return this.piece_encoder.get(piece.type)
    }
}

export function extract_setup(boardModel, invert = false){
    const result = [];
    const encoder = new PieceEncoder();
    for(let i = 0; i<100; ++i){
        if(boardModel.boardstate.squares[i].piece)
        result.push({
            sq: (invert)?99-i:i,
            piece: encoder.encode_piece(boardModel.boardstate.squares[i].piece)
        })
    }
    return result;
}