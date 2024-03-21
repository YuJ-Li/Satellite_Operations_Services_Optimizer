import logo from './logo.svg';
import './App.css';
import HomePage from './components/HomePage/HomePage';
import ViewDataPage from './components/ViewDataPage/ViewDataPage';
import AddSatellite from './components/AddSatellite/AddSatellite';
import { BrowserRouter as Router, Route, Routes,useLocation } from 'react-router-dom';

function App() {
  return (
      <div className="App">
        <Router>
          <Routes>
            <Route exact path="/" element={<> <HomePage/> </>} />
            <Route path="/view-data" element={<> <ViewDataPage/> </>} />
            <Route path="/add-satellite" element={<> <AddSatellite/> </>} />
          </Routes>
        </Router>
      </div>
  );
}

export default App;
