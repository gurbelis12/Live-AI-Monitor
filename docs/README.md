# **LIVE AI 3D Printer Monitor**

This project is a real-time AI monitoring system for 3D printers, designed for solo developers. It uses a Kinect V2 for RGB \+ Depth vision to detect print failures (spaghetti, warping, etc.) and automatically send corrective G-code commands to the printer.

This repository contains the complete source code, project plans, and web dashboard for the "24-Weekend Solo Developer Plan."

## **Core Features**

* **Live RGB \+ Depth Feed:** 30 FPS video pipeline using a Kinect V2.  
* **Real-time AI Detection:** Uses YOLOv8 to identify print failures at 5+ FPS.  
* **Live Printer Control:** Sends G-code commands (Pause, Stop, Temp Adjust) via pyserial.  
* **Automated Corrections:** An intelligent engine that applies corrections based on defect type and confidence.  
* **Web Dashboard:** A mobile-friendly Flask \+ SocketIO dashboard to monitor your print from anywhere on your network.  
* **Active Learning:** Includes scripts and structures for capturing and training on your own failure data.

## **Project Structure**

.  
├── docs/  
│   ├── PROJECT\_PLAN\_24\_WEEKEND.md  (The high-level 6-month plan)  
│   └── TECHNICAL\_CODE\_PLAN.md      (The detailed structural code plan)  
├── templates/  
│   └── live.html                   (Flask web dashboard)  
├── .gitignore                      (Keeps the repo clean)  
├── ai\_model.py                     (YOLO model wrapper & training)  
├── correction\_engine.py            (Applies corrective G-code)  
├── event\_logger.py                 (Handles logging)  
├── kinect\_capture.py               (Kinect V2 sensor interface)  
├── main.py                         (Main application orchestrator)  
├── printer\_control.py              (Serial communication with printer)  
├── README.md                       (This file)  
├── requirements.txt                (Python dependencies)  
└── web\_dashboard.py                (Flask \+ SocketIO server)

## **Installation**

1. **Clone the repository:**  
   git clone \[https://your-repo-url.com/live-ai-monitor.git\](https://your-repo-url.com/live-ai-monitor.git)  
   cd live-ai-monitor

2. **Create a Python virtual environment (Recommended):**  
   python \-m venv venv  
   source venv/bin/activate  \# On Windows: venv\\Scripts\\activate

3. **Install Python dependencies:**  
   pip install \-r requirements.txt

4. Install pykinect2 (MANUAL STEP):  
   pykinect2 is not available on PyPI. You must download the wheel (.whl) file that matches your Python version (e.g., cp310 for Python 3.10) and architecture (e.g., amd64).  
   * Find the wheels here: [Kinect/PyKinect2 Releases](https://www.google.com/search?q=https://github.com/Kinect/PyKinect2/releases) (or other community-provided sources).  
   * Install the downloaded wheel:  
     pip install C:\\path\\to\\your\\pykinect2-2.0.xxxx.whl

5. Download a base model:  
   This project uses YOLOv8. Download a base model to get started.  
   \# This will be used by ai\_model.py  
   \# You can also use 'yolov8n.pt'

   Place your trained best.pt or the default yolov8n.pt in the root folder.

## **Usage**

1. **Connect Hardware:**  
   * Ensure your 3D printer is connected via USB.  
   * Ensure your Kinect V2 is connected via its USB 3.0 adapter and powered on.  
2. **Configure the Project:**  
   * Edit printer\_control.py and change port='COM3' to your printer's correct serial port.  
   * Edit kinect\_capture.py and adjust the ROIMask coordinates to fit your printer's bed.  
3. **Run the Monitor:**  
   python main.py

4. Open the Web Dashboard:  
   Open your web browser and go to http://localhost:5000 (or your computer's IP address, e.g., http://192.168.1.10:5000, from your phone).

## **Project Plans**

* [**24-Weekend Project Plan**](https://www.google.com/search?q=./docs/PROJECT_PLAN_24_WEEKEND.md)**:** The original 6-month, week-by-week guide.  
* [**Technical Code Plan**](https://www.google.com/search?q=./docs/TECHNICAL_CODE_PLAN.md)**:** The detailed structural plan for all classes and methods.