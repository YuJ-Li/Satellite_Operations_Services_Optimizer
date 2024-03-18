import React, { useState } from 'react';
import './ViewDataPage.css'; // Importing the CSS file for styling
import backgroundImage from '../../assets/background.jpg';
function ViewDataPage() {
  const [satellites] = useState([
    { name: 'Satellite1', maintenance_without_outage: '[]', schedule: '[]', tle: 'TLE Data', storage_capacity: 500, capacity_used: 250 },
    // Add more entries as needed
  ]);

  const [tasks] = useState([
    { name: 'Task1', start_time: '2023-01-01 10:00', end_time: '2023-01-01 12:00', priority: 1, duration: '2 hours' },
    // Add more entries as needed
  ]);

  const [groundStations] = useState([
    { groundStationId: 'GS1', stationName: 'Ground Station 1', latitude: 34.05, longitude: -118.25, height: 100, stationMask: 'mask1', uplinkRate: 100, downlinkRate: 150 },
    // Add more entries as needed
  ]);

  const [outages] = useState([
    { outageId: 'O1', startTime: '2023-01-02 10:00', endTime: '2023-01-02 12:00', groundStation: 'GS1', satellite: 'Satellite1' },
    // Add more entries as needed
  ]);

  const backgroundStyle = {
    backgroundImage: `url(${backgroundImage})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    minHeight: '100vh', // Ensure it covers the full viewport height
  };

  return (
    <div className="viewDataPage" style={backgroundStyle}>
      <h1>View Data</h1>
      <div className="dataSection">
        <h2>Satellites</h2>
        <table className="dataTable">
          <thead>
            <tr>
              <th>Name</th>
              <th>Maintenance Without Outage</th>
              <th>Schedule</th>
              <th>TLE</th>
              <th>Storage Capacity (KB)</th>
              <th>Capacity Used (KWh)</th>
            </tr>
          </thead>
          <tbody>
            {satellites.map((satellite, index) => (
              <tr key={index}>
                <td>{satellite.name}</td>
                <td>{satellite.maintenance_without_outage}</td>
                <td>{satellite.schedule}</td>
                <td>{satellite.tle}</td>
                <td>{satellite.storage_capacity}</td>
                <td>{satellite.capacity_used}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Repeat for tasks, ground stations, and outages */}
    </div>
  );
}

export default ViewDataPage;
