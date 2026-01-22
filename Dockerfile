FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Pre-download EasyOCR models during build
RUN python -c "import easyocr; easyocr.Reader(['en'])"

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
