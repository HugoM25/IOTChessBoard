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

  // Function to handle promotion selection and API request
  const handleSelect = async (piece: string) => {
    try {
      // Make the API request to set the promotion piece type
      const response = await fetch('http://localhost:5000/api/v1/set_promotion_to', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ promotion_piece: piece }), // Send the selected piece
      });

      if (response.ok) {
        onSelect(piece); // Call the parent's onSelect handler
        onClose();       // Close the popup after selection
      } else {
        console.error('Failed to set promotion piece');
      }
    } catch (error) {
      console.error('Error setting promotion piece:', error);
    }
  };

  return (
    <div className="popup-overlay">
      <div>
        <h2>What should this pawn promote to?</h2>
        <div className="promotion-options">
          {promotionOptions.map(piece => (
            <button key={piece} onClick={() => handleSelect(piece)}>
              <img src={pieceMap[piece]} alt={piece} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PopupProm;
