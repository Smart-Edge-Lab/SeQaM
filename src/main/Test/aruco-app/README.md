# Aruco App

## Installation

- Install both server and client requirements via pip
```bash
pip intall -r requirements.txt
```
- Change the IP address for the collector in both files client.py and server.py
- You migth also need to update the server address in the client.py if you are running the server in a different machine


## Testing

Make sure you have the collector running and that you have properly configured the IP
to send traces from the scripts

Run the docker compose

```bash
docker compose up --build
```
