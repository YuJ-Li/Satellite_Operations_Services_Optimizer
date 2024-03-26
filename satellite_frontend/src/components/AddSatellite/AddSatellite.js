import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddSatellite.css'; // Importing the CSS file for styling
import backgroundImage from '../../assets/background.jpg';  // Adjust the path as necessary
import axios from 'axios'

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Satellite to add:', satellite);
    try {
      const response = await axios.post('http://localhost:8000/satellites/', satellite);
      console.log('Server response:', response);
      navigate('/'); // Navigate after submission
    }
    catch (error) {
      console.error('Error posting data:', error);
    }
  };

  return (
    <div className="addSatelliteContainer" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <form onSubmit={handleSubmit} className="addSatelliteForm">
        <label>
          Satellite Name:
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
        <button type="submit">Add Satellite</button>
      </form>
    </div>
  );
}

export default AddSatellite;
