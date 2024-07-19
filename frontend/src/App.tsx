import './App.scss'

import BoardPage from './pages/BoardPage';
import Settings from './pages/Settings';

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {

  return (
    <>
      <div>

        <Router>
          <Routes>
            <Route path="/" element={<BoardPage/>} />
            <Route path="/settings" element={<Settings/>} />
          </Routes>
        </Router>
       
        <div className="page-selection-zone">
          <h1>Chess Board</h1>
        </div>
      </div>
    </>
  )
}

export default App
