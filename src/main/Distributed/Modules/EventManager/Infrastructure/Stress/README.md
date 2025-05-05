#### **BIG NOTE: this currently not viable as the functionality of the stressor got integrated with the event manager.**

# Introduction
This branch is dedicated for the development of a stressor, using the tool called `stress-ng`. 
###### Note: keep in mind that this script only runs on Unix machines.
# Work
The current functionality of this stressor can be summarized with the following steps:
    1. One thread is running a *flask* server and listening to API events on multiple endpoints, and then creating a data model to host the stress event. 
    2. Another thread is reading this stress event and executing the stress-ng command based on the stress event parameters.

# Data Model
The data model is a simple class that holds the stress event parameters. It is designed to be used by the flask server to host the stress event in a way so that the stressor can read it and execute the stress-ng command. It also performs some basic validation on the API event to make sure that it contains the required parameters.

# How to run
1. To run this stressor, you have to clone the repository to your machine, then navigate to `src/main/Distributed/Modules/EventManager/Infrastructure/Stress`.
2. Change the permissions of the bash/shell script to be able to run it using `chmod +x run_script.sh` 
3. Now you should be able to run the bash/shell script by running the following command `sudo ./run_script.sh`.
   1. Running this script will create a virtual environment, and install the required dependencies in it. It will also use that virtual environment to run the stressor. If you want to delete the virtual enviroment folder **venv**, you can run the following command `sudo rm -R venv`.
4. To be able to send API events to the stressor, please take a notice of the IP:Port address you have in your terminal after running the script.
