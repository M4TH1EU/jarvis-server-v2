FROM python:3.9-alpine

ENV ENV_STATUS=${NODE_ENV:-production}

RUN apk update && apk upgrade

# needed for whispercpp
RUN apk add --no-cache --upgrade ffmpeg gcc musl-dev linux-headers g++
WORKDIR /jarvis

COPY ./jarvis /jarvis

# needed for padatious and adapt
RUN apk --no-cache add py3-fann2 fann-dev swig

COPY requirements.txt /jarvis/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3", "/jarvis/start.py"]