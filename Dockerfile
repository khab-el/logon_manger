FROM ubuntu

USER root

RUN apt-get update -y && \
    apt-get install -y \
    python3-pip \
    gcc \
    build-essential libssl-dev libffi-dev python3-dev \
    libsasl2-dev python-dev libldap2-dev libssl-dev

RUN pip3 install \
    flask \
    gunicorn \
    ldap3 \
    flask-simpleldap \
    requests

ADD ./app /app

WORKDIR /app

ENTRYPOINT [ "/app/entrypoint.sh" ]