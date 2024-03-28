import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddTask.css'; // Make sure to create this CSS file
import backgroundImage from '../../assets/background.jpg'; // Adjust the path as necessary
import axios from 'axios'



function AddTask() {
  const [taskType, setTaskType] = useState('MaintenanceTask');
  const [task, setTask] = useState({
  //   // Common attributes
  //   name: '',
  //   start_time: '',
  //   end_time: '',
  //   priority: '',
  //   duration: '',
  //   // MaintenanceTask specific
  //   next_maintenance: '',
  //   is_head: false,
  //   min_gap: '',
  //   max_gap: '',
  //   payload_outage: false,
  //   // ImageTask specific
  //   image_type: '',
  //   imagingRegionLatitude: '',
  //   imagingRegionLongitude: '',
  //   achievability: '',
    name: '',
    jsonData: null,
  });

  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    const reader = new FileReader()

    reader.onload = (event) => {
      const fileContent = event.target.result;
      try {
        const parsedJson = JSON.parse(fileContent)

        setTask({ ...task, jsonData: JSON.stringify(parsedJson) })
      } catch (error) {
        console.error('Error parsing JSON:', error);
      }
    }
    reader.readAsText(file)
  };


  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setTask({ ...task, [name]: type === 'checkbox' ? checked : value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Task to add:', task);
    // Add logic to send data to backend
    try {
      console.log("!!!!!!!The task type is ",taskType)
      var response = ""
      if (taskType==="MaintenanceTask"){
        console.log("Enter as a maintenance task")
        response = await axios.post('http://localhost:8000/maintenanceTasks/', task);
      } else if (taskType==="ImageTask"){
        console.log("Enter as an image task")
        response = await axios.post('http://localhost:8000/imagingTasks/', task);
      }
    
      console.log('Server response:', response);
      navigate('/'); // Navigate after submission
    }
    catch (error) {
      console.error('Error posting data:', error);
    }
  };

  return (
    <div className="addTaskContainer" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <form onSubmit={handleSubmit} className="addTaskForm">
        <label>
          Task Type:
          <select name="taskType" value={taskType || ''} onChange={(e) => setTaskType(e.target.value)}>
            <option value="MaintenanceTask">Maintenance Task</option>
            <option value="ImageTask">Image Task</option>
          </select>
        </label>
        <label>
          Task Name:
          <input type="text" name="name" value={task.name} onChange={handleChange} required />
        </label>
        <label>
          Upload Json File:
          <input type = "file" accept=".json" onChange={handleFileChange} />
        </label>
        
        <button type="submit">Add Task</button>
      </form>
    </div>
  );
}

export default AddTask;
