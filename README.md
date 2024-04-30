# Satellite_tasking_optimization (Group 22)

## Project Description
2023 McGill Capstone project with ASC/CSA

## Supervisors
| Name                      |                  Email                  |          Organization             |
|:-------------------------:|:---------------------------------------:|:---------------------------------:|
| Nathaniel Cziranka-Crooks | nathaniel.cziranka-crooks@asc-csa.gc.ca |        Canadian Space Agency      |
| Patrick Ivrin             |       patrick.irvin@asc-csa.gc.ca       |        Canadian Space Agency      |
| Dennis Giannacopoulos     |    dennis.giannacopoulos@mcgill.ca      | McGill University ECE Departement |


## Team Members (Group 22)
| Name                      | ID        | Email                                  |                   Major & Minor                        |                 GitHub Profile                |
|:-------------------------:|:---------:|:--------------------------------------:|:------------------------------------------------------:|:---------------------------------------------:|
| Noshin Saiyara Chowdhury  | 260971544 | noshin.chowdhury2@mail.mcgill.ca       | Computer Engineering                                   | [Noshin03](https://github.com/Noshin03)       |
| Kaifan Zheng              | 260962377 | kaifan.zheng@mail.mcgill.ca            | Computer Engineering                                   | [kaifanzheng](https://github.com/kaifanzheng) |
| Chun Li                   | 260986765 | chun.li4@mail.mcgill.ca                | Software Engineering & Applied Artificial Intelligence | [chun-li9](https://github.com/chun-li9)       |
| Yujin Li                  | 260968957 | yiujin.li@mail.mcgill.ca               | Software Engineering & Applied Artificial Intelligence | [YuJ-Li](https://github.com/YuJ-Li)           |

## Additional details
For further details, please visit our [wiki page](https://github.com/YuJ-Li/Satellite_tasking_optimization/wiki)

## Open the this project in dev container
Open the root directory in VSCode. While making sure Docker is running on your machine and there is no folder named `data` under the root directory, `CTRL+SHIFT+P` and search for `Dev Containers: Rebuild and Reopen in Container`.

Wait for the container to open, then access the application at http://localhost:7000/. To connect to this Git repository inside the dev container, go to `Source Control` -> `Manage Unsafe Repositories` -> choose `app`.

In the bash shell of the container, run the following command to migrate data:

```
python manage.py migrate
```

To run tests, use

```
python manage.py test <test-module>
```

## Build Production Image and Run Container

In terminal, go to the directory `Satellite_Operations_Services_Optimizer/Satellite_Operations_Services_Optimizer`. While making sure Docker is running on your machine and there is no folder named `data` under this directory, run the following command to build the Docker image of this application: 

```
docker-compose build
```

Then run the following command to start the container:

```
docker-compose up
```

After the container has started, in another terminal, run the following command and get into the shell of the container:

```
docker exec -it soso-container /bin/bash
```

In the shell, you can run commands like `python manage.py test <test-module>` as in the dev container.

## Run Project
To initiate the backend, navigate to the directory `Satellite_Operations_Services_Optimizer/Satellite_Operations_Services_Optimizer` and execute the following command:

```
python manage.py runserver 0.0.0.0:8000
```

To launch the frontend, go to the directory  `Satellite_Operations_Services_Optimizer/satellite_frontend`, and execute the following command:
```
npm start
```

After a brief moment, the web app will be accessible at localhost:3000/.

## User Manual
For the best user experience, we suggest running the web app on a 2K screen. Currently, we haven't implemented responsive design, so utilizing a 2K display will ensure that the content is displayed optimally without any layout adjustments intended for smaller screens.
### Home page
Upon entering the app, you will land directly on the home page.

![](https://github.com/YuJ-Li/Satellite_Operations_Services_Optimizer/blob/main/demo/home.png)

To begin, simply navigate to the Satellite page.

### Satellite Page
On this page, you have the option to add a satellite by entering its name and the corresponding Two-Line Element (TLE) data. You can find some sample TLEs in the "TLE/" directory, which you can use directly. Please note that satellites should be added one by one.

![](https://github.com/YuJ-Li/Satellite_Operations_Services_Optimizer/blob/main/demo/satellites.png)

Then navigate to the Groundstation Page
### Groundstation Page
The Groundstation page is currently a placeholder and does not affect the outcome of the application.

![](https://github.com/YuJ-Li/Satellite_Operations_Services_Optimizer/blob/main/demo/groundstations.png)

Then go to the Tasks Page
### Tasks Page
On this page, you can add one or multiple tasks by specifying type of task, task name and uploading the corresponding JSON file(s). Sample tasks are available in the "/order_samples" directory. Specifically, "group2," "group3," and "group4_newest" contain imaging tasks, while "m_group1" and "m_group2" consist of miscellaneous tasks. Additionally, you can delete a task by clicking on the delete button next to it.

![](https://github.com/YuJ-Li/Satellite_Operations_Services_Optimizer/blob/main/demo/tasks.png)

Next go to the Data page
### Data Page
On this page, you have the capability to set a global time for testing purposes. This time setting allows you to generate a complete schedule for all satellites. While in reality, the algorithm would operate based on the current time, for observation of performance, it currently operates according to the time set by the user. The time format should adhere to the 24-hour clock system as the following:

```
YYYY-MM-DD HH:MM:SS
```

The scheduling for the following 48 hours will then appear in the table below

![](https://github.com/YuJ-Li/Satellite_Operations_Services_Optimizer/blob/main/demo/data.png)


