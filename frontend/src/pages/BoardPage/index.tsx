import "./index.scss"

import Board from "../../components/Board";
import Clock from "../../components/Clock";
import Jail from "../../components/Jail";

import { useState, useEffect } from 'react'

interface BoardPageProps {
  fenStringBoard: string;
  CapturedPiecesByWhite: string[];
  CapturedPiecesByBlack: string[];
}

export default function BoardPage({fenStringBoard, CapturedPiecesByWhite, CapturedPiecesByBlack}: BoardPageProps) {

    const [fenString, setFenString] = useState<string>(fenStringBoard);
    const [pieces_captured_white, setPiecesCapturedWhite] = useState<string[]>(CapturedPiecesByWhite);
    const [pieces_captured_black, setPiecesCapturedBlack] = useState<string[]>(CapturedPiecesByBlack);

    useEffect(() => {
      setFenString(fenStringBoard);
      setPiecesCapturedWhite(CapturedPiecesByWhite);
      setPiecesCapturedBlack(CapturedPiecesByBlack);
    }, [fenStringBoard, CapturedPiecesByWhite, CapturedPiecesByBlack]);
  
    console.log("BoardPage: ", fenString, pieces_captured_white, pieces_captured_black);
  
    
    return (
        <div className="board-page">
        <div className='info-zone white'>
          <div className='jail-zone'>
            <Jail pieces={pieces_captured_white} isWhite={false}  /> 
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
            <Jail pieces={pieces_captured_black} isWhite={true} />
          </div>
        </div>
      </div>
    );
}