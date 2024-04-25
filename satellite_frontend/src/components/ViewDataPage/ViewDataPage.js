import React, { useState, useEffect } from 'react';
import axios from 'axios'

const ViewDataPage = () => {

  const [satellites, setSatellites] = useState([]);
  const [globalTime, setGlobalTime] = useState({
    time: '',
  });
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/satellites/');
        setSatellites(response.data); // Assuming the response.data is an array of satellites
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();

    // Clean-up function if needed
    return () => {
    };
  }, []); // Empty dependency array ensures useEffect only runs once on component mount


  const [groundStations] = useState([
    { groundStationId: 'GS1', stationName: 'Ground Station 1', latitude: 34.05, longitude: -118.25, height: 100, stationMask: 'mask1', uplinkRate: 100, downlinkRate: 150 },
    // Add more entries as needed
  ]);

  const [outages] = useState([
    { outageId: 'O1', startTime: '2023-01-02 10:00', endTime: '2023-01-02 12:00', groundStation: 'GS1', satellite: 'Satellite1' },
    // Add more entries as needed
  ]);

  // const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Time to change', globalTime);
    try {
      const response = await axios.post('http://localhost:8000/globalTime/', globalTime);
      console.log('Server response:', response);
      // navigate('/'); // Navigate after submission
    }
    catch (error) {
      console.error('Error posting data:', error);
    }
  };

  const handleChange = (e) => {
    setGlobalTime({ ...globalTime, [e.target.name]: e.target.value });
  };

  const backgroundStyle = {
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    minHeight: '100vh', // Ensure it covers the full viewport height
  };

  const handleClick = () => {
    // Refresh the page
    window.location.reload();
  };

  return (
    <section className="background data-page-container">
      <div className="data-page-wrapper">
        <div className="data-page-content-left">
          <div className="data-page-content-left-1">
              <span>04</span>
              <p>View Data</p>
          </div>
          <div className="data-page-content-left-2">
              <img src="assets/earth.png" alt="earth" />
          </div>
        </div>

        <div className="data-page-content-right">
          <form onSubmit={handleSubmit} className="setTimeForm">
            <label>
              Set Global Time:
              <input type="text" name="time" value={globalTime.time} onChange={handleChange} required/>
            </label>
            <button type="submit" onClick={handleClick}>Set Global Time and Generate Schedule</button>
            <div>
              <div className="table-title"><h2>Satellites</h2></div>
              
              <table className="schedule-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>TLE</th>
                    <th>Storage Capacity (KB)</th>
                    <th>Capacity Used (KB)</th>
                    <th>Schedule</th>
                    {/* <th>Maintenance Without Outage</th> */}
                  </tr>
                </thead>
                <tbody>
                  {satellites.map((satellite, index) => (
                    <tr key={index}>
                      <td>{satellite.name}</td>
                      <td>{satellite.tle}</td>
                      <td>{satellite.storage_capacity}</td>
                      <td>{satellite.capacity_used}</td>
                      <td>{satellite.schedule}</td>  
                      {/* <td>{satellite.maintenance_without_outage}</td> */}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </form>
          
        </div>
        
      </div>
    </section>
  );
}

export default ViewDataPage;
