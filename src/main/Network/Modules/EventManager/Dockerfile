FROM alpine:3.20.3

RUN apk add --no-cache python3
RUN apk add --no-cache py3-pip
RUN apk add --no-cache iperf3

WORKDIR /app

COPY src/main/Network/requirements.txt .

RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY src/main/Network .

COPY src/main/Central/ModuleManagement ModuleManagement

ARG VERSION
ENV VERSION=$VERSION

CMD ["python3", "Modules/EventManager/NetworkEventManagerModule.py"]
