import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddSatellite.css'; // Importing the CSS file for styling
import backgroundImage from '../../assets/background.jpg';  // Adjust the path as necessary

function AddSatellite() {
  const [satellite, setSatellite] = useState({
    name: '',
    maintenance_without_outage: '[]',
    schedule: '[]',
    tle: '',
    storage_capacity: '',
    capacity_used: '',
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setSatellite({ ...satellite, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Satellite to add:', satellite);
    // Add logic to send data to backend
    navigate('/'); // Navigate after submission
  };

  return (
    <div className="addSatelliteContainer" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <form onSubmit={handleSubmit} className="addSatelliteForm">
        <label>
          Name:
          <input type="text" name="name" value={satellite.name} onChange={handleChange} required />
        </label>
        {/* Repeat for other fields */}
        <label>
          TLE:
          <input type="text" name="tle" value={satellite.tle} onChange={handleChange} required />
        </label>
        <label>
          Storage Capacity (KB):
          <input type="number" name="storage_capacity" value={satellite.storage_capacity} onChange={handleChange} required />
        </label>
        <label>
          Capacity Used (kWh):
          <input type="number" name="capacity_used" value={satellite.capacity_used} onChange={handleChange} required />
        </label>
        <button type="submit">Add Satellite</button>
      </form>
    </div>
  );
}

export default AddSatellite;
