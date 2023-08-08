FROM python:3
WORKDIR /Home
COPY . /Home/
COPY requirements.txt /Home/requirements.txt
RUN pip install -r requirements.txt --default-timeout=100