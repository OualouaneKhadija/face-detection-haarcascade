"""
FastAPI Web Application for Face Detection System.

This module provides a modern web interface for the face detection system,
supporting real-time webcam detection, image upload, and video processing.
"""

import os
import sys
import time
import base64
import asyncio
from io import BytesIO
from typing import Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.detector import FaceDetector
import config

# Initialize FastAPI app
app = FastAPI(
    title="Face Detection System",
    description="Real-time face detection using Haar Cascade (Viola-Jones Algorithm)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Global detector instance
detector = FaceDetector()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Face Detection System</h1><p>Static files not found.</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "detector_loaded": detector.cascade is not None}


@app.post("/api/detect/image")
async def detect_image(
    file: UploadFile = File(...),
    scale_factor: float = Form(1.1),
    min_neighbors: int = Form(5)
):
    """
    Process an uploaded image for face detection.
    
    Args:
        file: Uploaded image file
        scale_factor: Detection scale factor
        min_neighbors: Minimum neighbors threshold
    
    Returns:
        JSON with detected faces and processed image
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not decode image"}
            )
        
        # Update detector parameters
        detector.set_detection_params(
            scale_factor=scale_factor,
            min_neighbors=min_neighbors
        )
        
        # Detect faces
        start_time = time.time()
        processed_image, faces = detector.process_frame(image)
        detection_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Convert processed image to base64
        _, buffer = cv2.imencode('.jpg', processed_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "success": True,
            "faces_count": len(faces),
            "faces": [{"x": int(x), "y": int(y), "width": int(w), "height": int(h)} 
                      for x, y, w, h in faces],
            "detection_time_ms": round(detection_time, 2),
            "image_data": f"data:image/jpeg;base64,{img_base64}",
            "original_size": {"width": image.shape[1], "height": image.shape[0]}
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/api/detect/base64")
async def detect_base64(
    image_data: str = Form(...),
    scale_factor: float = Form(1.1),
    min_neighbors: int = Form(5)
):
    """
    Process a base64 encoded image for face detection.
    Used for webcam frame processing.
    """
    try:
        # Decode base64 image
        if "," in image_data:
            image_data = image_data.split(",")[1]
        
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not decode image"}
            )
        
        # Update detector parameters
        detector.set_detection_params(
            scale_factor=scale_factor,
            min_neighbors=min_neighbors
        )
        
        # Detect faces
        start_time = time.time()
        faces = detector.detect_faces(image)
        detection_time = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "faces_count": len(faces),
            "faces": [{"x": int(x), "y": int(y), "width": int(w), "height": int(h)} 
                      for x, y, w, h in faces],
            "detection_time_ms": round(detection_time, 2)
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.websocket("/ws/detect")
async def websocket_detect(websocket: WebSocket):
    """
    WebSocket endpoint for real-time face detection.
    Receives base64 frames and returns detection results.
    """
    await websocket.accept()
    
    # Default parameters
    scale_factor = 1.1
    min_neighbors = 5
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Check for parameter updates
            if "scale_factor" in data:
                scale_factor = float(data["scale_factor"])
            if "min_neighbors" in data:
                min_neighbors = int(data["min_neighbors"])
            
            # Process frame if provided
            if "frame" in data:
                frame_data = data["frame"]
                
                # Decode base64 image
                if "," in frame_data:
                    frame_data = frame_data.split(",")[1]
                
                img_bytes = base64.b64decode(frame_data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is not None:
                    # Update and detect
                    detector.set_detection_params(
                        scale_factor=scale_factor,
                        min_neighbors=min_neighbors
                    )
                    
                    start_time = time.time()
                    faces = detector.detect_faces(image)
                    detection_time = (time.time() - start_time) * 1000
                    
                    # Send results
                    await websocket.send_json({
                        "faces_count": len(faces),
                        "faces": [{"x": int(x), "y": int(y), "width": int(w), "height": int(h)} 
                                  for x, y, w, h in faces],
                        "detection_time_ms": round(detection_time, 2)
                    })
                    
    except WebSocketDisconnect:
        print("[INFO] WebSocket client disconnected")
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")


@app.get("/api/config")
async def get_config():
    """Get current detection configuration."""
    return {
        "scale_factor": config.SCALE_FACTOR,
        "min_neighbors": config.MIN_NEIGHBORS,
        "min_size": config.MIN_SIZE,
        "box_color": config.BOX_COLOR
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  FACE DETECTION WEB INTERFACE")
    print("  Open http://localhost:8000 in your browser")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
