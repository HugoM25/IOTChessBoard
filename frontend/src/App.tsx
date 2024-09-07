import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import io from 'socket.io-client';

import './App.scss';
import BoardPage from './pages/BoardPage';
import Settings from './pages/Settings';
import PageSelector from './components/PageSelector';
import MainPage from './pages/MainPage'; 

import PopupProm from './components/PopupProm';


const socket = io('http://localhost:5000', {
  transports: ['websocket', 'polling']
});


function App() {
  const [fenString, setFenString] = useState<string>("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  const [pieces_captured_white, setPiecesCapturedWhite] = useState<string[]>([]);
  const [pieces_captured_black, setPiecesCapturedBlack] = useState<string[]>([]);
  const [timerWhite, setTimerWhite] = useState<number>(0);
  const [timerBlack, setTimerBlack] = useState<number>(0);

  const [isPopupOpen, setIsPopupOpen] = useState<boolean>(false);
  const [promotionChoice, setPromotionChoice] = useState<string | null>(null);

  const handleClosePopup = () => {
    setIsPopupOpen(false);
  };

  const handlePromotionSelect = (choice: string) => {
    setPromotionChoice(choice);
    console.log('Promotion choice:', choice);
    handleClosePopup();
  };

  useEffect(() => {
    socket.on('reload_backend', async () => {
      console.log('Reloading backend');
      try {
        const response = await fetch('http://localhost:5000/api/v1/chess_engine_data');
        const data = await response.json();
        console.log(data);
        const newFen = data.board_infos.board_fen.split(' ')[0];
        console.log("New FEN: ", newFen);
        setFenString(newFen);

        // Check if captured_pieces exists and is an array
        const capturedPieces = Array.isArray(data.board_infos.captured_pieces) ? data.board_infos.captured_pieces : [];
                
        // Filter captured pieces by color
        const whiteCaptured = capturedPieces.filter((piece: { color: string, name: string;}) => piece.color === 'w').map(piece => piece.name);
        const blackCaptured = capturedPieces.filter((piece: { color: string, name: string;}) => piece.color === 'b').map(piece => piece.name); 

        setPiecesCapturedWhite(whiteCaptured);
        setPiecesCapturedBlack(blackCaptured);

        console.log(pieces_captured_white);
        console.log(pieces_captured_black);

        
        
        setTimerWhite(data.board_infos.clocks.white as number);
        setTimerBlack(data.board_infos.clocks.black as number);  

        setIsPopupOpen(true); 


      }
      catch (error) {
        console.error('Error:', error);
      }
    }); 

    return () => {
      socket.off('reload_backend');
    };
  }, []);

  return (
    <>
      <div>
        <Router>
          <div className='main-zone'>
          <Routes>
            <Route path="/" element={<BoardPage fenStringBoard={fenString}
                                     CapturedPiecesByWhite={pieces_captured_white} CapturedPiecesByBlack={pieces_captured_black} timerBlack={timerBlack} timerWhite={timerWhite} />} />
            
            <Route path="/settings" element={<Settings/>} />

            <Route path="/jsp" element={<MainPage/>} />
          </Routes>
          </div>
          <div className="page-selection-zone">
            <PageSelector />
          </div>
          {isPopupOpen && (
              <PopupProm onClose={handleClosePopup} onSelect={handlePromotionSelect} />
            )}
        </Router>
      </div>
    </>
  )
}

export default App
