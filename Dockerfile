FROM python:3.10.5-slim-buster
LABEL maintainer.email="maksim.carkov.201300@gmail.com"
LABEL maintainer.git="s1Sharp"

EXPOSE 8080

RUN apt update && apt upgrade -y

WORKDIR /home

ENV PYTHONPATH="$PYTHONPATH:/home:home/src"

COPY . .

RUN chmod a+x docker/*.sh

RUN pip install -r requirements.txt

ENV PROJECT_ROOT="/home"

# Remove any third-party apt sources to avoid issues with expiring keys.
RUN rm -f /etc/apt/sources.list.d/*.list

# Install some basic utilities.
RUN apt-get update && apt-get install -y \
    curl \
    git \
    bzip2 \
    wget \
    gpg
