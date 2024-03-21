import React from 'react';
import './HomePage.css'; // Importing CSS for styling
import backgroundImage from '../../assets/background.jpg'; // Importing the background image
import { useNavigate } from 'react-router-dom'; // Importing useNavigate instead of useHistory

function HomePage() {
  const navigate = useNavigate(); // useNavigate for navigation

  // Inline style for the background image
  const homePageStyle = {
    backgroundImage: `url(${backgroundImage})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    height: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  // Function to handle navigation
  const navigateToViewData = () => {
    navigate('/view-data');
  };

  const navigateToAddSatellite = () => {
    navigate('/add-satellite');
  };

  const navigateToGroundStation = () => {
    navigate('/add-groundstation');
  };

  const navigateToOutage = () => {
    navigate('/add-outage');
  };

  const navigateToTask = () => {
    navigate('/add-task');
  };
  return (
    <div style={homePageStyle}>
      <div className="content">
        <h1>Welcome to the Satellite Optimization Tool</h1>
        <div className="buttonGroup">
          <button onClick={navigateToViewData}>View Data</button>
          <button onClick={navigateToAddSatellite}>Add Satellite</button>
          <button onClick={navigateToGroundStation}>Add Ground Station</button>
          <button onClick={navigateToOutage}>Add Outage</button>
          <button onClick={navigateToTask}>Add Tasks</button>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
