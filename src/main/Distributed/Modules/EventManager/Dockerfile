FROM alpine:3.20.3

RUN apk add --no-cache python3
RUN apk add --no-cache py3-pip
RUN apk add --no-cache stress-ng

WORKDIR /app

COPY Distributed/requirements.txt .

RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY Distributed .

COPY Central/ModuleManagement ModuleManagement

ARG VERSION
ENV VERSION=$VERSION

CMD ["python3", "Modules/EventManager/DistEventManagerModule.py"]
