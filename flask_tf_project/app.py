import os
import numpy as np
import cv2
import base64
from flask import Flask, request
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Flatten, Dropout

app = Flask(__name__)

MODEL_PATH = "mnist_model.h5"
model = None

# --- 1. THE BRAIN BUILDER ---
def load_or_train_model():
    global model
    if os.path.exists(MODEL_PATH):
        print("🧠 Found existing brain! Loading it...")
        model = load_model(MODEL_PATH)
    else:
        print("⚠️ No brain found. Training a new one... (Wait 1 min)")
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train = x_train / 255.0
        model = Sequential([
            Flatten(input_shape=(28, 28)),
            Dense(128, activation='relu'),
            Dropout(0.2),
            Dense(10, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(x_train, y_train, epochs=3)
        model.save(MODEL_PATH)

# --- 2. THE WEBSITE (Frontend - Ultimate Edition) ---
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
<title>NEON SLATE: Ultimate</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300&display=swap" rel="stylesheet">
<style>
    body {
        background-color: #0d0d12;
        color: #00ffcc;
        font-family: 'Roboto', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
    }
    
    h1 { font-family: 'Orbitron', sans-serif; font-size: 3rem; margin-bottom: 10px; text-shadow: 0 0 10px #00ffcc; letter-spacing: 2px; }

    .container {
        background: rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.1);
        border: 1px solid rgba(0, 255, 204, 0.2);
        text-align: center;
        width: 350px;
    }

    canvas {
        border: 2px solid #333;
        background-color: black;
        border-radius: 10px;
        box-shadow: 0 0 15px #000;
        cursor: crosshair;
        margin-bottom: 20px;
    }

    button {
        padding: 12px 25px;
        font-size: 14px;
        font-family: 'Orbitron', sans-serif;
        cursor: pointer;
        border: none;
        border-radius: 50px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        font-weight: bold;
        margin: 5px;
    }

    .btn-clear { background: transparent; border: 2px solid #ff4444; color: #ff4444; }
    .btn-clear:hover { background: #ff4444; color: white; box-shadow: 0 0 15px #ff4444; }

    .btn-predict { background: #00ffcc; color: black; box-shadow: 0 0 15px rgba(0, 255, 204, 0.5); }
    .btn-predict:hover { transform: scale(1.05); box-shadow: 0 0 25px rgba(0, 255, 204, 0.8); }

    /* CONFIDENCE BAR STYLES */
    #result-area { margin-top: 25px; min-height: 80px; }
    #prediction-text { font-size: 24px; font-family: 'Orbitron', sans-serif; color: white; margin-bottom: 10px; }
    .highlight { color: #00ffcc; font-size: 40px; font-weight: bold; }

    .bar-container {
        width: 100%;
        background-color: #333;
        height: 10px;
        border-radius: 5px;
        overflow: hidden;
        margin-top: 5px;
        display: none; /* Hidden until we predict */
    }
    
    .bar-fill {
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #ff4444, #ffff00, #00ffcc);
        transition: width 1s ease-out;
        box-shadow: 0 0 10px #00ffcc;
    }
    
    #confidence-text { font-size: 12px; color: #888; margin-top: 5px; }

</style>
</head>
<body>

    <div class="container">
        <h1>NEON SLATE</h1>
        <p style="color: #888; margin-bottom: 20px;">ULTIMATE EDITION</p>
        
        <canvas id="canvas" width="280" height="280"></canvas>
        
        <div>
            <button class="btn-clear" onclick="clearCanvas()">Erase</button>
            <button class="btn-predict" onclick="predict()">Analyze</button>
        </div>

        <div id="result-area">
            <div id="prediction-text">Waiting for input...</div>
            
            <div class="bar-container" id="bar-box">
                <div class="bar-fill" id="bar"></div>
            </div>
            <div id="confidence-text"></div>
        </div>
    </div>

    <script>
        var canvas = document.getElementById('canvas');
        var ctx = canvas.getContext('2d');
        var isDrawing = false;
        
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 20; 
        ctx.lineCap = 'round';
        ctx.shadowBlur = 10;
        ctx.shadowColor = 'white';

        canvas.onmousedown = function(e) { isDrawing = true; ctx.beginPath(); ctx.moveTo(e.offsetX, e.offsetY); };
        canvas.onmousemove = function(e) { if(isDrawing) { ctx.lineTo(e.offsetX, e.offsetY); ctx.stroke(); } };
        canvas.onmouseup = function() { isDrawing = false; };

        function clearCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            document.getElementById('prediction-text').innerText = "Waiting for input...";
            document.getElementById('bar-box').style.display = "none";
            document.getElementById('confidence-text').innerText = "";
        }

        function predict() {
            var dataURL = canvas.toDataURL();
            document.getElementById('prediction-text').innerHTML = "Scanning... <span style='color:#00ffcc'>⚡</span>";
            
            fetch('/predict', { method: 'POST', body: dataURL })
            .then(response => response.text())
            .then(text => { 
                // We receive "7,99.5" (Digit, Confidence)
                var parts = text.split(',');
                var digit = parts[0];
                var confidence = parseFloat(parts[1]);

                // Update Text
                document.getElementById('prediction-text').innerHTML = "DETECTED: <span class='highlight'>" + digit + "</span>";
                
                // Update Bar
                document.getElementById('bar-box').style.display = "block";
                setTimeout(() => { document.getElementById('bar').style.width = confidence + "%"; }, 100);
                
                document.getElementById('confidence-text').innerText = "Confidence: " + confidence + "%";
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_CODE

@app.route('/predict', methods=['POST'])
def predict():
    try:
        img_data = request.data.decode('utf-8').split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        # Preprocessing
        img_resized = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)
        img_final = img_resized.reshape(1, 28, 28) / 255.0
        
        if model is None: load_or_train_model()
        
        # --- NEW LOGIC: Get Number AND Confidence ---
        prediction = model.predict(img_final)
        
        digit = np.argmax(prediction)          # The Best Guess (e.g., 7)
        confidence = np.max(prediction) * 100  # The Probability (e.g., 99.4)
        
        print(f"✅ Guess: {digit} | Confidence: {confidence:.2f}%", flush=True)
        
        # Return both as a comma-separated string
        return f"{digit},{confidence:.1f}"

    except Exception as e:
        print("Error:", e)
        return "Error"

if __name__ == '__main__':
    load_or_train_model()
    print("🚀 NEON SERVER STARTING at http://127.0.0.1:5000")
    app.run(port=5000, debug=True)