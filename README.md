# Ergasia_1_e18011_Antoniadi_Charis
Repository for assignment 1 of Information Systems course, containing an app.py file and a README file with a detailed description of the project.


## Preparation
Firstly we need to open a terminal window to start docker
```bash
sudo dockerd
```
Then in a new terminal window, we type the command bellow to start mongodb
```bash
sudo docker start mongodb
```
In mongodb we have created an InfoSys database with two collections. The fist one is called Students and contains the students.json file and the second one is called Users and contains the users.json file.
<p>If the app.py file isn't located in the default path, we use the cd command in order to relocate to the directory where the file.
When we are ready to run the project, we use the command python3 followed by the file name, as seen below</p>

```bash
python3 app.py
```
