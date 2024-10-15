FROM python:3

LABEL authors="maikel-09"
LABEL version="1.0"

WORKDIR /home/metrics
COPY src/ /home/metrics

RUN python3 -m pip install -r requirements.txt

EXPOSE 9002

CMD ["python3", "buienradar-exporter.py"]