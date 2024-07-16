import { useState } from 'react'
import './App.scss'
import Board from './components/Board'
import Clock from './components/Clock';
import Jail from './components/Jail';

function App() {
  const [fenString, setFenString] = useState<string>("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");

  return (
    <>
      <div>
        <div className="board-zone">
          <div className='info-zone white'>
              <Clock isWhite={true} />
              <Jail pieces={['B', 'B', 'Q', 'P', 'N', 'P', 'P']} isWhite={false}  />
          </div>
          <div className='board-display-zone'>
            <Board fenString={fenString} />
          </div>
          <div className="info-zone black">
              <Clock isWhite={false} />
              <Jail pieces={['b', 'b', 'p', 'p', 'r', 'n', 'p', 'p']} isWhite={true} />
          </div>
        </div>
      </div>
    </>
  )
}

export default App
