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
Open the `Satellite_Operations_Services_Optimizer/Satellite_Operations_Services_Optimizer` folder in VSCode. While making sure Docker is running, `CTRL+SHIFT+P` and search for `Dev Containers: Rebuild and Reopen in Container`.

Wait for the container to open, then access the application at http://localhost:8000/. In the bash shell of the container, run the following command to migrate data:

```
python manage.py migrate
```

To run tests, use

```
python manage.py test <test-module>
```
