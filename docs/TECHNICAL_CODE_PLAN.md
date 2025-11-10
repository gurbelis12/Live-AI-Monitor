\<\!--  
This file contains the complete structural code plan.  
Content from the user's second prompt.  
\--\>

# **LIVE\_AI\_3D\_PRINTER\_MONITOR\_STRUCTURAL\_CODE\_PLAN.txt**

# **\================================================================================ PROJECT: Live AI 3D Printer Monitor \- Structural Code Implementation PURPOSE: Complete structural code patterns for 24-weekend solo developer project FORMAT: Copy-paste ready for AI code generation**

# **\================================================================================ SECTION 1: CORE SYSTEM ARCHITECTURE**

# **Main System Orchestrator Pattern**

class LiveSystem:  
def init(self):  
self.kinect \= LiveKinectCapture()  
self.printer \= LivePrinterControl()  
self.ai \= LiveAIModel()  
self.guard \= LiveLayerGuard()  
self.logger \= LiveEventLogger()  
self.web \= LiveWebDashboard()  
self.corrector \= LiveCorrectionEngine()  
def run\_live\_loop(self):  
    """Main live loop \- never blocks"""  
    while self.printing:  
        \# Get latest frame (non-blocking)  
        frame \= self.kinect.get\_latest\_frame()  
        if frame is None:  
            time.sleep(0.001)  
            continue  
          
        \# AI decision (every 6th frame \= 5 FPS)  
        if self.frame\_count % 6 \== 0:  
            defect \= self.ai.analyze\_live(frame)  
              
            \# Apply correction if detected  
            if defect:  
                self.corrector.apply(defect)  
                self.logger.log\_live(defect, frame)  
                self.web.broadcast\_live(defect)  
          
        self.frame\_count \+= 1

# **Live Threading Pattern \- Producer/Consumer**

from threading import Thread, Queue  
import time  
frame\_queue \= Queue(maxsize=10)  
ai\_result\_queue \= Queue()  
class LiveCaptureThread(Thread):  
def init(self, kinect):  
super().init(daemon=True)  
self.kinect \= kinect  
self.running \= True  
def run(self):  
    """Producer: Capture frames at 30 FPS"""  
    while self.running:  
        if self.kinect.has\_new\_color\_frame():  
            frame \= self.kinect.get\_last\_color\_frame()  
            try:  
                frame\_queue.put(frame, block=False)  
            except:  
                pass  \# Queue full, drop frame  
        time.sleep(0.001)

class LiveAIThread(Thread):  
def init(self, model):  
super().init(daemon=True)  
self.model \= model  
self.running \= True  
def run(self):  
    """Consumer: Process frames at 5 FPS"""  
    while self.running:  
        try:  
            frame \= frame\_queue.get(timeout=0.1)  
            \# Process every 6th frame  
            if self.model.frame\_count % 6 \== 0:  
                result \= self.model.analyze(frame)  
                ai\_result\_queue.put(result)  
        except:  
            pass

# **Usage in main**

capture\_thread \= LiveCaptureThread(kinect)  
ai\_thread \= LiveAIThread(ai\_model)  
capture\_thread.start()  
ai\_thread.start()

# **Main loop consumes results**

# **while printing: if not ai\_result\_queue.empty(): defect \= ai\_result\_queue.get() if defect: printer.emergency\_stop()**

# **\================================================================================ SECTION 2: LIVE KINECT CAPTURE STRUCTURE**

# **Live Kinect Initialization Pattern**

from pykinect2 import PyKinectV2  
from pykinect2.PyKinectRuntime import PyKinectRuntime  
class LiveKinectCapture:  
def init(self):  
self.kinect \= PyKinectRuntime(  
PyKinectV2.FrameSourceTypes\_Color |  
PyKinectV2.FrameSourceTypes\_Depth  
)  
self.latest\_rgb \= None  
self.latest\_depth \= None  
def get\_latest\_frame(self):  
    """Non-blocking frame retrieval"""  
    if self.kinect.has\_new\_color\_frame():  
        self.latest\_rgb \= self.kinect.get\_last\_color\_frame()  
      
    if self.kinect.has\_new\_depth\_frame():  
        self.latest\_depth \= self.kinect.get\_last\_depth\_frame()  
      
    return self.latest\_rgb, self.latest\_depth

