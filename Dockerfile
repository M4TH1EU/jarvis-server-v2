FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV ENV_STATUS=${NODE_ENV:-production}

# For suport set local time zone.
RUN apt-get update -y && apt-get upgrade -y

WORKDIR /jarvis

RUN apt install python3.9 python3-pip python3.9-dev python3.9-distutils python3-fann2 libfann-dev swig git python3-levenshtein curl -y

RUN git clone --progress --verbose https://github.com/M4TH1EU/jarvis-server-v2.git .

RUN python3 -m pip install -r requirements.txt

RUN apt-get clean -y

EXPOSE 5000

ENTRYPOINT [ "python3", "/jarvis/start.py"]