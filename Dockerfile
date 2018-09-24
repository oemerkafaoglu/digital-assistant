FROM python:3.6
MAINTAINER Ömer Kafaoglu "oemer@kafaoglu.de"
COPY . /digital-assistant
WORKDIR /digital-assistant
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
