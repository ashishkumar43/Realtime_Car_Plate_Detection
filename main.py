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

model = YOLO("best_license_plate_model_updated.pt")
reader = easyocr.Reader(['en'])

html = """
<!DOCTYPE html>
<html>
<head>

    <title>AutoVision AI</title>

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>

        *{
            margin:0;
            padding:0;
            box-sizing:border-box;
            font-family:Arial,sans-serif;
        }

        body{
            background:#f1f5f9;
            overflow-x:hidden;
        }

    
        .navbar{
            width:100%;
            height:85px;
            background:white;
            display:flex;
            justify-content:space-between;
            align-items:center;
            padding:0 60px;
            box-shadow:0 4px 18px rgba(0,0,0,0.06);
            position:sticky;
            top:0;
            z-index:100;
        }

        .logo-section{
            display:flex;
            align-items:center;
            gap:18px;
        }

        .logo{
            width:58px;
            height:58px;
            border-radius:16px;
            background:linear-gradient(to right,#2563eb,#7c3aed);
            display:flex;
            justify-content:center;
            align-items:center;
            color:white;
            font-size:28px;
            font-weight:bold;
            box-shadow:0 6px 18px rgba(37,99,235,0.3);
        }

        .brand-title{
            font-size:28px;
            font-weight:bold;
            color:#111827;
        }

        .brand-subtitle{
            color:#6b7280;
            font-size:14px;
            margin-top:3px;
        }

        .developer{
            font-size:16px;
            color:#374151;
        }

        .developer span{
            color:#2563eb;
            font-weight:bold;
        }

        
        .hero{
            padding:70px 20px 40px;
            text-align:center;
        }

        .hero-title{
            font-size:52px;
            font-weight:bold;
            color:#111827;
            line-height:1.2;
        }

        .gradient-text{
            background:linear-gradient(to right,#2563eb,#7c3aed);
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
        }

        .hero-subtitle{
            margin-top:25px;
            color:#6b7280;
            font-size:20px;
            line-height:1.7;
            max-width:850px;
            margin-left:auto;
            margin-right:auto;
        }

        
        .main-card{
            width:92%;
            max-width:1200px;
            margin:40px auto 70px;
            background:white;
            border-radius:28px;
            padding:45px;
            box-shadow:0 10px 40px rgba(0,0,0,0.08);
        }

        .section-title{
            text-align:center;
            font-size:30px;
            color:#111827;
            font-weight:bold;
            margin-bottom:12px;
        }

        .section-subtitle{
            text-align:center;
            color:#6b7280;
            margin-bottom:45px;
            font-size:17px;
        }

        .content-grid{
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:40px;
        }


        .upload-box{
            border:2px dashed #cbd5e1;
            border-radius:24px;
            padding:45px;
            text-align:center;
            background:#f8fafc;
            transition:0.3s;
        }

        .upload-box:hover{
            border-color:#2563eb;
            background:#eff6ff;
        }

        .upload-icon{
            font-size:70px;
            margin-bottom:20px;
        }

        .upload-heading{
            font-size:26px;
            font-weight:bold;
            color:#111827;
            margin-bottom:12px;
        }

        .upload-desc{
            color:#6b7280;
            margin-bottom:25px;
            line-height:1.6;
        }

        input[type=file]{
            width:100%;
            padding:18px;
            border-radius:14px;
            border:1px solid #d1d5db;
            background:white;
            cursor:pointer;
        }

        .detect-btn{
            margin-top:28px;
            width:100%;
            padding:18px;
            border:none;
            border-radius:14px;
            background:linear-gradient(to right,#2563eb,#7c3aed);
            color:white;
            font-size:18px;
            font-weight:bold;
            cursor:pointer;
            transition:0.3s;
            box-shadow:0 6px 20px rgba(37,99,235,0.25);
        }

        .detect-btn:hover{
            transform:translateY(-3px);
            opacity:0.95;
        }

        .loader{
            margin-top:22px;
            display:none;
            color:#2563eb;
            font-weight:bold;
            font-size:18px;
        }

        
        .result-panel{
            background:#f8fafc;
            border-radius:24px;
            padding:35px;
            border:1px solid #e5e7eb;
            min-height:400px;
        }

        .result-title{
            font-size:26px;
            font-weight:bold;
            color:#111827;
            margin-bottom:25px;
            text-align:center;
        }

        .plate-box{
            background:white;
            border-radius:16px;
            padding:18px;
            margin-top:15px;
            box-shadow:0 4px 10px rgba(0,0,0,0.05);
        }

        .plate{
            font-size:22px;
            font-weight:bold;
            color:#111827;
        }

        .status{
            margin-top:20px;
            font-size:22px;
            font-weight:bold;
        }

        .valid{
            color:#16a34a;
        }

        .fraud{
        color:#f59e0b;
        }

        .result-image{
            width:100%;
            margin-top:30px;
            border-radius:18px;
            border:1px solid #d1d5db;
            box-shadow:0 8px 25px rgba(0,0,0,0.08);
        }

        audio{
            width:100%;
            margin-top:18px;
        }

    
        .footer{
            text-align:center;
            padding:25px;
            color:#6b7280;
            font-size:15px;
        }


        @media(max-width:900px){

            .content-grid{
                grid-template-columns:1fr;
            }

            .hero-title{
                font-size:38px;
            }

            .navbar{
                padding:20px;
                flex-direction:column;
                height:auto;
                gap:15px;
            }

            .brand-title{
                font-size:24px;
            }

        }

    </style>

</head>

<body>

    <div class="navbar">

        <div class="logo-section">

            <div class="logo">
                🚘
            </div>

            <div>

                <div class="brand-title">
                    AutoVision AI
                </div>

                <div class="brand-subtitle">
                    Smart License Plate Detection System
                </div>

            </div>

        </div>

        <div class="developer">
            Developed by <span>Ashish Kumar</span>
        </div>

    </div>

    <!-- HERO -->

    <div class="hero">

        <div class="hero-title">
            AI Powered <span class="gradient-text">License Plate Detection</span>
        </div>

    </div>

    <!-- MAIN CARD -->

    <div class="main-card">

        <div class="section-title">
            🚗 Vehicle Plate Scanner
        </div>

        <div class="section-subtitle">
            Upload your vehicle image below to start AI detection.
        </div>

        <div class="content-grid">

            <!-- LEFT SIDE -->

            <div class="upload-box">

                <div class="upload-icon">
                    📤
                </div>

                <div class="upload-heading">
                    Upload Vehicle Image
                </div>

                <div class="upload-desc">
                    Supported formats: JPG, PNG, JPEG
                </div>

                <input type="file" id="fileInput">

                <button class="detect-btn" onclick="uploadImage()">
                    🔍 Start Detection
                </button>

                <div class="loader" id="loader">
                    Processing Image...
                </div>

            </div>

            <!-- RIGHT SIDE -->

            <div class="result-panel" id="result">

                <div class="result-title">
                    Detection Results
                </div>

                <p style="text-align:center;color:#6b7280;">
                    Your detection output will appear here.
                </p>

            </div>

        </div>

    </div>

    <!-- FOOTER -->

    <div class="footer">
        © 2026 AutoVision AI • Built with FastAPI, YOLO & EasyOCR
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

        <div class="result-title">
            Detection Results
        </div>

        <div class="plate-box">

            <div class="plate">
                🔑 Detected Plate: ${data.plate}
            </div>

            <div class="status ${data.status_class}">
                ${data.status}
            </div>

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

@app.get("/", response_class=HTMLResponse)
async def home():
    return html

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    contents = await file.read()

    image = Image.open(BytesIO(contents))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    results = model.predict(image, device='cpu')

    detected_plate = "No Plate Found"

    validation_text = "⚠ NO PLATE DETECTED"

    status_class = "fraud"

    audio_text = "No plate detected"

    # Indian vehicle number plate regex
    plate_pattern = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$'

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            confidence = float(box.conf[0]) * 100

            # =========================
            # CROP ROI
            # =========================

            roi = image[y1:y2, x1:x2]

            # =========================
            # PREPROCESSING
            # =========================

            # resize image
            roi = cv2.resize(roi, None, fx=3, fy=3)

            # grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # remove noise
            gray = cv2.bilateralFilter(gray, 11, 17, 17)

            # sharpen image
            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ])

            gray = cv2.filter2D(gray, -1, kernel)

            # threshold
            gray = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            # =========================
            # OCR
            # =========================

            ocr_result = reader.readtext(
                gray,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )

            text = ""

            if ocr_result:

                detected_texts = []

                for detection in ocr_result:
                    detected_texts.append(detection[-2])

                # combine all text
                text = "".join(detected_texts)

                # uppercase
                text = text.upper()

                # remove spaces/symbols
                text = re.sub(r'[^A-Z0-9]', '', text)

                print("DETECTED TEXT:", text)

            detected_plate = text

            # =========================
            # VALIDATION
            # =========================

            if len(text) >= 8 and re.match(plate_pattern, text):

                validation_text = "✅ VALID PLATE"

                status_class = "valid"

                color = (0, 255, 0)

                audio_text = (
                    f"Detected plate is {text}. "
                    f"This is a valid vehicle plate."
                )

            else:

                validation_text = "⚠ INVALID / UNRECOGNIZED PLATE"

                status_class = "fraud"

                color = (0, 0, 255)

                audio_text = (
                    f"Detected plate is {text}. "
                    f"The plate format could not be recognized."
                )

            # =========================
            # DRAW RESULTS
            # =========================

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                color,
                2
            )

            cv2.putText(
                image,
                f"{confidence:.2f}%",
                (x1, y1 - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )

            cv2.putText(
                image,
                text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

            cv2.putText(
                image,
                validation_text,
                (x1, y2 + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

            # stop after first plate
            break

    # =========================
    # IMAGE TO BASE64
    # =========================

    _, buffer = cv2.imencode(".jpg", image)

    image_base64 = base64.b64encode(
        buffer
    ).decode("utf-8")

    # =========================
    # AUDIO GENERATION
    # =========================

    tts = gTTS(audio_text)

    audio_fp = BytesIO()

    tts.write_to_fp(audio_fp)

    audio_fp.seek(0)

    audio_base64 = base64.b64encode(
        audio_fp.read()
    ).decode("utf-8")

    return {
        "plate": detected_plate,
        "status": validation_text,
        "status_class": status_class,
        "image": image_base64,
        "audio": audio_base64
    }
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)