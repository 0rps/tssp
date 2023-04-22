FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app
RUN  pip3 install -r requirements.txt

COPY ./ /app

ENTRYPOINT ["python3"]
CMD ["app.py"]
