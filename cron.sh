#/bin/bash
cd /opt/UsynoviteP
docker build -t usynovitep .
docker run -v /opt/UsynoviteP:/app usynovitep:latest