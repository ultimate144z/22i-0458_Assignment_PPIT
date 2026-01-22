---
title: Image Text Extractor
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Image Text Extractor

A web application that extracts text from images using OCR and generates PDF documents.

## Features

- Upload images (JPG, PNG, etc.)
- Extract text using EasyOCR (AI-powered)
- Generate PDF with original image and extracted text
- Download the PDF

## Tech Stack

- **Backend:** Flask (Python)
- **OCR Engine:** EasyOCR
- **PDF Generation:** FPDF2
- **Deployment:** Docker on Hugging Face Spaces

## Usage

1. Upload an image containing text
2. Click "Extract Text & Generate PDF"
3. View extracted text
4. Download the generated PDF

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:7860`
