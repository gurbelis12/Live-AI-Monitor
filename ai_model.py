"""
================================================================================
PROJECT: Live AI 3D Printer Monitor
FILE: ai_model.py
PURPOSE: AI model wrapper, training, and data collection.
Based on: SECTION 4: LIVE AI MODEL STRUCTURE
================================================================================
"""

import os
import shutil
import time
import numpy as np
import cv2
import torch
from ultralytics import YOLO

class LiveAIModel:
    """
    Wrapper for YOLOv8 model for live inference.
    Based on: Live AI Model Wrapper
    """
    def __init__(self, model_path='yolov8n.pt'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[AI] Initializing AI model on device: {self.device}")
        
        if not os.path.exists(model_path):
            print(f"[AI] WARNING: Model file not found at '{model_path}'.")
            print("[AI] Defaulting to 'yolov8n.pt'. This will download the model.")
            model_path = 'yolov8n.pt'
            
        try:
            self.model = YOLO(model_path).to(self.device)
            print(f"[AI] Model loaded: {model_path}")
            if hasattr(self.model, 'names'):
                 print(f"[AI] Model classes: {self.model.names}")
        except Exception as e:
            print(f"[AI] FATAL: Failed to load model '{model_path}'.")
            print(f"[AI] Error: {e}")
            raise

        self.frame_count = 0
        self.current_layer = 0 # This should be updated by the main loop
    
    def analyze_live(self, frame):
        """
        Analyze a single frame and return the highest confidence defect.
        Handles its own frame skipping.
        """
        self.frame_count += 1
        
        # Skip frames to achieve target FPS (e.g., 5 FPS from 30 FPS)
        if self.frame_count % 6 != 0:
            return None
        
        # Run YOLO inference
        try:
            results = self.model(frame, conf=0.75, verbose=False)
        except Exception as e:
            print(f"[AI] Error during model inference: {e}")
            return None
            
        highest_conf_defect = None
        
        # Process results
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls)
                confidence = float(box.conf)
                
                # Get adaptive threshold
                threshold = self.get_threshold(self.current_layer)
                
                if confidence > threshold:
                    defect_type = self.map_class_to_defect(class_id)
                    
                    if defect_type != 'unknown':
                        defect = {
                            'type': defect_type,
                            'confidence': confidence,
                            'bbox': box.xyxy[0].cpu().tolist() # [x1, y1, x2, y2]
                        }
                        
                        # Store the highest confidence defect
                        if highest_conf_defect is None or confidence > highest_conf_defect['confidence']:
                            highest_conf_defect = defect
        
        return highest_conf_defect
    
    def map_class_to_defect(self, class_id):
        """Map model classes to defect types"""
        if hasattr(self.model, 'names'):
            # Custom model with trained classes
            return self.model.names[class_id]
        else:
            # Default COCO classes (if using yolov8n.pt)
            # This is a basic proxy for anomaly detection.
            # 0: 'person'
            if class_id == 0: 
                return 'anomaly' 
            return 'unknown'
    
    def get_threshold(self, layer):
        """
        Adaptive confidence threshold.
        Be less sensitive in early layers (adhesion issues).
        """
        self.current_layer = layer
        if layer < 10: return 0.70 # More sensitive
        elif layer < 50: return 0.75
        else: return 0.80 # Less sensitive to small issues
        
    def set_current_layer(self, layer):
        self.current_layer = layer

class AITrainer:
    """
    Handles structuring and running the YOLO training process.
    Based on: Live AI Training Structure
    """
    def __init__(self, dataset_path='dataset/'):
        self.dataset_path = dataset_path
        self.model_output = 'models/'
        os.makedirs(self.model_output, exist_ok=True)
        print(f"[TRAINER] AI Trainer initialized. Dataset path: {dataset_path}")

    def prepare_dataset(self):
        """
        Creates the required directory structure and dataset.yaml file.
        """
        print("[TRAINER] Preparing dataset directories...")
        os.makedirs(f'{self.dataset_path}/images/train', exist_ok=True)
        os.makedirs(f'{self.dataset_path}/images/val', exist_ok=True)
        os.makedirs(f'{self.dataset_path}/labels/train', exist_ok=True)
        os.makedirs(f'{self.dataset_path}/labels/val', exist_ok=True)
        
        yaml_path = f'{self.dataset_path}/dataset.yaml'
        
        # Create dataset.yaml
        with open(yaml_path, 'w') as f:
            f.write(f'''# YOLOv8 Dataset Config
train: {os.path.abspath(self.dataset_path)}/images/train
val: {os.path.abspath(self.dataset_path)}/images/val

# Number of classes
nc: 3

# Class names
names: ['warping', 'stringing', 'spaghetti']
''')
        print(f"[TRAINER] Created {yaml_path}. Ready for data.")
        print("[TRAINER] Add your images and labels (from Roboflow, etc.) to these folders.")

    def train_live_model(self, base_model='yolov8n.pt', epochs=100, batch=8):
        """
        Train a new model on the live-captured dataset.
        Requires `ultralytics` to be installed.
        """
        print("[TRAINER] Starting model training...")
        data_yaml = f'{self.dataset_path}/dataset.yaml'
        if not os.path.exists(data_yaml):
            print(f"[TRAINER] Error: {data_yaml} not found. Run prepare_dataset() first.")
            return

        try:
            model = YOLO(base_model)
            
            results = model.train(
                data=data_yaml,
                epochs=epochs,
                imgsz=1920, # Use full Kinect resolution
                batch=batch,
                device=0 if torch.cuda.is_available() else 'cpu'
            )
            
            print(f"[TRAINER] Training complete. Results: {results}")
            
            # Find the best model weights
            best_model_path = os.path.join(results.save_dir, 'weights/best.pt')
            
            if os.path.exists(best_model_path):
                # Copy to a predictable location
                final_model_name = f"best_model_{int(time.time())}.pt"
                final_path = os.path.join(self.model_output, final_model_name)
                shutil.copy(best_model_path, final_path)
                print(f"[TRAINER] Best model saved to: {final_path}")
                print(f"[TRAINER] Copy this path to main.py to use the new model.")
            else:
                print(f"[TRAINER] Could not find 'best.pt' in {results.save_dir}")

        except Exception as e:
            print(f"[TRAINER] An error occurred during training: {e}")
            print("[TRAINER] Ensure 'ultralytics' is installed and CUDA is set up.")


class LiveDataCollector:
    """
    Captures and saves training data during live prints.
    Based on: Live Data Collection Pattern
    """
    def __init__(self, output_dir='live_raw_data/'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[COLLECTOR] Data collector initialized. Saving to: {output_dir}")

    def capture_training_sample(self, rgb_frame, depth_frame, defect_type, layer):
        """
        Capture one labeled sample (RGB + Depth) during a print.
        """
        timestamp = int(time.time())
        
        try:
            # Save with label
            rgb_filename = f'{self.output_dir}/{defect_type}_rgb_{layer}_{timestamp}.jpg'
            depth_filename = f'{self.output_dir}/{defect_type}_depth_{layer}_{timestamp}.npy'
            
            cv2.imwrite(rgb_filename, rgb_frame)
            if depth_frame is not None:
                np.save(depth_filename, depth_frame)
            
            print(f"[COLLECTOR] Captured {defect_type} sample at layer {layer} (Timestamp: {timestamp})")
        
        except Exception as e:
            print(f"[COLLECTOR] Error saving sample: {e}")