def get\_live\_rgb\_image(self):  
    """Convert live frame to OpenCV format"""  
    if self.latest\_rgb is None:  
        return None  
      
    rgb\_img \= self.latest\_rgb.reshape((1080, 1920, 4))  
    return cv2.cvtColor(rgb\_img, cv2.COLOR\_RGBA2BGR)

def get\_live\_depth\_image(self):  
    """Convert live depth to meters"""  
    if self.latest\_depth is None:  
        return None  
      
    depth\_img \= self.latest\_depth.reshape((424, 512))  
    return depth\_img \* 0.001  \# mm to meters

# **Live ROI Mask Generation**

class ROIMask:  
def init(self):  
self.mask \= np.zeros((1080, 1920), dtype=np.uint8)  
\# Define print area (adjust for your printer)  
cv2.rectangle(self.mask, (400, 300), (1520, 900), 255, \-1)  
def apply\_live(self, frame):  
    """Apply mask to live frame"""  
    return cv2.bitwise\_and(frame, frame, mask=self.mask)

# **Usage**

roi \= ROIMask()  
kinect \= LiveKinectCapture()

# **while True: rgb\_frame, depth\_frame \= kinect.get\_latest\_frame() if rgb\_frame is not None: img \= kinect.get\_live\_rgb\_image() masked \= roi.apply\_live(img) \# Use masked for AI detection**

# **\================================================================================ SECTION 3: LIVE PRINTER CONTROL STRUCTURE**

# **Live Printer Serial Pattern**

import serial  
import time  
class LivePrinterControl:  
def init(self, port='COM3', baud=115200):  
self.port \= port  
self.baud \= baud  
self.ser \= None  
self.connect\_live()  
def connect\_live(self):  
    """Auto-connect with retry"""  
    while True:  
        try:  
            self.ser \= serial.Serial(self.port, self.baud, timeout=2)  
            time.sleep(2)  \# Bootloader delay  
            print(f"\[LIVE\] Printer connected on {self.port}")  
            return  
        except serial.SerialException as e:  
            print(f"\[LIVE\] Connection failed: {e}, retrying in 5s...")  
            time.sleep(5)

def send\_live(self, gcode):  
    """Send with error recovery"""  
    try:  
        self.ser.write(gcode.encode() \+ b'\\n')  
        response \= self.ser.readline().decode().strip()  
        print(f"\[LIVE SEND\] {gcode} → {response}")  
        return response  
    except serial.SerialException:  
        print("\[LIVE\] Connection lost, reconnecting...")  
        self.connect\_live()  
        return None

def get\_live\_temp(self):  
    """Get current temperature"""  
    resp \= self.send\_live('M105')  
    \# Parse: "ok T:205.1 /210.0 B:60.2 /70.0"  
    if resp and 'T:' in resp and 'B:' in resp:  
        temps \= resp.split()  
        hotend \= float(temps\[1\].split(':')\[1\])  
        bed \= float(temps\[3\].split(':')\[1\])  
        return {'hotend': hotend, 'bed': bed}  
    return None

def emergency\_stop\_live(self):  
    """Immediate stop \- bypasses everything"""  
    self.send\_live('M112')

def set\_temp\_live(self, hotend=None, bed=None):  
    """Dynamic temperature adjustment"""  
    if hotend is not None:  
        self.send\_live(f'M104 S{hotend}')  
    if bed is not None:  
        self.send\_live(f'M140 S{bed}')

def adjust\_speed\_live(self, percentage):  
    """Live speed override"""  
    self.send\_live(f'M220 S{percentage}')

def pause\_live(self, reason="AI\_PAUSED"):  
    """Pause and show message on LCD"""  
    self.send\_live('M25')  \# Pause SD print  
    self.send\_live(f'M117 {reason}...')

def resume\_live(self):  
    """Resume from pause"""  
    self.send\_live('M24')  
    self.send\_live('M117 AI\_RESUMED')

# **Critical Live Command Reference**

