import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Importing useNavigate instead of useHistory

const Home = () => {
  return (
    <section className=" background home-page-container">
      <div className="home-page-content-container">
        <div className="home-page-content-left">
          <p className="home-page-content-left-1"> Satellite Operations Services Optimizer</p>
          <h1 className="home-page-content-left-2"> SOSO</h1>
          <p className="home-page-content-left-3">
            Seamlessly scheduler and downlinking images from a constellation of imaging satellites.
          </p>
        </div>
        <div className="home-page-content-right-wrapper">

        </div>
      </div>
    </section>
  );
};

export default Home;
