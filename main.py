from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from ultralytics import YOLO
from gtts import gTTS
from io import BytesIO
import tempfile
from PIL import Image
import uvicorn
import numpy as np
import cv2
import easyocr
import re
import base64
from io import BytesIO

app = FastAPI()

# =========================
# LOAD MODEL & OCR
# =========================

model = YOLO("best_license_plate_model_updated.pt")
reader = easyocr.Reader(['en'])

# =========================
# HTML + CSS + JS
# =========================

html = """
<!DOCTYPE html>
<html>
<head>

    <title>License Plate Detection</title>

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>

        *{
            margin:0;
            padding:0;
            box-sizing:border-box;
            font-family:Arial,sans-serif;
        }

        body{
            background:#eef2f7;
            height:100vh;
            overflow:hidden;
        }

        .main-container{
            display:flex;
            height:100vh;
            width:100%;
        }

        /* SIDEBAR */

        .sidebar{
            width:260px;
            background:#f4f6f9;
            border-right:1px solid #ddd;
            padding:30px 20px;
        }

        .nav-card{
            background:linear-gradient(to bottom,#3b82f6,#ef4444);
            border-radius:12px;
            padding:30px 20px;
            color:white;
            text-align:center;
            font-size:28px;
            font-weight:bold;
            margin-bottom:40px;
            box-shadow:0 5px 20px rgba(0,0,0,0.1);
        }

        .sidebar h3{
            color:#444;
            margin-bottom:20px;
            font-size:18px;
        }

        .nav-item{
            margin:15px 0;
            color:#555;
            cursor:pointer;
            font-size:16px;
        }

        .nav-item:hover{
            color:#2563eb;
        }

        /* CONTENT */

        .content{
            flex:1;
            padding:50px;
            overflow:auto;
        }

        .title{
            text-align:center;
            font-size:48px;
            font-weight:bold;
            color:#1d4ed8;
            margin-bottom:20px;
        }

        .subtitle{
            text-align:center;
            color:#555;
            font-size:18px;
            margin-bottom:40px;
        }

        .upload-section{
            background:white;
            border-radius:20px;
            padding:40px;
            max-width:900px;
            margin:auto;
            box-shadow:0 5px 25px rgba(0,0,0,0.08);
        }

        .upload-text{
            text-align:center;
            color:#2563eb;
            font-weight:bold;
            margin-bottom:30px;
        }

        .upload-grid{
            display:flex;
            gap:30px;
            align-items:flex-start;
            justify-content:center;
            flex-wrap:wrap;
        }

        .upload-box{
            border:2px dashed #cbd5e1;
            border-radius:15px;
            padding:40px;
            width:320px;
            text-align:center;
            background:#f8fafc;
        }

        .upload-box:hover{
            border-color:#2563eb;
        }

        input[type=file]{
            margin-top:20px;
        }

        .detect-btn{
            background:#1d4ed8;
            color:white;
            border:none;
            padding:14px 28px;
            border-radius:10px;
            font-size:16px;
            cursor:pointer;
            margin-top:25px;
            transition:0.3s;
        }

        .detect-btn:hover{
            background:#2563eb;
            transform:scale(1.03);
        }

        .loader{
            display:none;
            margin-top:20px;
            color:#2563eb;
            font-weight:bold;
        }

        .result-panel{
            width:400px;
        }

        .plate{
            margin-top:15px;
            font-size:20px;
            font-weight:bold;
            color:#111827;
        }

        .status{
            margin-top:15px;
            font-size:22px;
            font-weight:bold;
        }

        .valid{
            color:#16a34a;
        }

        .fraud{
            color:#dc2626;
        }

        .result-image{
            width:100%;
            margin-top:25px;
            border-radius:15px;
            border:1px solid #ddd;
            box-shadow:0 5px 20px rgba(0,0,0,0.08);
        }

        audio{
            margin-top:20px;
            width:100%;
        }

        @media(max-width:900px){

            .main-container{
                flex-direction:column;
            }

            .sidebar{
                width:100%;
                height:auto;
            }

            .content{
                padding:20px;
            }

            .title{
                font-size:34px;
            }

        }

    </style>

</head>

<body>

<div class="main-container">

    <!-- SIDEBAR -->

    <div class="sidebar">

        <div class="nav-card">
            Navigation
        </div>

        <h3>📌 Select Option</h3>

        <div class="nav-item">🏠 Home</div>
        <div class="nav-item">📤 Upload Image</div>
        <div class="nav-item">ℹ️ About</div>

    </div>

    <!-- CONTENT -->

    <div class="content">

        <div class="title">
            🚗 Upload an Image for License Plate Detection
        </div>

        <div class="subtitle">
            Upload an image of a vehicle to automatically detect and validate the license plate.
        </div>

        <div class="upload-section">

            <div class="upload-text">
                📂 Drag and drop an image or click to upload.
            </div>

            <div class="upload-grid">

                <!-- LEFT -->

                <div class="upload-box">

                    <h3>Upload Vehicle Image</h3>

                    <input type="file" id="fileInput">

                    <br>

                    <button class="detect-btn" onclick="uploadImage()">
                        🔍 Start Detection
                    </button>

                    <div class="loader" id="loader">
                        Processing Image...
                    </div>

                </div>

                <!-- RIGHT -->

                <div class="result-panel" id="result">

                </div>

            </div>

        </div>

    </div>

</div>

<script>

async function uploadImage(){

    const fileInput = document.getElementById("fileInput");

    if(fileInput.files.length === 0){
        alert("Please upload an image");
        return;
    }

    document.getElementById("loader").style.display = "block";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("/predict",{
        method:"POST",
        body:formData
    });

    const data = await response.json();

    document.getElementById("loader").style.display = "none";

    document.getElementById("result").innerHTML = `

        <div class="plate">
            🔑 Detected Plate: ${data.plate}
        </div>

        <div class="status ${data.status_class}">
            ${data.status}
        </div>

        <audio controls autoplay>
            <source src="data:audio/mp3;base64,${data.audio}" type="audio/mp3">
        </audio>

        <img class="result-image"
        src="data:image/jpeg;base64,${data.image}">
    `;
}

</script>

</body>
</html>
"""

