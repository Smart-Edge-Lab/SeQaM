# Event Manager Docker Container
The dockerfile in this directory is containerizing the event manager and the stressor app.
To use this dockerfile as a stand-alone container, you need to build the docker image by running the following command: `docker build -f ./Dockerfile -t event_manager ../../`.  
***Note:*** The `../../` at the end of the command instead of `.` is to change the context where of the docker container, specifically so it can use some files inside other folders under the same parent. That is to say, to go back in the directory path.

Then you could run the docker container by running `docker run -it --name event_manager -p 8888:8888 --memory="7500m" --cpus="4" event_manager`.  
***Note:*** Notice that the docker compose file and the command above, both introduce  a hard limit of resources that the docker container can use, and this uses cgroups internally.

If you want to include another app to run in the same container please edit the docker file by adding your requirements, edit the context used in the docker build command if needed, and don't forget to edit the run command according to your needs.
