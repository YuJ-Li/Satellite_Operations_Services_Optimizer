import logo from './logo.svg';
import './App.css';
import HomePage from './components/HomePage/HomePage';
import ViewDataPage from './components/ViewDataPage/ViewDataPage';
import AddSatellite from './components/AddSatellite/AddSatellite';
import AddGroundStation from './components/AddGroundStation/AddGroundStation';
import AddOutage from './components/AddOutage/AddOutage';
import AddTask from './components/AddTask/AddTask';
import { BrowserRouter as Router, Route, Routes,useLocation } from 'react-router-dom';

function App() {
  return (
      <div className="App">
        <Router>
          <Routes>
            <Route exact path="/" element={<> <HomePage/> </>} />
            <Route path="/view-data" element={<> <ViewDataPage/> </>} />
            <Route path="/add-satellite" element={<> <AddSatellite/> </>} />
            <Route path="/add-groundstation" element={<> <AddGroundStation/> </>} />
            <Route path="/add-outage" element={<> <AddOutage/> </>} />
            <Route path="/add-task" element={<> <AddTask/> </>} />
          </Routes>
        </Router>
      </div>
  );
}

export default App;