# =========================
# HOME ROUTE
# =========================

@app.get("/", response_class=HTMLResponse)
async def home():
    return html

# =========================
# PREDICTION ROUTE
# =========================

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    contents = await file.read()

    image = Image.open(BytesIO(contents))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    results = model.predict(image, device='cpu')

    detected_plate = "No Plate Found"
    validation_text = "FRAUDULENT PLATE"
    status_class = "fraud"

    plate_pattern = r'^(MH|HR|DL)[A-Z0-9]{1,2}[A-Z]{1,2}[0-9]{1,4}[A-Z0-9]{0,4}$'

    audio_text = "No plate detected"

    for result in results:

        for box in result.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            confidence = box.conf[0] * 100

            roi = image[y1:y2, x1:x2]

            ocr_result = reader.readtext(roi)

            text = ""

            if ocr_result:
                text = ocr_result[0][-2].strip().upper()

            detected_plate = text

            if re.match(plate_pattern, text):

                validation_text = "✅ VALID PLATE"
                status_class = "valid"
                color = (0,255,0)

                audio_text = f"Detected plate is {text}. This is a valid plate."

            else:

                validation_text = "❌ FRAUDULENT PLATE"
                status_class = "fraud"
                color = (0,0,255)

                audio_text = f"Detected plate is {text}. This is a fraudulent plate."

            cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),2)

            cv2.putText(
                image,
                f"{confidence:.2f}%",
                (x1,y1-30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,0,0),
                2
            )

            cv2.putText(
                image,
                text,
                (x1,y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,255,0),
                2
            )

            cv2.putText(
                image,
                validation_text,
                (x1,y2+30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

    # Convert image to base64
    _, buffer = cv2.imencode(".jpg", image)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    # Generate Audio
    tts = gTTS(audio_text)

    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)

    audio_base64 = base64.b64encode(audio_fp.read()).decode("utf-8")

    return {
        "plate": detected_plate,
        "status": validation_text,
        "status_class": status_class,
        "image": image_base64,
        "audio": audio_base64
    }
    
# =========================
# MAIN
# =========================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)