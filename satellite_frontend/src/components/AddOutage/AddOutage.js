import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddOutage.css'; // Assuming we're reusing the CSS from the AddSatellite component
import backgroundImage from '../../assets/background.jpg'; // Adjust the path as necessary
function AddOutage() {
  const [outage, setOutage] = useState({
    outageId: '',
    startTime: '',
    endTime: '',
    groundStation: '',
    satellite: '',
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setOutage({ ...outage, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Outage to add:', outage);
    // Add logic to send data to backend
    navigate('/'); // Navigate after submission
  };

  return (
    <div className="addContainer" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <form onSubmit={handleSubmit} className="addForm">
        <label>
          Outage ID:
          <input type="text" name="outageId" value={outage.outageId} onChange={handleChange} required />
        </label>
        <label>
          Start Time (YYYY-MM-DD HH:MM:SS):
          <input type="text" name="startTime" value={outage.startTime} onChange={handleChange} required />
        </label>
        <label>
          End Time (YYYY-MM-DD HH:MM:SS):
          <input type="text" name="endTime" value={outage.endTime} onChange={handleChange} required />
        </label>
        <label>
          Ground Station ID:
          <input type="text" name="groundStation" value={outage.groundStation} onChange={handleChange} required />
        </label>
        <label>
          Satellite Name:
          <input type="text" name="satellite" value={outage.satellite} onChange={handleChange} required />
        </label>
        <button type="submit">Add Outage</button>
      </form>
    </div>
  );
}

export default AddOutage;
