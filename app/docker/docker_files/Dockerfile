FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get -y install netcat &&  apt-get -y install gettext

RUN mkdir /code
COPY . /code/
WORKDIR /code

RUN set -e; \
    /usr/local/bin/python -m pip install --upgrade pip ;\
    python -m pip install --default-timeout=100 -r /code/requirements.txt ;\
    chmod +x /code/docker/entrypoints/entrypoint.sh ;

RUN chmod +x /code/docker/entrypoints/entrypoint.sh
RUN touch /code/logs/celery.log
RUN chmod +x /code/logs/celery.log
ENTRYPOINT ["/code/docker/entrypoints/entrypoint.sh"]
