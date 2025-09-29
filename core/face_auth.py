import face_recognition
import cv2
import numpy as np
import os
from PIL import Image
from typing import Optional, Tuple, List

class FaceAuthenticator:
    def __init__(self, known_faces_dir: str = "known_faces"):
        """
        Initialize face authenticator with directory containing known face images.
        
        Args:
            known_faces_dir (str): Directory containing images of authorized users
        """
        self.known_faces_dir = known_faces_dir
        self.known_face_encodings = []
        self.known_face_names = []
        self._load_known_faces()
    
    def _load_known_faces(self) -> None:
        """Load and encode all known faces from the known_faces directory."""
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
            print(f"Created {self.known_faces_dir} directory. Please add authorized user images.")
            return

        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(self.known_faces_dir, filename)
                pil_image = Image.open(image_path).convert('RGB')
                image = np.array(pil_image)
                print(f"Loaded image {filename}: shape={image.shape}, dtype={image.dtype}")
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    self.known_face_encodings.append(face_encodings[0])
                    # Use filename without extension as person name
                    self.known_face_names.append(os.path.splitext(filename)[0])
    
    def authenticate(self, frame_or_path) -> Tuple[bool, Optional[str]]:
        """
        Authenticate a person from given frame or image path.
        
        Args:
            frame_or_path: numpy array (frame) or string (path to image)
            
        Returns:
            Tuple[bool, Optional[str]]: (is_authorized, person_name if authorized else None)
        """
        if isinstance(frame_or_path, str):
            frame = face_recognition.load_image_file(frame_or_path)
        else:
            frame = frame_or_path
            
        # Find all faces in the frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        # Check each face found
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            
            if True in matches:
                first_match_index = matches.index(True)
                return True, self.known_face_names[first_match_index]
        
        return False, None
    
    def verify_face_realtime(self, timeout: int = 30) -> Tuple[bool, Optional[str]]:
        """
        Verify face in real-time using webcam.
        
        Args:
            timeout (int): Timeout in seconds
            
        Returns:
            Tuple[bool, Optional[str]]: (is_authorized, person_name if authorized else None)
        """
        cap = cv2.VideoCapture(0)
        start_time = cv2.getTickCount()
        
        try:
            while True:
                # Check timeout
                elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                if elapsed_time > timeout:
                    print("Authentication timeout")
                    return False, None
                
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Convert BGR to RGB
                rgb_frame = frame[:, :, ::-1]
                
                # Try to authenticate
                is_authorized, name = self.authenticate(rgb_frame)
                if is_authorized:
                    return True, name
                
                # Display the frame
                cv2.imshow('Face Authentication', frame)
                
                # Break loop on 'q' press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
        return False, None

    def add_new_user(self, name: str, image_path: str) -> bool:
        """
        Add a new authorized user.
        
        Args:
            name (str): Name of the person
            image_path (str): Path to person's face image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(image_path):
                print(f"Image not found: {image_path}")
                return False
                
            pil_image = Image.open(image_path).convert('RGB')
            image = np.array(pil_image)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                print("No face found in the image")
                return False
            
            # Save the image to known_faces directory
            ext = os.path.splitext(image_path)[1]
            new_path = os.path.join(self.known_faces_dir, f"{name}{ext}")
            os.makedirs(self.known_faces_dir, exist_ok=True)
            
            with open(image_path, 'rb') as src, open(new_path, 'wb') as dst:
                dst.write(src.read())
            
            # Update encodings
            self.known_face_encodings.append(face_encodings[0])
            self.known_face_names.append(name)
            
            return True
            
        except Exception as e:
            print(f"Error adding new user: {str(e)}")
            return False