import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddTask.css'; // Make sure to create this CSS file
import backgroundImage from '../../assets/background.jpg'; // Adjust the path as necessary

function AddTask() {
  const [taskType, setTaskType] = useState('MaintenanceTask');
  const [task, setTask] = useState({
    // Common attributes
    name: '',
    start_time: '',
    end_time: '',
    priority: '',
    duration: '',
    // MaintenanceTask specific
    next_maintenance: '',
    is_head: false,
    min_gap: '',
    max_gap: '',
    payload_outage: false,
    // ImageTask specific
    image_type: '',
    imagingRegionLatitude: '',
    imagingRegionLongitude: '',
    achievability: '',
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setTask({ ...task, [name]: type === 'checkbox' ? checked : value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Task to add:', task);
    // Add logic to send data to backend
    navigate('/'); // Navigate after submission
  };

  return (
    <div className="addTaskContainer" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <form onSubmit={handleSubmit} className="addTaskForm">
        <label>
          Task Type:
          <select name="taskType" value={taskType} onChange={(e) => setTaskType(e.target.value)}>
            <option value="MaintenanceTask">Maintenance Task</option>
            <option value="ImageTask">Image Task</option>
          </select>
        </label>
        {/* Common Task fields */}
        <label>
            Start Time:
            <input type="text" name="startTime" value={task.start_time} onChange={handleChange} />
        </label>
        <label>
            End Time:
            <input type="text" name="endTime" value={task.end_time} onChange={handleChange} />
        </label>
        <label>
            Priority:
            <input type="text" name="priority" value={task.priority} onChange={handleChange} />
        </label>
        {/* Conditional rendering for MaintenanceTask */}
        {taskType === 'MaintenanceTask' && (
          <>
            <label>
              Next Maintenance:
              <input type="text" name="next_maintenance" value={task.next_maintenance} onChange={handleChange} />
            </label>
            {/* Other MaintenanceTask specific fields */}
          </>
        )}
        {/* Conditional rendering for ImageTask */}
        {taskType === 'ImageTask' && (
          <>
            <label>
              Image Type:
              <input type="text" name="image_type" value={task.image_type} onChange={handleChange} />
            </label>
            <label>
              ImagingRegionLatitude:
              <input type="text" name="imagingRegionLatitude" value={task.imagingRegionLatitude} onChange={handleChange} />
            </label>
            <label>
              ImagingRegionLongitude:
              <input type="text" name="imagingRegionLongitude" value={task.imagingRegionLongitude} onChange={handleChange} />
            </label>
            {/* Other ImageTask specific fields */}
          </>
        )}
        <button type="submit">Add Task</button>
      </form>
    </div>
  );
}

export default AddTask;
