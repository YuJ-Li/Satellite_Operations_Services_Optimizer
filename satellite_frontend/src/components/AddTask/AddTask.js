import React, { useEffect, useState } from 'react';
import axios from 'axios'
import { useNavigate } from 'react-router-dom';

const AddTask = () => {
  const [taskTypeOptions] = useState([
    { name: 'Maintenance Task', value: 'MaintenanceTask' },
    { name: 'Image Task', value: 'ImageTask' },
  ]);

  const navigate = useNavigate();
  const [imageTasks, setImageTasks] = useState([]);
  const [maintenanceTasks, setMaintenanceTasks] = useState([]);
  const [activeTaskType, setActiveTaskType] = useState('MaintenanceTask');
  const [task, setTask] = useState({
    name: '',
    jsonData: null,
  });

  useEffect(() => {
    // adds the active class as page loads
    let linkItem = document.querySelector("#task");

    linkItem.classList.add("active");


    fetchData();
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
        const fileNameWithoutExtension = file.name.split('.').slice(0, -1).join('.');
        setTask({ ...task, jsonData: JSON.stringify(parsedJson), name: fileNameWithoutExtension })
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


  const fetchData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/imagingTasks/');
      setImageTasks(response.data);

      const response2 = await axios.get('http://localhost:8000/maintenanceTasks/')
      setMaintenanceTasks(response2.data)
    } catch (error) {
      console.error('Error fetching data:', error);
    }
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
      fetchData();
      window.location.reload();
    }
    catch (error) {
      console.error('Error posting data:', error);
    }

  };

  const handleDeleteM = async (taskName) => {
    try {
      const response = await axios.delete(`http://localhost:8000/maintenanceTasks/${taskName}/`);
      window.location.reload();
    }
    catch (error) {
      console.error('Error deleting task:', error);
    }
  };
  
  const handleDeleteI = async (taskName) => {
    try {
      const response = await axios.delete(`http://localhost:8000/imagingTasks/${taskName}/`);
      window.location.reload();
    }
    catch (error) {
      console.error('Error deleting task:', error);
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
        <div className="addTaskForm">
        <form onSubmit={handleSubmit} className='tForm'>
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
        <div className="task-table">
              <div className="table-title"><h2>Tasks</h2></div>
              <div className="table-content">
                <div className="table-left">
                  <table className="show-tasks-table">
                    <thead>
                      <tr>
                        <th>Imaging Tasks</th>
                        <th>Operation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {imageTasks.map((ImageTask, index) => (
                        <tr key={index}>
                          <td>{ImageTask.name}</td>
                          <td>
                            <button onClick={() => handleDeleteI(ImageTask.name)}>
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="table-right">
                  <table className="show-tasks-table">
                    <thead>
                      <tr>
                        <th>Maintenance Tasks</th>
                        <th>Operation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {maintenanceTasks.map((maintenance, index) => (
                        <tr key={index}>
                          <td>{maintenance.name}</td>
                          <td>
                            <button onClick={() => handleDeleteM(maintenance.name)}>
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
          </div>
        </div>
      </div>
      </div>
    </section>
  );
}

export default AddTask;
