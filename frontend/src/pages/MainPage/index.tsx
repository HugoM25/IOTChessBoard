import "./index.scss";
import { useState } from 'react';

export default function MainPage() {
    const [fen, setFen] = useState('');

    const startGame = async () => {
        const defaultFen = "rnbqkb1r/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"; // Default starting FEN

        const fenPosStart = fen.trim() || defaultFen; // Use the FEN from input or default

        try {
            const response = await fetch('http://localhost:5000/api/v1/start_new_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ fen_pos_start: fenPosStart }),
            });

            console.error("Does this work?");

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Error starting game:", errorData.error);
            } else {
                const data = await response.json();
                console.log(data.message); // Handle the success response
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };

    return (
        <>
            <div className="main-page">
                <div>
                    <button className="btn_style1" onClick={startGame}>Start Game</button>
                </div>
                <div>
                    <input 
                        type="text" 
                        className="fen_input" 
                        placeholder="FEN STRING" 
                        value={fen}
                        onChange={(e) => setFen(e.target.value)} 
                    />
                    <button className="btn_style1">Load fen position</button>                    
                </div>
            </div>
        </>
    );
}
