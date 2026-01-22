from flask import Flask, render_template_string, request, send_file
import easyocr
from PIL import Image
from fpdf import FPDF
import tempfile
import os
import numpy as np

app = Flask(__name__)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Image Text Extractor</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">

<style>
    * {
        box-sizing: border-box;
        font-family: 'Inter', sans-serif;
    }

    body {
        margin: 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }

    .card {
        background: #fff;
        width: 100%;
        max-width: 900px;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }

    h1 {
        text-align: center;
        font-weight: 700;
        margin-bottom: 5px;
        color: #222;
    }

    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }

    .upload-box {
        border: 2px dashed #bbb;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        cursor: pointer;
        transition: 0.3s;
        background: #fafafa;
    }

    .upload-box:hover {
        border-color: #667eea;
        background: #f4f6ff;
    }

    input[type="file"] {
        display: none;
    }

    .upload-box p {
        margin: 0;
        font-size: 16px;
        color: #555;
    }

    .preview {
        margin-top: 20px;
        text-align: center;
    }

    .preview img {
        max-width: 100%;
        max-height: 300px;
        border-radius: 10px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }

    .actions {
        text-align: center;
        margin-top: 25px;
    }

    button {
        background: #667eea;
        color: #fff;
        padding: 14px 36px;
        border: none;
        border-radius: 30px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: 0.3s;
    }

    button:hover {
        background: #5a67d8;
    }

    .result {
        margin-top: 40px;
    }

    textarea {
        width: 100%;
        min-height: 220px;
        resize: none;
        padding: 15px;
        font-size: 14px;
        border-radius: 10px;
        border: 1px solid #ddd;
        background: #f9f9f9;
    }

    .download-btn {
        background: #28a745;
        margin-top: 15px;
    }

    .download-btn:hover {
        background: #218838;
    }

    .loader {
        display: none;
        text-align: center;
        margin-top: 20px;
        color: #555;
    }

    @media(max-width: 600px) {
        .card {
            padding: 20px;
        }
    }
</style>
</head>

<body>

<div class="card">
    <h1>🖼️ Image Text Extractor</h1>
    <p class="subtitle">Upload an image, extract text using AI, and download as PDF</p>

    <form method="POST" enctype="multipart/form-data" onsubmit="showLoader()">

        <label class="upload-box">
            <input type="file" name="image" accept="image/*" required onchange="previewImage(event)">
            <p>📤 Click or drag an image here</p>
        </label>

        <div class="preview" id="preview"></div>

        <div class="actions">
            <button type="submit">Extract Text & Generate PDF</button>
        </div>

        <div class="loader" id="loader">
            ⏳ Processing image, please wait...
        </div>
    </form>

    {% if extracted_text %}
    <div class="result">
        <h3>📄 Extracted Text</h3>
        <textarea readonly>{{ extracted_text }}</textarea>
        <a href="/download">
            <button class="download-btn">⬇ Download PDF</button>
        </a>
    </div>
    {% endif %}
</div>

<script>
function previewImage(event) {
    const preview = document.getElementById('preview');
    preview.innerHTML = '';
    const img = document.createElement('img');
    img.src = URL.createObjectURL(event.target.files[0]);
    preview.appendChild(img);
}

function showLoader() {
    document.getElementById('loader').style.display = 'block';
}
</script>

</body>
</html>

'''

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = None

    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                # Open image
                img = Image.open(file)
                img_array = np.array(img)

                # Extract text using EasyOCR
                results = reader.readtext(img_array)
                extracted_text = '\n'.join([text[1] for text in results])

                if not extracted_text.strip():
                    extracted_text = "No text detected"

                # Create PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Extracted Document", ln=True, align="C")
                pdf.ln(10)

                # Save temp image
                temp_img = os.path.join(tempfile.gettempdir(), "temp.jpg")
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(temp_img, "JPEG")

                pdf.image(temp_img, x=10, w=190)
                pdf.ln(85)

                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Extracted Text:", ln=True)
                pdf.set_font("Arial", "", 10)
                clean_text = extracted_text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, clean_text)

                # Save PDF
                pdf_path = os.path.join(tempfile.gettempdir(), "output.pdf")
                pdf.output(pdf_path)
                os.remove(temp_img)

    return render_template_string(HTML, extracted_text=extracted_text)

@app.route('/download')
def download():
    pdf_path = os.path.join(tempfile.gettempdir(), "output.pdf")
    return send_file(pdf_path, as_attachment=True, download_name="extracted_document.pdf")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
