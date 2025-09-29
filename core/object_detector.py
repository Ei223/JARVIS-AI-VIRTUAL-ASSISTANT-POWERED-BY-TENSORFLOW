import cv2
from ultralytics import YOLO
import numpy as np
import threading
from queue import Queue
import time
from typing import List, Tuple, Dict, Optional

class ObjectDetector:
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize object detector with YOLOv8
        
        Args:
            confidence_threshold: Minimum confidence score for detections (0-1)
        """
        print("Initializing Object Detection System...")
        self.model = YOLO('yolov8n.pt')  # Load the smallest YOLOv8 model for faster inference
        self.confidence_threshold = confidence_threshold
        self.detection_queue = Queue()
        self.is_running = False
        self.current_frame = None
        self.current_detections = []
        
        # Start detection thread
        self.detection_thread = None
        print("Object Detection System initialized!")
        
    def start(self, camera_id: int = 0):
        """Start object detection on specified camera"""
        self.is_running = True
        self.cap = cv2.VideoCapture(camera_id)
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
    def stop(self):
        """Stop object detection"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join()
        if hasattr(self, 'cap'):
            self.cap.release()
            
    def _detection_loop(self):
        """Main detection loop running in separate thread"""
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Store current frame for visualization
            self.current_frame = frame
            
            # Run detection
            results = self.model(frame, verbose=False)
            
            # Process detections
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    if box.conf.item() > self.confidence_threshold:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf)
                        cls = int(box.cls)
                        name = result.names[cls]
                        
                        detections.append({
                            'bbox': (x1, y1, x2, y2),
                            'confidence': conf,
                            'class': name
                        })
            
            # Update current detections
            self.current_detections = detections
            
            # Add to queue for external access
            if not self.detection_queue.empty():
                try:
                    self.detection_queue.get_nowait()
                except:
                    pass
            self.detection_queue.put((frame, detections))
            
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
            
    def get_latest_detections(self) -> Tuple[Optional[np.ndarray], List[Dict]]:
        """
        Get the latest frame and detections
        
        Returns:
            Tuple containing:
            - Frame (numpy array)
            - List of detections, each with bbox, confidence, and class
        """
        try:
            return self.detection_queue.get_nowait()
        except:
            return None, []
            
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw detection boxes and labels on frame
        
        Args:
            frame: Input frame
            detections: List of detection dictionaries
            
        Returns:
            Frame with detections drawn
        """
        output = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class']} {det['confidence']:.2f}"
            
            # Draw box
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 255), 2)
            
            # Draw label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(output, (x1, y1 - 20), (x1 + w, y1), (0, 255, 255), -1)
            
            # Draw label text
            cv2.putText(output, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            
        return output
        
    def get_detected_objects(self) -> List[str]:
        """
        Get list of currently detected object names
        
        Returns:
            List of object class names
        """
        return [det['class'] for det in self.current_detections]