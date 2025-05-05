FROM python:3.12-slim

WORKDIR /app

COPY ./api/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./api/src /app

COPY ./common/src/seqam_data_fh_dortmund_project_emulate/ /app/seqam_data_fh_dortmund_project_emulate

ARG VERSION
ENV VERSION=$VERSION

CMD ["fastapi", "run", "--port", "80", "edpapi_fh_dortmund_project_emulate/app.py"]
