# StockPulse用Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Tensorflow追加
RUN pip install --no-cache-dir tensorflow

COPY . .

CMD ["streamlit", "run", "dashboard/app.py"]
