# Face Detection System (Haar Cascade)

This project implements a real-time face detection system using the Viola-Jones algorithm (Haar Cascade). It offers both a versatile command-line interface (CLI) and a modern web application for detecting faces via webcam, images, or videos.

## 🚀 Features

- **Real-Time Detection**: Uses the webcam to detect faces instantly.

- **Image Processing**: Downloads and detects faces from image files (JPG, PNG).

- **Video Processing**: Analyzes video files with frame-by-frame face tracking.

- **Web Interface**: An intuitive user interface built with FastAPI.

- **Configurable Parameters**: Easily adjust the scaling factor and minimum neighbors count to optimize detection.

## 🛠️ Technologies Used

This project was developed using the following technologies:

- **Python**: Primary programming language.

- **OpenCV (cv2)**: Powerful library for image processing and computer vision.

- **FastAPI**: Modern and fast web framework for creating the API and web interface.

- **NumPy**: Scientific computing and matrix manipulation for image processing.

- **HAAR Cascade Classifiers**: Pre-trained models for object (face) detection.

- **JavaScript/HTML/CSS**: For the frontend of the web interface.

## 🎓 What I Learned

Through this project, I acquired and strengthened my skills in:

- **Computer Vision**: Understanding the Viola-Jones algorithm and manipulating video and image streams with OpenCV.

- **Backend Development**: Creating RESTful APIs and WebSockets with FastAPI for real-time communication.

- **Integration**: Connecting backend image processing to a frontend user interface.

- **Project Management**: Organizing code into reusable modules (`face_detector.py`, `app.py`).

## 💻 How to Launch the Project

### Prerequisites

Make sure you have Python installed. Next, install the necessary dependencies:

```bash
pip install opencv-python-headless numpy fastapi uvicorn python-multipart
# Note: If you are using the webcam locally, use `opencv-python` instead of `headless`
pip install opencv-python numpy fastapi uvicorn python-multipart
```

### Method 1: Web Interface (Recommended)

1. Start the web server:

```bash
python app.py

```
2. Open your browser to the address provided (usually `http://localhost:8000`).

### Method 2: Command Line (CLI)

You can use the `face_detector.py` script directly:

**For a webcam:**
```bash
python face_detector.py --source webcam
```

**For an image:**
```bash
python face_detector.py --source image --path path/to/image.jpg --save
```

**For a video:**
```bash
python face_detector.py --source video --path path/to/video.mp4 --save
```

**Additional options:**
- `--save`: Saves the result (image or video) to the `output` folder.

- `--scale-factor 1.2`: Adjusts the sensitivity (1.1 by default).

- `--min-neighbors 6`: Adjusts the precision (5 by default).

## 👤 Author

**Khadija Oualouane**
[GitHub Profile](https://github.com/OualouaneKhadija)
