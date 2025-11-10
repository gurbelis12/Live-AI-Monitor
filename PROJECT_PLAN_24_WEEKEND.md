\<\!-- This file contains the complete 24-weekend project guide. Content from the user's first prompt. \--\>

# **LIVE AI 3D Printer Monitor: Solo Developer Project Guide**

## **24-Weekend Plan for Real-Time Kinect \+ AI Print Monitoring**

**Author:** Solo Developer Project Plan **Date:** \[Current Date\]

## **Table of Contents**

1. [Project Overview](https://www.google.com/search?q=%23project-overview)  
2. [Hardware Requirements](https://www.google.com/search?q=%23hardware-requirements)  
3. [Software Requirements](https://www.google.com/search?q=%23software-requirements)  
4. [Critical LIVE Principles](https://www.google.com/search?q=%23critical-live-principles)  
5. [24-Weekend Timeline](https://www.google.com/search?q=%2324-weekend-timeline)  
   * [Month 1: Live Foundation & MVP](https://www.google.com/search?q=%23month-1-live-foundation--mvp)  
   * [Month 2: Live Depth Enhancement](https://www.google.com/search?q=%23month-2-live-depth-enhancement)  
   * [Month 3: Live AI Training](https://www.google.com/search?q=%23month-3-live-ai-training-active-learning)  
   * [Month 4: Live Corrections](https://www.google.com/search?q=%23month-4-live-corrections-beyond-emergency-stop)  
   * [Month 5: Live Web UI & System Integration](https://www.google.com/search?q=%23month-5-live-web-ui--system-integration)  
   * [Month 6: Live Analytics & Release](https://www.google.com/search?q=%23month-6-live-analytics--release)  
6. [Live Performance Targets](https://www.google.com/search?q=%23live-performance-targets)  
7. [Troubleshooting Live Issues](https://www.google.com/search?q=%23troubleshooting-live-issues)  
8. [Release Checklist](https://www.google.com/search?q=%23release-checklist)  
9. [Final Notes](https://www.google.com/search?q=%23final-notes)

\<a name="project-overview"\>\</a\>

## **1\. Project Overview**

Build a real-time AI monitoring system for Creality E3 V2 using Xbox Kinect V2 that detects print failures (warping, stringing, spaghetti) and automatically corrects them via G-code commands.  
**Core Features:**

* Live 30 FPS Kinect video feed (RGB \+ Depth)  
* Real-time AI inference (5 FPS)  
* Automatic emergency stop & corrective actions  
* Live web dashboard (mobile-friendly)  
* Logging & analytics

\<a name="hardware-requirements"\>\</a\>

## **2\. Hardware Requirements**

| Component | Specification | Est. Cost | Purpose |
| :---- | :---- | :---- | :---- |
| **Sensor** | Microsoft Kinect V2 (Model 1525\) | \~$30 (Used) | RGB-D Vision Source |
| **Adapter** | Kinect V2 USB 3.0 PC Adapter | \~$25 | Power & Data connectivity |
| **Host PC** | Minimum: i5 CPU, 8GB RAM. Preferred: NVIDIA GPU (GTX 1050+) | Variable | Running AI models & CV pipeline |
| **Printer Connection** | High-quality USB Mini-B cable (shielded, with ferrite core) | \~$10 | Serial communication (G-code) |
| **Mount** | Printed Tripod or V-Slot mount | \~$2 (filament) | Stable camera positioning |

\<a name="software-requirements"\>\</a\>

## **3\. Software Requirements**

| Software/Library | Version | Installation Command | Purpose |
| :---- | :---- | :---- | :---- |
| **Python** | 3.9+ | https://www.python.org/downloads/ | Core language |
| **OpenCV** | 4.5+ | pip install opencv-python | Computer vision tasks |
| **Kinect Drivers** | libfreenect2 | https://github.com/OpenKinect/libfreenect2 | Interface with Kinect |
| **Python Wrapper** | pylibfreenect2 | pip install pylibfreenect2 | Python bindings for driver |
| **AI Runtime** | TensorFlow Lite | pip install tflite-runtime | Run optimized AI models |
| **Serial Comm** | PySerial | pip install pyserial | Send G-code to printer |
| **Web Backend** | Flask | pip install Flask | Host web dashboard |
| **Database** | SQLite3 | (Built-in to Python) | Log print history |

\<a name="critical-live-principles"\>\</a\>

## **4\. Critical LIVE Principles**

**\[CALLOUT BOX\]**  
**Critical LIVE Principles: Read Before Coding**

1. **FAIL-SAFE, NOT SILENT:** If the monitor script crashes or the camera disconnects, the system MUST assume a failure and pause the print. A silent failure is a fire hazard.  
2. **LATENCY KILLS:** The entire pipeline (Capture \-\> Infer \-\> Act) must be under 1 second. A 5-second delay is 5 seconds of spaghetti you can't undo.  
3. **TRUST IS EARNED:** Start in "Log Only" mode. Graduate to "Pause Only" mode after 10+ prints with no false positives. Only enable "Kill Print" mode after 50+ successful prints.  
4. **DEPTH IS TRUTH:** The depth sensor is your ground truth for Z-axis problems. If the depth map shows a 10mm object where the G-code expects a 5mm object, trust the depth map.  
5. **ONE COMMAND AT A TIME:** Always wait for the printer to send ok after a G-code command before sending another. Flooding the serial buffer is a path to chaos.  
6. **TEST LIVE, TEST SMALL:** End every weekend with a *real*, live print. A 20-minute calibration cube test is worth more than 2 hours of simulated testing.

\<a name="24-weekend-timeline"\>\</a\>

## **5\. 24-Weekend Timeline**

\<a name="month-1-live-foundation--mvp"\>\</a\>

### **MONTH 1: Live Foundation & MVP**

**Weekend 1: Live Kinect Video Pipeline**

* **Goal:** Establish a stable, multi-threaded 30 FPS RGB \+ Depth video feed.  
* **Friday:** Install libfreenect2 drivers and pylibfreenect2. Verify connection with the provided Protonect test executable.  
* **Saturday:** Write a Python script using threading to create two separate threads: one for capturing frames (to avoid blocking) and one for displaying them with OpenCV (cv2.imshow).  
* **Sunday:** Refine the pipeline. Add frame registration to align the RGB and Depth images. Display them side-by-side. Stress-test for 1 hour to check for memory leaks or USB drops.  
* **Success Criteria:** A stable 60-minute+ live feed showing aligned RGB and Depth images.

**Weekend 2: Live Printer Control**

* **Goal:** Establish two-way serial communication with the printer.  
* **Friday:** Connect to the printer via USB. Find the correct COM port (Windows) or /dev/tty (Linux). Write a pyserial script to connect at 115200 baud.  
* **Saturday:** Implement a send\_gcode(command) function that sends a command (e.g., M105 \- get temps) and *waits* for the ok response from the printer. Parse the temperature response.  
* **Sunday:** Create functions for pause\_print() (using M25), resume\_print() (using M24), and emergency\_stop() (using M112). **Test these functions on a dry run (no filament) first\!**  
* **Success Criteria:** Python script can reliably read the printer's temperature and manually pause a live print.

**Weekend 3: Live MVP AI (Emergency Stop)**

* **Goal:** Integrate a basic pre-trained AI model to detect "spaghetti" failures.  
* **Friday:** Download a pre-trained "spaghetti detection" model (like one from The Spaghetti Detective's open-source projects) in .tflite format for efficiency.  
* **Saturday:** Integrate the TensorFlow Lite runtime into your Kinect stream. Run inference on the RGB frame once every 2 seconds (to start).  
* **Sunday:** Connect the AI to printer controls. If the model returns "spaghetti" with \> 95% confidence, trigger the emergency\_stop() function. **Test this by waving a ball of yarn in front of the printer (a "synthetic failure").**  
* **Success Criteria:** Waving a "synthetic" spaghetti failure in front of the camera triggers M112 and stops the printer within 5 seconds.

**Weekend 4: Live ROI Masking**

* **Goal:** Focus the AI's attention only on the print bed.  
* **Friday:** Write a simple utility script using OpenCV's setMouseCallback to click and define a 4-point polygon (a "Region of Interest" or ROI) for your print bed.  
* **Saturday:** Save these 4 points to a config.json file. On startup, load this ROI and use cv2.fillPoly to create a binary mask.  
* **Sunday:** Apply this mask to every frame *before* sending it to the AI. This zeroes out all data from the background, eliminating false positives from a messy desk or moving cables.  
* **Success Criteria:** The AI completely ignores any "synthetic failure" (yarn ball) held *outside* the defined print bed area.

\<a name="month-2-live-depth-enhancement"\>\</a\>

### **MONTH 2: Live Depth Enhancement**

**Weekend 5: Live Depth Calibration**

* **Goal:** Create a "baseline" depth map of the empty print bed.  
* **Friday:** With the printer cold and the bed clear, run a capture script to average 100 depth frames. This creates a stable "zero-state" map.  
* **Saturday:** Save this baseline\_depth.npy (Numpy) file.  
* **Sunday:** In your main script, load this baseline and subtract it from the *current* depth frame. This isolates only the *print* and removes any slight tilt or warping of the bed itself.  
* **Success Criteria:** The live depth feed shows the empty bed as pure black (zero height), and a calibration cube placed on it appears as a clean, isolated object.

**Weekend 6: Live Layer Guard**

* **Goal:** Detect warping or "blob" failures using pure depth data.  
* **Friday:** Parse the *current Z-height* from the printer. You can do this by sending M114 (get position) or by proxy (e.g., interfacing with OctoPrint's API if you use it).  
* **Saturday:** In your calibrated depth map, find the *maximum measured height*.  
* **Sunday:** Implement the "Layer Guard" logic: if (max\_measured\_height \> (current\_z\_height \+ 5.0)): trigger\_pause(). This detects if a part has warped up by 5mm or if a blob has formed.  
* **Success Criteria:** Starting a print and placing your finger on the bed (simulating a 15mm+ warp) triggers a system pause.

**Weekend 7: Live Fusion AI**

* **Goal:** Combine RGB-based AI and Depth-based "Layer Guard" for a single, reliable score.  
* **Friday:** Rearchitect the logic. You now have two failure signals: ai\_spaghetti\_confidence (0.0-1.0) and depth\_anomaly\_mm (0.0-50.0).  
* **Saturday:** Create a weighted "Total Risk Score". E.g., risk \= (ai\_spaghetti\_confidence \* 0.7) \+ (normalize(depth\_anomaly\_mm) \* 0.3).  
* **Sunday:** Tune these weights. A "pause" might be triggered at risk \> 0.7, and an "emergency\_stop" at risk \> 0.95. This "sensor fusion" is far more robust than one signal alone.  
* **Success Criteria:** The system can now detect *both* fine stringing (high AI score) and a large delamination (high Depth score).

**Weekend 8: Live Performance Optimization**

* **Goal:** Ensure the full pipeline (Kinect \+ ROI \+ AI \+ Depth) runs in real-time.  
* **Friday:** Profile your code using cProfile. Identify the biggest bottleneck (it's almost always AI inference or frame resizing).  
* **Saturday:** Move the AI inference to its own dedicated threading.Thread. The main thread feeds it frames via a queue.Queue, and the AI thread runs as fast as it can without blocking the video feed.  
* **Sunday:** Optimize frame processing. Ensure all resizing (cv2.resize) is done *before* applying masks or running AI, as operating on smaller images is much faster.  
* **Success Criteria:** Main video feed remains at 30 FPS, and the AI "Inference FPS" is stable at 5+ FPS.

\<a name="month-3-live-ai-training-active-learning"\>\</a\>

### **MONTH 3: Live AI Training (Active Learning)**

**Weekend 9: Live Failure Logger**

* **Goal:** Automatically save images of *potential* failures for re-training.  
* **Friday:** Write a function save\_training\_sample(frame, reason) that saves the current RGB and Depth frame to a folder, named with a timestamp and reason (e.g., 20231026\_143005\_risk\_0.6.jpg).  
* **Saturday:** Trigger this function automatically whenever Total\_Risk is in the "uncertain" range (e.g., 0.5 to 0.7).  
* **Sunday:** Add a manual "Save Failure" hotkey ('s') to your OpenCV window to manually capture failures the AI misses.  
* **Success Criteria:** After a weekend of printing, you have a new folder with 20+ images of "tricky" situations for your AI to learn from.

**Weekend 10: Live Dataset Curation**

* **Goal:** Quickly label the data you just collected.  
* **Friday:** Download a free labeling tool (like labelImg) or write a simple Python script: show an image, press 's' for 'spaghetti', 'w' for 'warping', 'n' for 'normal'.  
* **Saturday:** Go through your logged images from W9 and label them all.  
* **Sunday:** Augment your dataset. Take your "failure" images and apply random flips, crops, and brightness changes to create 10x more training data.  
* **Success Criteria:** You have a new, labeled training dataset of 200+ images *specific to your printer and lighting*.

**Weekend 11: Live Model Fine-Tuning**

* **Goal:** Re-train your AI model with your new, specific data.  
* **Friday:** Set up a Google Colab notebook to use their free GPUs for training.  
* **Saturday:** Load your W3 base model and "fine-tune" it on your new dataset for 100 epochs. This updates the model's weights to be better at recognizing *your* failures.  
* **Sunday:** Download the new .tflite model file (model\_v2.tflite) and test it.  
* **Success Criteria:** The new model shows a \>90% confidence on a failure image that the V1 model only scored as 60%.

**Weekend 12: Live Model Swap**

* **Goal:** Implement "hot-swapping" to update the AI without restarting the monitor.  
* **Friday:** In your main script, check the modification time of the model.tflite file on disk.  
* **Saturday:** If the file has changed, signal the AI inference thread to pause, reload the tflite.Interpreter with the new model file, and resume.  
* **Sunday:** Test this live: while monitoring a print, replace model.tflite with model\_v2.tflite. The monitor should update its AI "brain" mid-print without crashing.  
* **Success Criteria:** The OpenCV window text changes from "Model: v1" to "Model: v2" live, without dropping a single video frame.

\<a name="month-4-live-corrections-beyond-emergency-stop"\>\</a\>

### **MONTH 4: Live Corrections (Beyond Emergency Stop)**

**Weekend 13: Live Temperature Adjustment**

* **Goal:** Automatically correct for minor stringing by adjusting temperature.  
* **Friday:** Create a new "Stringing" class in your AI model (using your W10 dataset).  
* **Saturday:** Implement "Corrective Action" logic: if (stringing\_confidence \> 0.8) and (time\_since\_last\_correction \> 10\_minutes): send\_gcode("M104 S{current\_temp \- 5}").  
* **Sunday:** Test this on a string-prone filament (like PETG). Watch the printer's console to see the temperature command being sent.  
* **Success Criteria:** The system detects minor stringing and autonomously lowers the hotend temp by 5°C, reducing the stringing on subsequent layers.

**Weekend 14: Live Speed Adjustment**

* **Goal:** Automatically slow down the print if a "wobble" or "blob" is detected.  
* **Friday:** Use your depth map to detect sudden Z-height anomalies (blobs).  
* **Saturday:** Implement logic: if (blob\_detected): send\_gcode("M220 S75") (Set feed rate to 75%).  
* **Sunday:** Implement a "cool-down" period: if the blob is stable for 5 minutes, return to 100% speed: M220 S100.  
* **Success Criteria:** A small part detaching and sticking to the nozzle (forming a blob) causes the printer to slow down, increasing the chance of recovery.

**Weekend 15: Live Pause & Resume**

* **Goal:** Perfect the "Pause" state instead of just killing the print.  
* **Friday:** Refine the pause\_print() function. It should: M25 (pause), move the head away (G1 X0 Y0 Z{current\_z \+ 10}), and send M300 (beep) to alert you.  
* **Saturday:** Add a "Pause" state to your main loop. When paused, the AI continues monitoring the bed.  
* **Sunday:** Add a hotkey ('r') to trigger resume\_print() (M24), which allows you to manually clear a blob and then resume.  
* **Success Criteria:** The system pauses, beeps, you run over, pull off a blob, hit 'r', and the print successfully resumes.

**Weekend 16: Live Adaptive Confidence**

* **Goal:** Make the AI "learn" from your corrections to reduce false positives.  
* **Friday:** Every time the system pauses and you hit "Resume," log this as a "false positive" event.  
* **Saturday:** If 3 false positives occur in one print, automatically *increase* the Total\_Risk threshold for a pause (e.g., from 0.7 to 0.75).  
* **Sunday:** Save this new threshold to your config.json file so it persists. This makes the system less "trigger-happy" over time, adapting to your specific needs.  
* **Success Criteria:** The system "cries wolf" less often after a week of use, as the confidence threshold has self-adjusted.

\<a name="month-5-live-web-ui--system-integration"\>\</a\>

### **MONTH 5: Live Web UI & System Integration**

**Weekend 17: Live Web UI (Flask)**

* **Goal:** Create a web-based dashboard to monitor the print from your phone.  
* **Friday:** Set up a basic Flask web server in a new thread.  
* **Saturday:** Create an HTML page. Use mjpeg-streamer techniques to stream the OpenCV video feed from Python to a \<img\> tag in the browser.  
* **Sunday:** Add status text (Current Temp, AI Risk Score) to the webpage, updated via AJAX calls to a /status.json endpoint on your Flask server.  
* **Success Criteria:** You can watch a live 30 FPS video feed of your printer from your phone's web browser (on the same WiFi).

**Weekend 18: Live Mobile Dashboard**

* **Goal:** Add *control* to the web dashboard.  
* **Friday:** Add "Pause," "Resume," and "Emergency Stop" buttons to the HTML page.  
* **Saturday:** Create Flask endpoints (e.g., /api/pause) that your buttons call. These endpoints trigger your existing Python pause\_print() functions.  
* **Sunday:** Use a simple CSS framework (like Bootstrap) to make the buttons large and mobile-friendly. **Add a password or simple auth to your endpoints\!**  
* **Success Criteria:** You can successfully PAUSE and RESUME a print from your phone.

**Weekend 19: Live Multi-Threading**

* **Goal:** Finalize the system architecture for stability.  
* **Friday:** Review your threading logic. You should now have at least 4 threads:  
  1. KinectStream (high-priority, handles I/O).  
  2. AI\_Inference (low-priority, CPU-bound).  
  3. FlaskServer (runs the web dashboard).  
  4. MainThread (handles logic, OpenCV display, printer comms).  
* **Saturday:** Implement queue.Queue objects for passing data (like frames and commands) safely between threads to prevent race conditions.  
* **Sunday:** Stress test by opening 5 browser tabs on your dashboard while the AI is running. The main loop should not lag.  
* **Success Criteria:** The system runs for 6+ hours with all threads active, without deadlocks or crashes.

**Weekend 20: Live Connection Recovery**

* **Goal:** Make the system robust against USB cable glitches.  
* **Friday:** Add try...except blocks around your pyserial ser.write() and ser.read() calls.  
* **Saturday:** If a serial exception occurs, start a "reconnect" loop that tries to re-open the serial port every 5 seconds.  
* **Sunday:** Do the same for the Kinect. If the listener.waitForNewFrame() fails, try to re-initialize the Freenect2 device. If reconnection fails for 60s, trigger an emergency pause.  
* **Success Criteria:** You can physically unplug the printer's USB cable and plug it back in; the monitor script automatically reconnects and continues.

\<a name="month-6-live-analytics--release"\>\</a\>

### **MONTH 6: Live Analytics & Release**

**Weekend 21: Live Database**

* **Goal:** Log all print history and failures to a persistent database.  
* **Friday:** Set up a sqlite3 database (prints.db). Create tables: print\_jobs (start\_time, end\_time, status) and failure\_events (timestamp, failure\_type, risk\_score, snapshot\_path).  
* **Saturday:** Integrate db.execute(...) commands into your main loop. Log the start of a print, and log every time a failure is detected or a correction is made.  
* **Sunday:** When a print finishes (or is stopped), update its print\_jobs record with the final status ("Completed," "AI\_Stopped," "User\_Stopped").  
* **Success Criteria:** After 3 prints, your prints.db file contains a complete history of those jobs and any failures that occurred.

**Weekend 22: Live Analytics Dashboard**

* **Goal:** Visualize your print history and failure data.  
* **Friday:** Add a new /analytics page to your Flask app.  
* **Saturday:** Use a simple JavaScript charting library (like Chart.js) to query a new /api/print\_history endpoint and display a bar chart of "Success vs. Failure" rates.  
* **Sunday:** Add a gallery that loads all the saved failure images from your database, letting you review past failures.  
* **Success Criteria:** Your web dashboard now has a "History" tab that shows you a chart of your printer's long-term reliability.

**Weekend 23: Live 24-Hour Burn-In**

* **Goal:** A final, comprehensive stress test of the entire system.  
* **Friday:** Start a large, 24-hour+ print.  
* **Saturday:** Let the system run completely unattended (but stay nearby with a fire extinguisher, just in case). Monitor it only from the web dashboard.  
* **Sunday:** Review the 24-hour logs. Did the script crash? Did it have memory leaks? Did it false-positive? Did it miss a real failure? This is your final exam.  
* **Success Criteria:** The 24-hour print completes successfully, OR it fails, and the system correctly pauses/stops it, and the script itself runs for 24 hours without crashing.

**Weekend 24: Live Release**

* **Goal:** Clean up, document, and package your project.  
* **Friday:** Clean your code. Add comments. Move all hard-coded values (like PRINTER\_PORT) to a single config.json file.  
* **Saturday:** Write a comprehensive README.md file. Include installation steps, how to run the ROI calibrator, and what each feature does.  
* **Sunday:** Initialize a git repository, make your first commit, and upload it to GitHub. Congratulations, you're an open-source developer.  
* **Success Criteria:** You have a clean, shareable project on GitHub that another solo developer could (in theory) download and use.

\<a name="live-performance-targets"\>\</a\>

## **6\. Live Performance Targets**

| Metric | Target | Minimum Acceptable | Notes |
| :---- | :---- | :---- | :---- |
| **Video Latency** | \< 200ms | \< 500ms | Delay between reality and what you see on screen. |
| **AI Inference FPS** | 5 FPS | 2 FPS | How many times per second the AI checks for failure. |
| **Time to Detect** | \< 3 seconds | \< 10 seconds | Time from spaghetti *start* to M112 command. |
| **False Positive Rate** | \< 1 per 50h | \< 1 per 10h | Rate of unnecessary pauses on good prints. |
| **System CPU Load** | \< 40% (avg) | \< 75% (avg) | Must leave resources for the OS and other tasks. |
| **System RAM Usage** | \< 1 GB | \< 2 GB | Check for memory leaks. |

\<a name="troubleshooting-live-issues"\>\</a\>

## **7\. Troubleshooting Live Issues**

| Symptom | Probable Cause | Solution |
| :---- | :---- | :---- |
| **Video feed is laggy or stuttering** | AI inference is blocking the main thread. | Move AI interpreter.invoke() to a separate threading.Thread. |
| **Printer disconnects randomly** | USB power management (OS) or EMI from printer. | 1\. Disable USB power saving. 2\. Use a high-quality, shielded USB cable with a ferrite core. |
| **"Permission Denied" on COM port** | Another program (e.g., Cura, PrusaSlicer) is using the port. | Close all other slicer/printer control software. |
| **AI sees "ghosts" or false spaghetti** | Poor lighting, shadows, or reflective bed. | 1\. Improve room lighting. 2\. Add an LED strip to the printer. 3\. Re-train with "shadowy" images as 'normal'. |
| **Kinect depth is noisy or has holes** | USB 3.0 bandwidth issue or reflective/black filament. | 1\. Ensure Kinect is on its own USB 3.0 root hub. 2\. Black/shiny materials absorb IR light; AI must rely more on RGB. |

\<a name="release-checklist"\>\</a\>

## **8\. Release Checklist**

* \[ \] **Code:** config.json is separated from main script.  
* \[ \] **Code:** All personal keys/passwords removed from code.  
* \[ \] **Code:** requirements.txt file is generated (pip freeze \> requirements.txt).  
* \[ \] **Code:** All debug print() statements are removed or commented out.  
* \[ \] **Documentation:** README.md is written with clear install and usage steps.  
* \[ \] **Documentation:** LICENSE file is included (e.g., MIT or GPLv3).  
* \[ \] **Testing:** ROI calibrator script works.  
* \[ \] **Testing:** System successfully auto-recovers from printer USB disconnect.  
* \[ \] **Testing:** System correctly identifies a "synthetic" spaghetti test.  
* \[ \] **Testing:** Web dashboard "Emergency Stop" button works.

\<a namename="final-notes"\>\</a\>

## **9\. Final Notes**

* This is a living document. You *will* get stuck, and you *will* need to adjust this plan. That is part of the process.  
* Always test "kill" commands (M112) with your hand on the printer's power switch. Trust, but verify.  
* Document every change in a git commit. When you break something, git revert will be your best friend.  
* Join the community: r/3Dprinting, The Spaghetti Detective Discord, and other forums are invaluable.