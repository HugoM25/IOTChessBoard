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

    // Create an array of unique pieces
    const uniquePieces = Object.keys(pieceCountMap);

    return (
        <div className={`jail ${props.isWhite ? 'white' : 'black'}`}>
            {
                uniquePieces.map((piece, index) => (
                    Array.from({ length: pieceCountMap[piece] }).map((_, i) => (
                        <img
                            key={`${piece}-${i}`}
                            src={pieceMap[piece]} // Use pieceMap to get the correct SVG path
                            alt={piece}
                            className={`jail-piece ${i > 0 ? 'same' : ''}`} // Add "same" class to subsequent pieces
                        />
                    ))
                ))
            }
        </div>
    );
}