# **COMMANDS \= { 'emergency\_stop': 'M112', 'get\_temp': 'M105', 'set\_hotend\_temp': 'M104 S{}', 'set\_bed\_temp': 'M140 S{}', 'adjust\_speed': 'M220 S{}', 'adjust\_flow': 'M221 S{}', 'set\_fan': 'M106 S{}', 'pause\_print': 'M25', 'resume\_print': 'M24', 'home\_all': 'G28', 'move\_to': 'G1 X{} Y{} Z{} F{}' }**

# **\================================================================================ SECTION 4: LIVE AI MODEL STRUCTURE**

# **Live AI Model Wrapper**

from ultralytics import YOLO  
import torch  
class LiveAIModel:  
def init(self, model\_path='yolov8n.pt'):  
self.device \= 'cuda' if torch.cuda.is\_available() else 'cpu'  
self.model \= YOLO(model\_path).to(self.device)  
self.frame\_count \= 0  
def analyze\_live(self, frame):  
    """Analyze frame and return defect if detected"""  
    self.frame\_count \+= 1  
      
    \# Skip frames to achieve 5 FPS  
    if self.frame\_count % 6 \!= 0:  
        return None  
      
    results \= self.model(frame, conf=0.75, verbose=False)  
      
    for r in results\[0\].boxes:  
        class\_id \= int(r.cls)  
        confidence \= float(r.conf)  
          
        \# Map to defect types  
        defect\_type \= self.map\_class\_to\_defect(class\_id)  
          
        if confidence \> self.get\_threshold(current\_layer):  
            return {  
                'type': defect\_type,  
                'confidence': confidence,  
                'bbox': r.xyxy\[0\].tolist()  
            }  
      
    return None

def map\_class\_to\_defect(self, class\_id):  
    """Map model classes to defect types"""  
    if hasattr(self.model, 'names'):  
        \# Custom model with trained classes  
        return self.model.names\[class\_id\]  
    else:  
        \# Default COCO classes (blob detection)  
        if class\_id \== 0:  
            return 'anomaly'  \# Proxy for any failure

def get\_threshold(self, layer):  
    """Adaptive confidence threshold"""  
    if layer \< 10: return 0.70  
    elif layer \< 50: return 0.75  
    else: return 0.80

# **Live AI Training Structure**

class AITrainer:  
def init(self):  
self.dataset\_path \= 'dataset/'  
self.model\_output \= 'models/'  
def prepare\_dataset(self):  
    """Structure: dataset/images/, dataset/labels/, dataset.yaml"""  
    os.makedirs(f'{self.dataset\_path}/images/train', exist\_ok=True)  
    os.makedirs(f'{self.dataset\_path}/images/val', exist\_ok=True)  
    os.makedirs(f'{self.dataset\_path}/labels/train', exist\_ok=True)  
    os.makedirs(f'{self.dataset\_path}/labels/val', exist\_ok=True)  
      
    \# Create dataset.yaml  
    with open(f'{self.dataset\_path}/dataset.yaml', 'w') as f:  
        f.write(f'''train: ./images/train

val: ./images/val  
nc: 3  
names: \['warping', 'stringing', 'spaghetti'\]  
''')  
def train\_live\_model(self):  
    """Train on live-captured dataset"""  
    command \= f"yolo task=detect mode=train model=yolov8n.pt data=dataset/dataset.yaml epochs=100 imgsz=1920 batch=8 device=cuda"  
    os.system(command)  
      
    \# Result: models/best.pt (copy to project root)  
    shutil.copy('runs/detect/train/weights/best.pt', 'best.pt')

# **Live Data Collection Pattern**

class LiveDataCollector:  
def init(self):  
self.output\_dir \= 'live\_raw\_data/'  
os.makedirs(self.output\_dir, exist\_ok=True)  
def capture\_training\_sample(self, defect\_type, layer):  
    """Capture one labeled sample during print"""  
    timestamp \= int(time.time())  
      
    \# Capture both RGB and Depth  
    rgb \= kinect.get\_color\_frame()  
    depth \= kinect.get\_depth\_frame()  
      
    \# Save with label  
    cv2.imwrite(f'{self.output\_dir}/{defect\_type}\_rgb\_{layer}\_{timestamp}.jpg', rgb)  
    np.save(f'{self.output\_dir}/{defect\_type}\_depth\_{layer}\_{timestamp}.npy', depth)  
      
    \# Manual annotation (later in Roboflow)  
    print(f"Captured {defect\_type} sample at layer {layer}")

