import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddGroundStation.css'; // Reusing the CSS from AddSatellite for styling
import backgroundImage from '../../assets/background.jpg'; // Adjust the path as necessary

function AddGroundStation() {
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
    <div className="addContainer" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <form onSubmit={handleSubmit} className="addForm">
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
  );
}

export default AddGroundStation;
