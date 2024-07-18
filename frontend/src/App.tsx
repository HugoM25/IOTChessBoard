import { useState } from 'react'
import './App.scss'
import Board from './components/Board'
import Clock from './components/Clock';
import Jail from './components/Jail';

function App() {
  const [fenString, setFenString] = useState<string>("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");

  const handlePreviousClick = () => {
      // Logic for handling previous button click
      console.log('Previous button clicked');
  };

  const handleNextClick = () => {
      // Logic for handling next button click
      console.log('Next button clicked');
  };
  return (
    <>
      <div>
        <div className="board-page">
          <div className='info-zone white'>
            <div className='jail-zone'>
              <Jail pieces={['B', 'B', 'Q', 'P', 'N', 'P', 'P']} isWhite={false}  /> 
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
              <Jail pieces={['b', 'b', 'p', 'p', 'r', 'n', 'p', 'p']} isWhite={true} />
            </div>
          </div>
        </div>
        <div className="page-selection-zone">
          <button onClick={handlePreviousClick}></button>
          <button onClick={handlePreviousClick}></button>
          <button onClick={handleNextClick}></button>
        </div>
      </div>
    </>
  )
}

export default App
