FROM alpine:3.20.3

RUN apk add --no-cache python3
RUN apk add --no-cache py3-pip
RUN apk add --no-cache stress-ng
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers

WORKDIR /app

COPY src/main/Distributed/requirements.txt .

RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY common/src .

COPY src/main/Distributed .

COPY src/main/Central/ModuleManagement ModuleManagement

ARG VERSION
ENV VERSION=$VERSION

CMD ["python3", "Modules/EventManager/DistEventManagerModule.py"]
