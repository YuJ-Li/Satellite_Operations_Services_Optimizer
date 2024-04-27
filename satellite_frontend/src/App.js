import logo from './logo.svg';
import './App.css';
import Header from "./components/Header";
import { BrowserRouter as Router, Route, Routes,useLocation } from 'react-router-dom';
// Pages
import Home from './components/HomePage/HomePage';
import ViewDataPage from './components/ViewDataPage/ViewDataPage';
import AddSatellite from './components/AddSatellite/AddSatellite';
import AddGroundStation from './components/AddGroundStation/AddGroundStation';
import AddTask from './components/AddTask/AddTask';


function App() {
  return (
    <main className="main-container">
    <Routes>
      <Route path="/" element={<Header />}>
        <Route index element={<Home />} />
        <Route path="/add-satellite" element={<AddSatellite />} />
        <Route path="/add-groundstation" element={<AddGroundStation />} />
        <Route path="/add-task" element={<AddTask />} />
        <Route path="/view-data" element={<ViewDataPage />} />
      </Route>
    </Routes>
    </main>
  );
}

export default App;
