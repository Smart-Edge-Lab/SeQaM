FROM ubuntu:22.04

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y curl iproute2 net-tools python3 iputils-ping traceroute python3-pip libgl1-mesa-glx libgtk2.0-dev && \
    apt-get clean

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "client.py"]