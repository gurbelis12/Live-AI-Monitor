"""
================================================================================
PROJECT: Live AI 3D Printer Monitor
FILE: main.py
PURPOSE: Main system orchestrator.
Based on: SECTION 1: CORE SYSTEM ARCHITECTURE
================================================================================

This script initializes all modules, starts the capture and AI threads,
and runs the main logic loop to coordinate detection, correction, and web broadcasting.
"""

import time
import cv2
from queue import Queue, Empty
from threading import Thread

# --- Import project modules ---
from kinect_capture import LiveKinectCapture, ROIMask
from printer_control import LivePrinterControl
from ai_model import LiveAIModel
from correction_engine import LiveCorrectionEngine
from web_dashboard import LiveWebDashboard
from event_logger import LiveEventLogger

# --- Global Queues (from SECTION 1) ---
# frame_queue: Holds raw frames from Kinect for AI processing
frame_queue = Queue(maxsize=10) 
# ai_result_queue: Holds detection results from AI for main loop
ai_result_queue = Queue()
# web_frame_queue: Holds the single latest frame for web dashboard
# Use maxsize=1 to only keep the most recent frame
web_frame_queue = Queue(maxsize=1)

# --- Thread Definitions (from SECTION 1) ---

class LiveCaptureThread(Thread):
    """
    Producer Thread: Captures frames from Kinect at max FPS.
    Puts *all* frames into frame_queue for AI.
    Puts *latest* frame into web_frame_queue for dashboard.
    """
    def __init__(self, kinect, roi_mask):
        super().__init__(daemon=True, name="CaptureThread")
        self.kinect = kinect
        self.roi_mask = roi_mask
        self.running = True
        print("[CAPTURE] Capture thread initialized.")

    def run(self):
        print("[CAPTURE] Capture thread started.")
        while self.running:
            # Get raw frame data
            rgb_frame, _ = self.kinect.get_latest_frame()
            
            if rgb_frame is not None:
                # Convert to OpenCV format
                img = self.kinect.get_live_rgb_image(rgb_frame)
                if img is None:
                    time.sleep(0.001)
                    continue

                # Apply ROI mask
                masked_img = self.roi_mask.apply_live(img)
                
                # --- Queue for AI Thread ---
                try:
                    # Non-blocking put for AI processing
                    frame_queue.put(masked_img, block=False)
                except:
                    # AI queue is full, drop frame (normal behavior)
                    pass 
                
                # --- Queue for Web Thread ---
                try:
                    # Clear queue
                    while not web_frame_queue.empty():
                        web_frame_queue.get_nowait()
                    # Put latest frame
                    web_frame_queue.put(img, block=False) 
                except:
                    # Web queue is full (unlikely with maxsize=1)
                    pass
            
            # Sleep tiny amount to yield processor
            time.sleep(0.001) 
        print("[CAPTURE] Capture thread stopped.")

    def stop(self):
        self.running = False

class LiveAIThread(Thread):
    """
    Consumer Thread: Processes frames from frame_queue.
    Analyzes frames at a set interval (e.g., 5 FPS).
    Puts detection results (if any) into ai_result_queue.
    """
    def __init__(self, model):
        super().__init__(daemon=True, name="AIThread")
        self.model = model
        self.running = True
        print("[AI] AI thread initialized.")

    def run(self):
        print("[AI] AI thread started.")
        while self.running:
            try:
                # Wait for a frame from the capture thread
                frame = frame_queue.get(timeout=1.0)
                
                # Analyze frame (model handles its own frame skipping)
                # Based on: LiveAIModel.analyze_live
                result = self.model.analyze_live(frame)
                
                if result:
                    # Put defect result into the queue for main loop
                    ai_result_queue.put(result)
                    
            except Empty:
                # Queue was empty, just loop again
                pass
            except Exception as e:
                print(f"[AI] Error in AI thread: {e}")
                time.sleep(0.5)
        print("[AI] AI thread stopped.")

    def stop(self):
        self.running = False

# --- Main Application ---
def main():
    print("[SYSTEM] Starting Live AI 3D Printer Monitor...")

    # 1. Initialize Modules
    try:
        # Log to 'print_monitor.log'
        logger = LiveEventLogger("print_monitor.log") 
        kinect = LiveKinectCapture()
        roi = ROIMask()
        # --- IMPORTANT ---
        # --- ADJUST YOUR PRINTER'S PORT HERE ---
        printer = LivePrinterControl(port='COM3', baud=115200) 
        # --- ADJUST YOUR MODEL PATH HERE ---
        ai_model = LiveAIModel(model_path='best.pt') # Use your trained 'best.pt' or 'yolov8n.pt'
        
        corrector = LiveCorrectionEngine(printer, logger)
        web_dashboard = LiveWebDashboard() # This will pass printer/ai objects
    
    except ImportError as e:
        print(f"[FATAL] Failed to import module. Is pykinect2 installed? Error: {e}")
        print("See README.md for installation instructions.")
        return
    except Exception as e:
        print(f"[FATAL] Failed to initialize modules: {e}")
        return

    # 2. Start Worker Threads
    capture_thread = LiveCaptureThread(kinect, roi)
    ai_thread = LiveAIThread(ai_model)
    
    capture_thread.start()
    ai_thread.start()

    # 3. Main Logic Loop (consumes AI results)
    print("[SYSTEM] Main loop running. Press Ctrl+C to stop.")
    current_layer = 0 # TODO: This should be updated, e.g., from G-code parser
    
    try:
        while True:
            # --- A. Check for AI Detections ---
            try:
                defect = ai_result_queue.get(timeout=0.01) # Non-blocking
                
                # We found a defect!
                print(f"[MAIN] Defect detected: {defect['type']} ({defect['confidence']:.2f})")
                logger.log_defect(defect)
                
                # Apply correction
                corrector.apply_live_correction(defect)
                
            except Empty:
                # No defect found, continue
                pass

            # --- B. Broadcast Web Dashboard Frame ---
            try:
                # Get the latest frame for the web dashboard
                web_frame = web_frame_queue.get_nowait()
                
                # Get live printer status
                temps = printer.get_live_temp()
                if temps is None:
                    temps = {'hotend': 0, 'bed': 0, 'hotend_target': 0, 'bed_target': 0}
                
                # Prepare metadata
                metadata = {
                    'layer': current_layer,
                    'temp': temps,
                    'defect': None # TODO: Add last defect info
                }
                
                # Broadcast
                web_dashboard.broadcast_live_frame(web_frame, metadata)
                
            except Empty:
                # No new web frame, skip
                pass
            except Exception as e:
                print(f"[MAIN] Error in web broadcast loop: {e}")

            # Small sleep to prevent 100% CPU on main thread
            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\n[SYSTEM] Shutdown signal received...")
        logger.log_system("Shutdown signal received.")
    except Exception as e:
        print(f"\n[SYSTEM] FATAL ERROR in main loop: {e}")
        logger.log_system(f"FATAL ERROR: {e}")
    finally:
        # 7. Cleanup
        print("[SYSTEM] Stopping threads...")
        capture_thread.stop()
        ai_thread.stop()
        
        capture_thread.join(timeout=2.0)
        ai_thread.join(timeout=2.0)
        
        printer.close()
        kinect.close()
        
        print("[SYSTEM] Shutdown complete.")
        logger.log_system("Shutdown complete.")

if __name__ == "__main__":
    main()