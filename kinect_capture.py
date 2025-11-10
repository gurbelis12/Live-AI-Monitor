"""
================================================================================
PROJECT: Live AI 3D Printer Monitor
FILE: kinect_capture.py
PURPOSE: Live Kinect V2 frame capture.
Based on: SECTION 2: LIVE KINECT CAPTURE STRUCTURE
================================================================================
"""

import numpy as np
import cv2

try:
    from pykinect2 import PyKinectV2
    from pykinect2.PyKinectRuntime import PyKinectRuntime
except ImportError:
    print("="*50)
    print("FATAL ERROR: pykinect2 library not found.")
    print("Please ensure it is installed correctly for your Python version.")
    print("This is a common issue and may require specific wheel files.")
    print("See README.md for installation instructions.")
    print("="*50)
    raise

class LiveKinectCapture:
    """
    Handles initialization and frame grabbing from the Kinect V2 sensor.
    Based on: Live Kinect Initialization Pattern
    """
    def __init__(self):
        print("[KINECT] Initializing Kinect V2 Runtime...")
        try:
            self.kinect = PyKinectRuntime(
                PyKinectV2.FrameSourceTypes_Color | 
                PyKinectV2.FrameSourceTypes_Depth
            )
            print("[KINECT] Kinect runtime started.")
        except Exception as e:
            print(f"[KINECT] FATAL: Failed to initialize Kinect runtime: {e}")
            print("Is the Kinect V2 plugged in (USB 3.0) and powered (Adapter)?")
            raise
            
        self.latest_rgb_frame = None
        self.latest_depth_frame = None

    def get_latest_frame(self):
        """
        Non-blocking frame retrieval. Stores raw frame data.
        """
        if self.kinect.has_new_color_frame():
            self.latest_rgb_frame = self.kinect.get_last_color_frame()
        
        if self.kinect.has_new_depth_frame():
            self.latest_depth_frame = self.kinect.get_last_depth_frame()
        
        return self.latest_rgb_frame, self.latest_depth_frame

    def get_live_rgb_image(self, rgb_frame_data):
        """
        Convert live raw color frame to OpenCV format (BGR).
        """
        if rgb_frame_data is None:
            return None
        
        # Reshape the raw data (1080, 1920, 4 channels BGRA)
        rgb_img = rgb_frame_data.reshape((
            self.kinect.color_frame_desc.Height, 
            self.kinect.color_frame_desc.Width, 
            4
        ))
        
        # Convert BGRA to BGR
        return cv2.cvtColor(rgb_img, cv2.COLOR_BGRA2BGR)

    def get_live_depth_image(self, depth_frame_data):
        """
        Convert live raw depth frame to a normalized 8-bit image for visualization
        or a float image in meters.
        """
        if depth_frame_data is None:
            return None
        
        # Reshape raw data
        depth_img_raw = depth_frame_data.reshape((
            self.kinect.depth_frame_desc.Height,
            self.kinect.depth_frame_desc.Width
        ))
        
        # Convert to float (meters)
        # Note: Raw depth is in mm (uint16).
        depth_img_meters = depth_img_raw.astype(np.float32) * 0.001
        
        return depth_img_meters
        
    def close(self):
        """Safely close the Kinect runtime."""
        if hasattr(self, 'kinect'):
            self.kinect.close()
            print("[KINECT] Kinect runtime closed.")


class ROIMask:
    """
    Generates and applies a Region of Interest mask to focus AI.
    Based on: Live ROI Mask Generation
    """
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.mask = np.zeros((self.height, self.width), dtype=np.uint8)
        
        # --- IMPORTANT ---
        # Define your print area coordinates here (top_left, bottom_right)
        # These values are for a 1920x1080 frame.
        # You MUST adjust these for your printer setup!
        top_left_x = 400
        top_left_y = 300
        bottom_right_x = 1520
        bottom_right_y = 900
        
        print(f"[ROI] Creating mask from ({top_left_x},{top_left_y}) to ({bottom_right_x},{bottom_right_y})")
        
        # Create a white rectangle (255) on the black mask (0)
        cv2.rectangle(
            self.mask, 
            (top_left_x, top_left_y), 
            (bottom_right_x, bottom_right_y), 
            255,  # Color (white)
            -1    # Thickness (-1 for filled)
        )
    
    def apply_live(self, frame):
        """
        Apply the pre-calculated mask to a live frame.
        """
        # Ensure frame dimensions match mask
        if frame.shape[0] != self.height or frame.shape[1] != self.width:
            # Resize frame to match mask if necessary (e.g., test image)
            frame = cv2.resize(frame, (self.width, self.height))
        
        # Use bitwise_and to zero out everything outside the mask
        return cv2.bitwise_and(frame, frame, mask=self.mask)