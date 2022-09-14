FROM python:3
COPY . /app
RUN pip install opencv-python && pip install paho-mqtt && pip install scipy
WORKDIR /app
CMD python executar.bat