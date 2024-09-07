import "./index.scss"
import { useState } from 'react'

export default function MainPage() {

    return (
        <>
        <div className="main-page">
                <div>
                    <button className="btn_style1">Start Game</button>
                </div>
                <div>
                    <input type="text" className="fen_input" placeholder="FEN STRING"  />
                    <button className="btn_style1">Load fen position</button>                    
                </div>
        </div>
        </>
    );
}