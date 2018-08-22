FROM python:3.7-alpine3.7
ADD ./post.py /app/
ADD ./requirements.txt /app/
ADD ./secret.py /app
RUN pip install -r requirements.txt
WORKDIR /app
CMD python post.py
