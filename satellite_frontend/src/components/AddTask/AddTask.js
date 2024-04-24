import React, { useEffect, useState } from 'react';
import axios from 'axios'

const AddTask = () => {
  const [taskTypeOptions] = useState([
    { name: 'Maintenance Task', value: 'MaintenanceTask' },
    { name: 'Image Task', value: 'ImageTask' },
  ]);

  const [activeTaskType, setActiveTaskType] = useState('MaintenanceTask');
  const [task, setTask] = useState({
    name: '',
    jsonData: null,
  });

  useEffect(() => {
    // adds the active class as page loads
    let linkItem = document.querySelector("#task");

    linkItem.classList.add("active");

    return () => {
      // remove the active class as the page unmounts
      linkItem.classList.remove("active");
    };
  }, [activeTaskType]);


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
    try {
      console.log("!!!!!!!The task type is ",activeTaskType)
      let response = "";
      if (activeTaskType === "MaintenanceTask") {
        console.log("Enter as a maintenance task")
        response = await axios.post('http://localhost:8000/maintenanceTasks/', task);
      } else if (activeTaskType === "ImageTask") {
        console.log("Enter as an image task")
        response = await axios.post('http://localhost:8000/imagingTasks/', task);
      }
    
      console.log('Server response:', response);
    }
    catch (error) {
      console.error('Error posting data:', error);
    }
  };

  return (
    <section className="background task-page-container">
      <div className="task-page-wrapper">
        <div className="task-page-content-left">
          <div className="task-page-content-left-1">
              <span>03</span>
              <p>Add Task</p>
          </div>
          <div className="task-page-content-left-2">
              <img src="assets/earth.png" alt="earth" />
          </div>
        </div>

      <div className="task-page-content-right">
        <form onSubmit={handleSubmit} className="addTaskForm">
          <div className="task-page-content-right-nav">
            {taskTypeOptions.map(option => (
              <div
                id={option.value === activeTaskType ? "task" : ""}
                key={option.value}
                className="task-page-content-nav-item"
                onClick={() => setActiveTaskType(option.value)}
              >
                {option.name}
              </div>
            ))}
          </div>
          <label>
            Task Name:
            <input type="text" name="name" value={task.name} onChange={handleChange} required />
          </label>
          <label>
            Upload Json File:
            <input type="file" accept=".json" onChange={handleFileChange} />
          </label>
          <button type="submit">Add Task</button>
        </form>
      </div>
      </div>
    </section>
  );
}

export default AddTask;
