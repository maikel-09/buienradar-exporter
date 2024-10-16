FROM python:3-slim

LABEL authors="Maikel Wagteveld"
LABEL version="v1.0.0"

WORKDIR /home/metrics
COPY src/ /home/metrics

RUN python3 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 9002

CMD ["python3", "buienradar-exporter.py"]