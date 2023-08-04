FROM python:3
WORKDIR /Home
COPY . /Home/
COPY requirements.txt .
RUN pip install -r requirements --default-timeout=100