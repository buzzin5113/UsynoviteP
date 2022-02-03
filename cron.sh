#/bin/bash
cd /opt/UsynoviteP
docker build -t usynovitep .
docker run --rm -v /opt/UsynoviteP:/app usynovitep:latest