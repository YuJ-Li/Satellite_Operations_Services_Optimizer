import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';


const AddGroundStation = () => {
  const [groundStation, setGroundStation] = useState({
    groundStationId: '',
    stationName: '',
    latitude: '',
    longitude: '',
    height: '',
    stationMask: '',
    uplinkRate: '',
    downlinkRate: '',
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setGroundStation({ ...groundStation, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Ground station to add:', groundStation);
    // Add logic to send data to backend
    navigate('/'); // Navigate after submission
  };

  return (
    <section className=" background ground-page-container">
      <div className="ground-page-title">
        <span>02</span>
        <p>Add Ground Stations</p>
      </div>
      <div className="ground-page-content-wrapper">
        <div className="ground-page-content-left">
          <div className="addGroundContainer">
            <form onSubmit={handleSubmit} className="addGroundForm">
              <label>
                Ground Station ID:
                <input type="text" name="groundStationId" value={groundStation.groundStationId} onChange={handleChange} required />
              </label>
              <label>
                Station Name:
                <input type="text" name="stationName" value={groundStation.stationName} onChange={handleChange} required />
              </label>
              <label>
                Latitude:
                <input type="number" name="latitude" value={groundStation.latitude} onChange={handleChange} required />
              </label>
              <label>
                Longitude:
                <input type="number" name="longitude" value={groundStation.longitude} onChange={handleChange} required />
              </label>
              <label>
                Height (meters):
                <input type="number" name="height" value={groundStation.height} onChange={handleChange} required />
              </label>
              <label>
                Station Mask:
                <input type="text" name="stationMask" value={groundStation.stationMask} onChange={handleChange} />
              </label>
              <label>
                Uplink Rate (Mbps):
                <input type="number" step="0.01" name="uplinkRate" value={groundStation.uplinkRate} onChange={handleChange} required />
              </label>
              <label>
                Downlink Rate (Mbps):
                <input type="number" step="0.01" name="downlinkRate" value={groundStation.downlinkRate} onChange={handleChange} required />
              </label>
              <button type="submit">Add Ground Station</button>
            </form>
          </div>
        </div>
        <div className="ground-page-content-right">
          <img src="assets/image-ground-portrait.jpg" alt='ground' />
        </div>
      </div>
    </section>
  );
}

export default AddGroundStation;
