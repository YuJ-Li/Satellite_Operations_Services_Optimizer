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

  return (
    <div style={homePageStyle}>
      <div className="content">
        <h1>Welcome to the Satellite Optimization Tool</h1>
        <div className="buttonGroup">
          <button onClick={navigateToViewData}>View Data</button>
          <button>Add Satellite</button>
          <button>Add Ground Station</button>
          <button>Add Outage</button>
          <button>Add Tasks</button>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
