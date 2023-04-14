FROM python:3.10

RUN apt update -y && apt upgrade -y
RUN apt install -y apt-transport-https

# Add RU locale
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -yq --no-install-recommends
RUN apt install -y locales locales-all
ENV LANGUAGE ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
RUN locale-gen ru_RU.UTF-8 && dpkg-reconfigure locales

COPY ./src /src
COPY ./requirements.txt /tmp/requirements.txt

WORKDIR /src

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

CMD python3 run.py
