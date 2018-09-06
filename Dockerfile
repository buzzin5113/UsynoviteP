FROM python:3.7-alpine3.7
RUN mkdir /app
WORKDIR /app
RUN pip install -r /app/requirements.txt
CMD python post.py
