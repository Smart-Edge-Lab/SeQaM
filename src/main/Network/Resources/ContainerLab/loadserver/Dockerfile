  FROM ubuntu:22.04
  RUN apt-get update -y
  RUN apt-get upgrade -y
  RUN apt-get install -y curl
  RUN apt install -y iproute2
  RUN apt-get install net-tools -y
  RUN apt-get install -y python3 iputils-ping traceroute 
  #RUN apt-get install python3-pip
  RUN apt-get install -y python3-pip 
  
  WORKDIR /app
  
  
  COPY . .

  #RUN pip3 install requirements.txt
  RUN pip3 install -r requirements.txt
  EXPOSE 8080

  CMD ["python3", "sockser.py"]
