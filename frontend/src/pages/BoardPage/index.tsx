import "./index.scss"

import Board from "../../components/Board";
import Clock from "../../components/Clock";
import Jail from "../../components/Jail";

import { useState } from 'react'


export default function BoardPage() {

    const [fenString, setFenString] = useState<string>("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");

    return (
        <div className="board-page">
        <div className='info-zone white'>
          <div className='jail-zone'>
            <Jail pieces={['B', 'B', 'Q', 'P', 'N', 'P', 'P']} isWhite={false}  /> 
          </div>
          <div className="clock-zone">
            <Clock isWhite={true} />
          </div>
        </div>
        <div className='board-display-zone'>
          <Board fenString={fenString} />
        </div>
        <div className="info-zone black">
          <div className="clock-zone">
            <Clock isWhite={false} />
          </div>
          <div className='jail-zone'>
            <Jail pieces={['b', 'b', 'p', 'p', 'r', 'n', 'p', 'p']} isWhite={true} />
          </div>
        </div>
      </div>
    );
}