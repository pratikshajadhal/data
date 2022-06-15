FROM python:3.9.13-slim

RUN set -ex; \
    apt-get update && apt-get -y install --no-install-recommends \
        ca-certificates \
        curl

# create non-root container user
RUN useradd -ms /bin/bash appuser
USER appuser

# create/cd to app dir
WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip3 --timeout=300  install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]
