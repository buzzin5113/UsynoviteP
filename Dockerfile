FROM python:3.7-alpine3.7
RUN mkdir /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python post.py
