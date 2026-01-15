FROM python:3.12-slim
ENV TZ=Europe/Amsterdam
ENV APP_TIMEZONE=Europe/Amsterdam
WORKDIR /app
COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y tzdata \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