\================================================================================

# **\================================================================================ SECTION 5: LIVE CORRECTION ENGINE STRUCTURE**

# **Live Correction Engine**

class LiveCorrectionEngine:  
def init(self, printer):  
self.printer \= printer  
self.corrections \= {  
'warping': \[  
{'cmd': 'M140 S+5', 'threshold': 0.80, 'desc': 'Raise bed temp'},  
{'cmd': 'M205 X8', 'threshold': 0.90, 'desc': 'Reduce jerk'}  
\],  
'stringing': \[  
{'cmd': 'M104 S-10', 'threshold': 0.75, 'desc': 'Lower hotend temp'},  
{'cmd': 'M106 S255', 'threshold': 0.85, 'desc': 'Max fan'}  
\],  
'spaghetti': \[  
{'cmd': 'M112', 'threshold': 0.85, 'desc': 'Emergency stop'}  
\],  
'layer\_skip': \[  
{'cmd': 'M112', 'threshold': 0.80, 'desc': 'Stop print'}  
\],  
'overhang\_stringing': \[  
{'cmd': 'M220 S80', 'threshold': 0.80, 'desc': 'Slow to 80%'}  
\]  
}  
def apply\_live\_correction(self, defect):  
    """Apply corrections based on live detection"""  
    if defect\['type'\] not in self.corrections:  
        return  
      
    for correction in self.corrections\[defect\['type'\]\]:  
        if defect\['confidence'\] \> correction\['threshold'\]:  
            cmd \= self.parse\_dynamic\_command(correction\['cmd'\])  
              
            print(f"\[LIVE CORRECTION\] Applying: {cmd}")  
            self.printer.send\_live(cmd)  
              
            \# Log the correction  
            logger.log\_correction(defect, cmd)  
              
            \# Only apply first matching correction  
            break

def parse\_dynamic\_command(self, cmd\_template):  
    """Parse commands with live values"""  
    if 'S+' in cmd\_template:  
        current \= self.printer.get\_live\_temp()\['bed'\]  
        new\_temp \= current \+ int(cmd\_template.split('+')\[1\])  
        return f"M140 S{new\_temp}"  
      
    elif 'S-' in cmd\_template:  
        current \= self.printer.get\_live\_temp()\['hotend'\]  
        new\_temp \= current \- int(cmd\_template.split('-')\[1\])  
        return f"M104 S{new\_temp}"  
      
    elif 'S%' in cmd\_template:  
        return cmd\_template.replace('S%', f"S{int(cmd\_template.split('%')\[1\])}")  
      
    else:  
        return cmd\_template

# **Live Adaptive Parameters**

class LiveParameterTuner:  
def init(self):  
self.base\_hysteresis \= 5 \# Don't change if within ±5°C  
self.correction\_cooldown \= 30 \# Seconds between corrections  
    self.last\_correction \= 0  
    self.last\_temp \= {'hotend': 0, 'bed': 0}

def should\_correct\_live(self, new\_temp, target\_temp):  
    """Check if correction needed (hysteresis)"""  
    return abs(new\_temp \- target\_temp) \> self.base\_hysteresis

def is\_cooldown\_over(self):  
    """Prevent rapid correction spam"""  
    return time.time() \- self.last\_correction \> self.correction\_cooldown

\================================================================================

# **\================================================================================ SECTION 6: LIVE WEB DASHBOARD STRUCTURE**

# **Live Web Dashboard Engine**

from flask import Flask, render\_template  
from flask\_socketio import SocketIO  
import threading  
import base64  
class LiveWebDashboard:  
def init(self):  
self.app \= Flask(name)  
self.socketio \= SocketIO(self.app, cors\_allowed\_origins="\*")  
self.clients \= 0  
    self.\_setup\_routes()  
    self.\_setup\_socketio()  
      
    \# Start Flask in background thread  
    self.server\_thread \= threading.Thread(  
        target=self.socketio.run,  
        args=(self.app,),  
        kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False},  
        daemon=True  
    )  
    self.server\_thread.start()  
    print("\[LIVE WEB\] Dashboard running at http://localhost:5000")

