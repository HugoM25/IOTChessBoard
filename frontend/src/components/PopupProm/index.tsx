import './index.scss';
import React from 'react';
import { pieceMap } from "../../constants/pieces";

interface PopupPromProps {
  onClose: () => void;
  onSelect: (choice: string) => void;
  color: 'white' | 'black';
}

const PopupProm: React.FC<PopupPromProps> = ({ onClose, onSelect, color }) => {
  // Define promotion options based on color
  const promotionOptions = color === 'white' ? ['Q', 'N', 'R', 'B'] : ['q', 'n', 'r', 'b'];

  return (
    <div className="popup-overlay">
      <div>
        <h2>What should this pawn promote to?</h2>
        <div className="promotion-options">
          {promotionOptions.map(piece => (
            <button key={piece} onClick={() => onSelect(piece)}>
              <img src={pieceMap[piece]} alt={piece} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PopupProm;
