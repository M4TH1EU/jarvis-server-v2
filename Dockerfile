FROM python:3.9-alpine

ENV ENV_STATUS=${NODE_ENV:-production}

# needed in older versions of jarvis-server
# RUN apk update && apk upgrade
# RUN apk add --no-cache --upgrade grep

WORKDIR /jarvis

COPY ./jarvis /jarvis

# needed in older versions of jarvis-server
RUN apk add py3-fann2 fann-dev swig

COPY requirements.txt /jarvis/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3", "/jarvis/start.py"]