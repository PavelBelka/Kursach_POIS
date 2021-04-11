FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /library
WORKDIR /library
COPY requirements.txt /library/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /library/