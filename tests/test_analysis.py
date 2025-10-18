import unittest
import numpy as np
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from movement_analysis import DanceMovementAnalyzer

class TestDanceMovementAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.analyzer = DanceMovementAnalyzer()
    
    def test_angle_calculation(self):
        """Test angle calculation between three points."""
        # Test case: 90 degree angle
        point1 = {'x': 0, 'y': 0}
        point2 = {'x': 0, 'y': 1} 
        point3 = {'x': 1, 'y': 1}
        
        angle = self.analyzer._calculate_angle(point1, point2, point3)
        self.assertAlmostEqual(angle, 90.0, places=1)
    
    def test_arm_angle_calculation(self):
        """Test arm angle calculation with mock keypoints."""
        # Mock keypoints for left arm
        keypoints = {
            11: {'x': 0.5, 'y': 0.5},  # Left shoulder
            13: {'x': 0.5, 'y': 0.6},  # Left elbow
            15: {'x': 0.6, 'y': 0.6}   # Left wrist
        }
        
        angle = self.analyzer._calculate_arm_angle(keypoints, 'left')
        self.assertIsInstance(angle, float)
        self.assertGreaterEqual(angle, 0)
        self.assertLessEqual(angle, 180)
    
    def test_posture_stability(self):
        """Test posture stability calculation."""
        # Mock aligned posture
        keypoints = {
            11: {'x': 0.4, 'y': 0.5},  # Left shoulder
            12: {'x': 0.6, 'y': 0.5},  # Right shoulder  
            23: {'x': 0.4, 'y': 0.7},  # Left hip
            24: {'x': 0.6, 'y': 0.7}   # Right hip
        }
        
        stability = self.analyzer._calculate_posture_stability(keypoints)
        self.assertGreaterEqual(stability, 0)
        self.assertLessEqual(stability, 1)
    
    def test_empty_landmarks_analysis(self):
        """Test analysis with empty landmarks."""
        analysis = self.analyzer.analyze_movement(None)
        self.assertEqual(analysis, {})
    
    def tearDown(self):
        """Clean up after each test method."""
        self.analyzer.release()

if __name__ == '__main__':
    unittest.main()