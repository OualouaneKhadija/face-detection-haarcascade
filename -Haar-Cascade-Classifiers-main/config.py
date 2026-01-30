"""
Configuration module for Face Detection System.

This module contains all configurable parameters for the Haar Cascade face detection.
Adjust these values to optimize detection for your specific use case.
"""

# =============================================================================
# DETECTION PARAMETERS
# =============================================================================

# Scale Factor: Specifies how much the image size is reduced at each image scale.
# - Value > 1.0 (e.g., 1.1 means 10% reduction)
# - Smaller values = more accurate but slower
# - Larger values = faster but may miss faces
SCALE_FACTOR = 1.1

# Min Neighbors: Specifies how many neighbors each candidate rectangle should have.
# - Higher values = fewer detections but higher quality (reduces false positives)
# - Lower values = more detections but more false positives
# - Recommended: 3-6
MIN_NEIGHBORS = 5

# Minimum Size: Minimum possible object size (width, height in pixels).
# Objects smaller than this are ignored.
MIN_SIZE = (30, 30)

# Maximum Size: Maximum possible object size (width, height in pixels).
# Objects larger than this are ignored. None = no limit.
MAX_SIZE = None

# =============================================================================
# VISUALIZATION SETTINGS
# =============================================================================

# Bounding box color (BGR format)
BOX_COLOR = (0, 255, 0)  # Green

# Bounding box thickness
BOX_THICKNESS = 2

# FPS text color (BGR format)
FPS_COLOR = (0, 255, 255)  # Yellow

# FPS text position
FPS_POSITION = (10, 30)

# Font scale for text
FONT_SCALE = 0.7

# =============================================================================
# CASCADE CLASSIFIER PATH
# =============================================================================

# Path to the Haar Cascade XML file
# This file contains the pre-trained classifier for frontal face detection
CASCADE_PATH = "models/haarcascade_frontalface_default.xml"

# Alternative cascades (can be switched for different detection needs):
# - haarcascade_frontalface_alt.xml (alternative frontal face)
# - haarcascade_frontalface_alt2.xml (another alternative)
# - haarcascade_profileface.xml (side profile detection)
# - haarcascade_eye.xml (eye detection)

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================

# Target FPS for display (affects waitKey delay)
TARGET_FPS = 30

# Frame resize factor for faster processing (1.0 = no resize)
# Lower values = faster processing but less accurate
RESIZE_FACTOR = 1.0

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

# Default output directory for saved images/videos
OUTPUT_DIR = "output"

# Default output image format
OUTPUT_IMAGE_FORMAT = ".jpg"

# JPEG quality (0-100)
JPEG_QUALITY = 95
