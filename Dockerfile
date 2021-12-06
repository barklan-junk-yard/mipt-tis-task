ARG DOCKER_IMAGE_PREFIX=
FROM ${DOCKER_IMAGE_PREFIX}python:3.9

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y gcc python3-dev ufw

# install dependencies
RUN pip install --upgrade pip wheel
COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

# copy project
COPY . .

# run entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
ENTRYPOINT ["python", "/usr/src/app/entrypoint.sh"]