def \_setup\_routes(self):  
    @self.app.route('/')  
    def index():  
        return render\_template('live.html')  
      
    @self.app.route('/logs')  
    def logs():  
        return render\_template('logs.html')

def \_setup\_socketio(self):  
    @self.socketio.on('connect')  
    def handle\_connect():  
        self.clients \+= 1  
        print(f"\[LIVE WEB\] Client connected ({self.clients} total)")  
        self.socketio.emit('live\_status', {'status': 'Connected', 'fps': 0})  
      
    @self.socketio.on('disconnect')  
    def handle\_disconnect():  
        self.clients \-= 1  
        print(f"\[LIVE WEB\] Client disconnected ({self.clients} total)")

def broadcast\_live\_frame(self, frame, metadata):  
    """Broadcast live frame to all connected clients"""  
    if self.clients \== 0:  
        return  \# No clients connected, skip encoding  
      
    \_, buffer \= cv2.imencode('.jpg', frame, \[cv2.IMWRITE\_JPEG\_QUALITY, 80\])  
    image\_base64 \= base64.b64encode(buffer).decode()  
      
    self.socketio.emit('live\_frame', {  
        'image': image\_base64,  
        'layer': metadata.get('layer', 0),  
        'temp': metadata.get('temp', {}),  
        'defect': metadata.get('defect', None),  
        'timestamp': time.time()  
    })

def broadcast\_live\_status(self, status\_dict):  
    """Broadcast live status update"""  
    self.socketio.emit('live\_status', status\_dict)

# **Live Web Templates (HTML) Pattern**

# **templates/live.html**

'''

\<\!DOCTYPE html\>

\<html lang="en"\>  
\<head\>  
\<meta name="viewport" content="width=device-width, initial-scale=1.0"\>  
\<title\>LIVE AI Monitor\</title\>  
\<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"\>\</script\>  
\<style\>  
body { margin: 0; background: \#1a1a1a; color: \#fff; font-family: Arial; }  
\#live\_video { width: 100%; max-width: 800px; border: 2px solid \#00ff00; }  
.status { font-size: 20px; padding: 10px; text-align: center; }  
.alert { color: \#ff0000; font-weight: bold; }  
.metrics { display: flex; justify-content: space-around; padding: 10px; }  
\</style\>  
\</head\>  
\<body\>  
\<div class="status" id="status"\>Connecting to LIVE monitor...\</div\>  
\<div class="metrics"\>  
\<div\>Layer: \<span id="layer"\>--\</span\>\</div\>  
\<div\>Hotend: \<span id="hotend"\>--°C\</span\>\</div\>  
\<div\>Bed: \<span id="bed"\>--°C\</span\>\</div\>  
\</div\>  
\<canvas id="live\_video"\>\</canvas\>  
\<div id="last\_defect"\>\</div\>  
\<script\>  
    const socket \= io();  
    const canvas \= document.getElementById('live\_video');  
    const ctx \= canvas.getContext('2d');  
      
    socket.on('live\_frame', (data) \=\> {  
        const img \= new Image();  
        img.onload \= function() {  
            canvas.width \= img.width;  
            canvas.height \= img.height;  
            ctx.drawImage(img, 0, 0);  
        };  
        img.src \= 'data:image/jpeg;base64,' \+ data.image;  
          
        document.getElementById('layer').textContent \= data.layer;  
        document.getElementById('hotend').textContent \= data.temp.hotend \+ '°C';  
        document.getElementById('bed').textContent \= data.temp.bed \+ '°C';  
          
        if (data.defect) {  
            document.getElementById('last\_defect').className \= 'alert';  
            document.getElementById('last\_defect').textContent \=   
                \`DEFECT: ${data.defect.type} (${data.defect.confidence.toFixed(2)})\`;  
        } else {  
            document.getElementById('last\_defect').className \= '';  
            document.getElementById('last\_defect').textContent \= '';  
        }  
    });  
      
    socket.on('live\_status', (data) \=\> {  
        document.getElementById('status').textContent \= data.status;  
    });  
\</script\>

\</body\>  
\</html\>  
'''