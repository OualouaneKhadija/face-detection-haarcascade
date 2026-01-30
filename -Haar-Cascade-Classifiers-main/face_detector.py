#!/usr/bin/env python3
"""
Face Detection System using Haar Cascade.

This application detects human faces in real-time using OpenCV's
Haar Cascade classifier (Viola-Jones algorithm).

Features:
    - Webcam real-time detection
    - Image file processing
    - Video file processing
    - Configurable detection parameters
    - FPS monitoring
    - Output saving

Usage:
    # Webcam detection
    python face_detector.py --source webcam
    
    # Image detection
    python face_detector.py --source image --path ./image.jpg
    
    # Video detection
    python face_detector.py --source video --path ./video.mp4

Author: Face Detection System
License: MIT
"""

import argparse
import cv2
import os
import sys
import time
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from utils.detector import FaceDetector


class FaceDetectionApp:
    """
    Main application class for face detection.
    
    Handles different input sources (webcam, image, video) and
    provides a unified interface for face detection.
    """
    
    def __init__(
        self,
        scale_factor: float = None,
        min_neighbors: int = None,
        min_size: tuple = None
    ):
        """
        Initialize the application.
        
        Args:
            scale_factor: Detection scale factor
            min_neighbors: Minimum neighbors for validation
            min_size: Minimum face size
        """
        self.detector = FaceDetector(
            scale_factor=scale_factor,
            min_neighbors=min_neighbors,
            min_size=min_size
        )
        
        # FPS calculation
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.current_fps = 0
        
    def _update_fps(self) -> float:
        """
        Calculate and update FPS.
        
        Returns:
            Current FPS value
        """
        self.fps_frame_count += 1
        elapsed = time.time() - self.fps_start_time
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_frame_count / elapsed
            self.fps_frame_count = 0
            self.fps_start_time = time.time()
            
        return self.current_fps
    
    def run_webcam(self, camera_id: int = 0, save_output: bool = False) -> None:
        """
        Run face detection on webcam feed.
        
        Args:
            camera_id: Camera device ID (default: 0)
            save_output: Whether to save output video
        """
        print("\n" + "="*60)
        print("  FACE DETECTION - WEBCAM MODE")
        print("="*60)
        print(f"  Camera ID: {camera_id}")
        print(f"  Scale Factor: {self.detector.scale_factor}")
        print(f"  Min Neighbors: {self.detector.min_neighbors}")
        print("  Press 'q' to quit, 's' to save screenshot")
        print("="*60 + "\n")
        
        # Open webcam
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print("[ERROR] Failed to open webcam. Please check camera connection.")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Video writer for saving
        out = None
        if save_output:
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
            output_path = os.path.join(config.OUTPUT_DIR, f"webcam_output_{int(time.time())}.avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
            print(f"[INFO] Recording to: {output_path}")
        
        screenshot_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("[ERROR] Failed to capture frame")
                    break
                
                # Detect faces and draw boxes
                processed_frame, faces = self.detector.process_frame(frame)
                
                # Update and display FPS
                fps = self._update_fps()
                processed_frame = self.detector.draw_info(processed_frame, len(faces), fps)
                
                # Display frame
                cv2.imshow("Face Detection - Webcam (Press 'q' to quit)", processed_frame)
                
                # Save frame if recording
                if out is not None:
                    out.write(processed_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n[INFO] Quitting...")
                    break
                elif key == ord('s'):
                    # Save screenshot
                    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
                    screenshot_path = os.path.join(
                        config.OUTPUT_DIR, 
                        f"screenshot_{screenshot_count}.jpg"
                    )
                    cv2.imwrite(screenshot_path, processed_frame)
                    print(f"[INFO] Screenshot saved: {screenshot_path}")
                    screenshot_count += 1
                    
        finally:
            cap.release()
            if out is not None:
                out.release()
            cv2.destroyAllWindows()
            print("[INFO] Webcam released")
    
    def run_image(self, image_path: str, save_output: bool = False) -> None:
        """
        Run face detection on an image file.
        
        Args:
            image_path: Path to the image file
            save_output: Whether to save output image
        """
        print("\n" + "="*60)
        print("  FACE DETECTION - IMAGE MODE")
        print("="*60)
        print(f"  Image: {image_path}")
        print(f"  Scale Factor: {self.detector.scale_factor}")
        print(f"  Min Neighbors: {self.detector.min_neighbors}")
        print("  Press any key to close")
        print("="*60 + "\n")
        
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"[ERROR] Image file not found: {image_path}")
            return
        
        # Read image
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"[ERROR] Failed to read image: {image_path}")
            return
        
        print(f"[INFO] Image size: {image.shape[1]}x{image.shape[0]}")
        
        # Detect faces
        start_time = time.time()
        processed_image, faces = self.detector.process_frame(image)
        detection_time = time.time() - start_time
        
        # Print results
        print(f"\n[RESULTS]")
        print(f"  Faces detected: {len(faces)}")
        print(f"  Detection time: {detection_time*1000:.2f} ms")
        
        if faces:
            print(f"\n  Face coordinates (x, y, width, height):")
            for i, (x, y, w, h) in enumerate(faces):
                print(f"    Face {i+1}: ({x}, {y}, {w}, {h})")
        
        # Add detection info to image
        info_text = f"Detected: {len(faces)} face(s) | Time: {detection_time*1000:.1f}ms"
        cv2.putText(
            processed_image, info_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2
        )
        
        # Save output if requested
        if save_output:
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(config.OUTPUT_DIR, f"{name}_detected{ext}")
            cv2.imwrite(output_path, processed_image)
            print(f"\n[INFO] Output saved: {output_path}")
        
        # Display image
        cv2.imshow("Face Detection - Image (Press any key to close)", processed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def run_video(self, video_path: str, save_output: bool = False) -> None:
        """
        Run face detection on a video file.
        
        Args:
            video_path: Path to the video file
            save_output: Whether to save output video
        """
        print("\n" + "="*60)
        print("  FACE DETECTION - VIDEO MODE")
        print("="*60)
        print(f"  Video: {video_path}")
        print(f"  Scale Factor: {self.detector.scale_factor}")
        print(f"  Min Neighbors: {self.detector.min_neighbors}")
        print("  Press 'q' to quit, 'p' to pause")
        print("="*60 + "\n")
        
        # Check if file exists
        if not os.path.exists(video_path):
            print(f"[ERROR] Video file not found: {video_path}")
            return
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"[ERROR] Failed to open video: {video_path}")
            return
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"[INFO] Video properties:")
        print(f"  Resolution: {width}x{height}")
        print(f"  FPS: {fps:.2f}")
        print(f"  Total frames: {total_frames}")
        
        # Video writer for saving
        out = None
        if save_output:
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
            filename = os.path.basename(video_path)
            name, _ = os.path.splitext(filename)
            output_path = os.path.join(config.OUTPUT_DIR, f"{name}_detected.avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            print(f"[INFO] Saving output to: {output_path}")
        
        # Calculate delay for real-time playback
        delay = int(1000 / fps) if fps > 0 else 33
        
        frame_count = 0
        paused = False
        total_faces_detected = 0
        
        try:
            while True:
                if not paused:
                    ret, frame = cap.read()
                    
                    if not ret:
                        print("\n[INFO] Video ended")
                        break
                    
                    frame_count += 1
                    
                    # Detect faces
                    processed_frame, faces = self.detector.process_frame(frame)
                    total_faces_detected += len(faces)
                    
                    # Update FPS
                    current_fps = self._update_fps()
                    
                    # Draw info overlay
                    processed_frame = self.detector.draw_info(
                        processed_frame, len(faces), current_fps
                    )
                    
                    # Draw progress bar
                    progress = frame_count / total_frames if total_frames > 0 else 0
                    bar_width = int(width * 0.8)
                    bar_start = int(width * 0.1)
                    cv2.rectangle(
                        processed_frame,
                        (bar_start, height - 20),
                        (bar_start + bar_width, height - 10),
                        (100, 100, 100), -1
                    )
                    cv2.rectangle(
                        processed_frame,
                        (bar_start, height - 20),
                        (bar_start + int(bar_width * progress), height - 10),
                        (0, 255, 0), -1
                    )
                    
                    # Display frame
                    cv2.imshow("Face Detection - Video (Press 'q' to quit)", processed_frame)
                    
                    # Save frame if recording
                    if out is not None:
                        out.write(processed_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(delay) & 0xFF
                
                if key == ord('q'):
                    print("\n[INFO] Quitting...")
                    break
                elif key == ord('p'):
                    paused = not paused
                    print(f"[INFO] {'Paused' if paused else 'Resumed'}")
                    
        finally:
            cap.release()
            if out is not None:
                out.release()
            cv2.destroyAllWindows()
            
            # Print statistics
            print(f"\n[STATISTICS]")
            print(f"  Frames processed: {frame_count}")
            print(f"  Total detections: {total_faces_detected}")
            if frame_count > 0:
                print(f"  Avg detections/frame: {total_faces_detected/frame_count:.2f}")


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description="Face Detection System using Haar Cascade",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Webcam detection
  python face_detector.py --source webcam
  
  # Image detection
  python face_detector.py --source image --path ./photo.jpg
  
  # Video detection with output saving
  python face_detector.py --source video --path ./video.mp4 --save
  
  # Adjust detection parameters
  python face_detector.py --source webcam --scale-factor 1.2 --min-neighbors 6
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--source", "-s",
        type=str,
        required=True,
        choices=["webcam", "image", "video"],
        help="Input source type"
    )
    
    # Optional arguments
    parser.add_argument(
        "--path", "-p",
        type=str,
        help="Path to image or video file (required for image/video source)"
    )
    
    parser.add_argument(
        "--camera", "-c",
        type=int,
        default=0,
        help="Camera device ID (default: 0)"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to file"
    )
    
    # Detection parameters
    parser.add_argument(
        "--scale-factor", "-sf",
        type=float,
        default=config.SCALE_FACTOR,
        help=f"Scale factor for detection (default: {config.SCALE_FACTOR})"
    )
    
    parser.add_argument(
        "--min-neighbors", "-mn",
        type=int,
        default=config.MIN_NEIGHBORS,
        help=f"Minimum neighbors for detection (default: {config.MIN_NEIGHBORS})"
    )
    
    parser.add_argument(
        "--min-size",
        type=int,
        nargs=2,
        default=list(config.MIN_SIZE),
        metavar=("WIDTH", "HEIGHT"),
        help=f"Minimum face size (default: {config.MIN_SIZE})"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.source in ["image", "video"] and not args.path:
        parser.error(f"--path is required for {args.source} source")
    
    # Print banner
    print("\n" + "="*60)
    print("       FACE DETECTION SYSTEM - HAAR CASCADE")
    print("       Using Viola-Jones Algorithm (OpenCV)")
    print("="*60)
    
    # Create application
    app = FaceDetectionApp(
        scale_factor=args.scale_factor,
        min_neighbors=args.min_neighbors,
        min_size=tuple(args.min_size)
    )
    
    # Run appropriate mode
    if args.source == "webcam":
        app.run_webcam(camera_id=args.camera, save_output=args.save)
    elif args.source == "image":
        app.run_image(image_path=args.path, save_output=args.save)
    elif args.source == "video":
        app.run_video(video_path=args.path, save_output=args.save)
    
    print("\n[INFO] Face Detection System terminated")


if __name__ == "__main__":
    main()
