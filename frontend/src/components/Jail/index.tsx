import { pieceMap } from "../../constants/pieces";
import './index.scss';

interface JailProps {
    pieces: string[];
    isWhite: boolean;
}

export default function Jail(props: JailProps) {

    // Create a map to count occurrences of each piece
    const pieceCountMap: { [key: string]: number } = {};
    props.pieces.forEach(piece => {
        pieceCountMap[piece] = (pieceCountMap[piece] || 0) + 1;
    });

    // Order the pieces in this order : King, Queen, Rook, Bishop, Knight, Pawn
    const pieceOrder = ['K', 'Q', 'R', 'B', 'N', 'P'];
    // Sort the pieces by the order
    const sortedPieces = Object.keys(pieceCountMap).sort((a, b) => pieceOrder.indexOf(a.toUpperCase()) - pieceOrder.indexOf(b.toUpperCase()));

    // Create an array of 5 divs
    const divs = Array.from({ length: 5 }).map((_, index) => {
        const piece = sortedPieces[index];
        return (
            <div key={index} className="piece-container">
                {
                    piece && Array.from({ length: pieceCountMap[piece] }).map((_, i) => (
                        <img
                            key={`${piece}-${i}`}
                            src={pieceMap[piece]} // Use pieceMap to get the correct SVG path
                            alt={piece}
                            className={`jail-piece ${i > 0 ? 'same' : ''}`} // Add "same" class to subsequent pieces
                            style={{ left: `${i * 10}px` }} // Apply dynamic left position
                        />
                    ))
                }
            </div>
        );
    });

    return (
        <div className={`jail ${props.isWhite ? 'white' : 'black'}`}>
            {divs}
        </div>
    );
}