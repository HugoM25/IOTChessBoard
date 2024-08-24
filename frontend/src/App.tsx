import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import io from 'socket.io-client';

import './App.scss';
import BoardPage from './pages/BoardPage';
import Settings from './pages/Settings';
import PageSelector from './components/PageSelector';

const socket = io('http://localhost:5000', {
  transports: ['websocket', 'polling']
});

function App() {
  const [fenString, setFenString] = useState<string>("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  const [pieces_captured_white, setPiecesCapturedWhite] = useState<string[]>([]);
  const [pieces_captured_black, setPiecesCapturedBlack] = useState<string[]>([]);
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
        setPiecesCapturedWhite([]);
        setPiecesCapturedBlack([]);
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
                                     CapturedPiecesByWhite={pieces_captured_white} CapturedPiecesByBlack={pieces_captured_black} />} />
            
            <Route path="/settings" element={<Settings/>} />

            <Route path="/jsp" element={<h1>JSP</h1>} />
          </Routes>
          </div>
          <div className="page-selection-zone">
            <PageSelector />
          </div>
        </Router>
      </div>
    </>
  )
}

export default App
