import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, List, Optional, Dict, Any
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DanceMovementAnalyzer:
    def __init__(self):
        """Initialize MediaPipe Pose model for dance movement analysis."""
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[List]]:
        """
        Process a single frame to detect pose landmarks and draw skeleton.
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            
            # Process with MediaPipe Pose
            results = self.pose.process(rgb_frame)
            
            # Convert back to BGR for OpenCV
            rgb_frame.flags.writeable = True
            processed_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            
            # Draw pose landmarks if detected
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    processed_frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
            
            return processed_frame, results.pose_landmarks
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame, None
    
    def process_video(self, input_path: str, output_path: str) -> Tuple[str, dict]:
        """
        Process a video file to analyze dance movements.
        FIXED VERSION with proper video writing
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        cap = None
        out = None
        
        try:
            # Open video
            cap = cv2.VideoCapture(input_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Video properties: {width}x{height} at {fps}fps")
            
            # Initialize video writer - FIXED CODEC ISSUE
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use mp4v codec
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                raise ValueError(f"Cannot create output video: {output_path}")
            
            frame_count = 0
            analysis_data = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame, landmarks = self.process_frame(frame)
                
                # Analyze movement if landmarks detected
                if landmarks:
                    analysis = self.analyze_movement(landmarks)
                    analysis['frame'] = frame_count
                    analysis_data.append(analysis)
                    
                    # Display analysis on frame
                    self._display_analysis(processed_frame, analysis)
                
                # Write processed frame
                out.write(processed_frame)
                frame_count += 1
                
                # Log progress every 50 frames
                if frame_count % 50 == 0:
                    logger.info(f"Processed {frame_count} frames...")
            
            logger.info(f"Video processing complete. Total frames: {frame_count}")
            
            # Create analysis summary
            summary = self._create_analysis_summary(analysis_data)
            
            return output_path, summary
            
        except Exception as e:
            logger.error(f"Error in video processing: {e}")
            raise e
            
        finally:
            # Release resources properly
            if cap:
                cap.release()
            if out:
                out.release()
            logger.info("Video resources released")
    
    def analyze_movement(self, landmarks) -> dict:
        """
        Analyze dance movements from pose landmarks.
        """
        if not landmarks:
            return {}
        
        # Extract key points for analysis
        keypoints = {}
        for idx, landmark in enumerate(landmarks.landmark):
            keypoints[idx] = {
                'x': landmark.x,
                'y': landmark.y, 
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        
        # Calculate basic movement metrics
        analysis = {
            'body_parts_detected': len(keypoints),
            'left_arm_angle': self._calculate_arm_angle(keypoints, 'left'),
            'right_arm_angle': self._calculate_arm_angle(keypoints, 'right'),
            'left_leg_angle': self._calculate_leg_angle(keypoints, 'left'),
            'right_leg_angle': self._calculate_leg_angle(keypoints, 'right'),
            'posture_stability': self._calculate_posture_stability(keypoints)
        }
        
        return analysis
    
    def _calculate_arm_angle(self, keypoints: dict, side: str) -> float:
        """Calculate arm bend angle."""
        try:
            if side == 'left':
                shoulder = keypoints[11]  # Left shoulder
                elbow = keypoints[13]     # Left elbow
                wrist = keypoints[15]     # Left wrist
            else:
                shoulder = keypoints[12]  # Right shoulder
                elbow = keypoints[14]     # Right elbow
                wrist = keypoints[16]     # Right wrist
            
            return self._calculate_angle(shoulder, elbow, wrist)
        except:
            return 0.0
    
    def _calculate_leg_angle(self, keypoints: dict, side: str) -> float:
        """Calculate leg bend angle."""
        try:
            if side == 'left':
                hip = keypoints[23]       # Left hip
                knee = keypoints[25]      # Left knee
                ankle = keypoints[27]     # Left ankle
            else:
                hip = keypoints[24]       # Right hip
                knee = keypoints[26]      # Right knee
                ankle = keypoints[28]     # Right ankle
            
            return self._calculate_angle(hip, knee, ankle)
        except:
            return 0.0
    
    def _calculate_angle(self, point1: dict, point2: dict, point3: dict) -> float:
        """Calculate angle between three points."""
        try:
            # Convert to vectors
            v1 = np.array([point1['x'] - point2['x'], point1['y'] - point2['y']])
            v2 = np.array([point3['x'] - point2['x'], point3['y'] - point2['y']])
            
            # Calculate angle
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.degrees(np.arccos(cos_angle))
            
            return angle
        except:
            return 0.0
    
    def _calculate_posture_stability(self, keypoints: dict) -> float:
        """Calculate posture stability based on shoulder and hip alignment."""
        try:
            left_shoulder = keypoints[11]
            right_shoulder = keypoints[12]
            left_hip = keypoints[23]
            right_hip = keypoints[24]
            
            shoulder_center = {
                'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
                'y': (left_shoulder['y'] + right_shoulder['y']) / 2
            }
            hip_center = {
                'x': (left_hip['x'] + right_hip['x']) / 2,
                'y': (left_hip['y'] + right_hip['y']) / 2
            }
            
            # Calculate vertical alignment
            alignment = abs(shoulder_center['x'] - hip_center['x'])
            stability = max(0, 1 - alignment * 10)
            
            return stability
        except:
            return 0.0
    
    def _display_analysis(self, frame: np.ndarray, analysis: dict):
        """Display analysis data on the video frame."""
        try:
            y_offset = 30
            line_height = 25
            
            metrics = [
                f"Frame: {analysis.get('frame', 0)}",
                f"Left Arm: {analysis.get('left_arm_angle', 0):.1f}°",
                f"Right Arm: {analysis.get('right_arm_angle', 0):.1f}°", 
                f"Left Leg: {analysis.get('left_leg_angle', 0):.1f}°",
                f"Right Leg: {analysis.get('right_leg_angle', 0):.1f}°",
                f"Stability: {analysis.get('posture_stability', 0):.2f}"
            ]
            
            for i, text in enumerate(metrics):
                y_pos = y_offset + (i * line_height)
                cv2.putText(
                    frame, text, (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
                )
        except Exception as e:
            logger.error(f"Error displaying analysis: {e}")
    
    def _create_analysis_summary(self, analysis_data: list) -> dict:
        """Create a summary of the dance analysis."""
        if not analysis_data:
            return {"error": "No movement data detected"}
        
        try:
            # Calculate averages
            summary = {
                "total_frames": len(analysis_data),
                "average_left_arm_angle": np.mean([d.get('left_arm_angle', 0) for d in analysis_data]),
                "average_right_arm_angle": np.mean([d.get('right_arm_angle', 0) for d in analysis_data]),
                "average_left_leg_angle": np.mean([d.get('left_leg_angle', 0) for d in analysis_data]),
                "average_right_leg_angle": np.mean([d.get('right_leg_angle', 0) for d in analysis_data]),
                "average_stability": np.mean([d.get('posture_stability', 0) for d in analysis_data]),
                "frames_with_detection": len(analysis_data)
            }
            
            return summary
        except Exception as e:
            logger.error(f"Error creating analysis summary: {e}")
            return {"error": "Analysis summary creation failed"}
    
    def release(self):
        """Release MediaPipe resources."""
        if self.pose:
            self.pose.close()