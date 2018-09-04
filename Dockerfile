FROM python:3.7-alpine3.7
RUN mkdir /app
ADD ./post.py /app/
ADD ./requirements.txt /app/
ADD ./secret.py /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python post.py
