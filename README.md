# Ergasia_1_e18011_Antoniadi_Charis
Repository for assignment 1 of Information Systems course, containing an app.py file and a README file with a detailed description of the project.


## Preparation
Firstly we need to open a terminal window to start docker
```bash
sudo dockerd
```
In a new terminal window, we type the commands bellow
```bash
sudo docker pull mongo #to pull the image from docker hub
sudo docker pull mongo:4.0.4 #to download the latest version of MONGODB image
sudo docker run -d -p 27017:27017 --name mongodb mongo:4.0.4 #to deploy image for the first time
sudo docker start mongodb #to start mongodb
```
Then we are going to use the Mongo Shell to create the InfoSys database, which will contain two collections. The fist one is called Students and contains the students.json file and the second one is called Users and contains the users.json file. To access the mongo shell we type:
```bash
sudo docker exec -it mongodb mongo
```
In Mongo Shell we type:
```bash
use InfoSys #to create InfoSys db
sudo docker cp students.json mongodb:/students.json #to copy data from host to container
docker exec -it mongodb mongoimport --db=InfoSys --collection=Students --file=students.json #to add the file to Students collection
sudo docker cp users.json mongodb:/users.json #to copy data from host to container
docker exec -it mongodb mongoimport --db=InfoSys --collection=Users --file=users.json #to add the file to Users collection
```
When we are ready to run the project, we use the command python3 followed by the file name, as seen below

```bash
python3 app.py
```
*note: If the app.py file isn't located in the default path, we use the cd command in order to relocate to the directory where the file.
