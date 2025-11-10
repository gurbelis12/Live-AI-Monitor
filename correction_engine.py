"""
================================================================================
PROJECT: Live AI 3D Printer Monitor
FILE: correction_engine.py
PURPOSE: Applies corrective G-code actions based on AI defects.
Based on: SECTION 5: LIVE CORRECTION ENGINE STRUCTURE
================================================================================
"""

import time
import re

class LiveCorrectionEngine:
    """
    Receives defect info and sends corrective commands to the printer.
    Based on: Live Correction Engine
    """
    def __init__(self, printer, logger):
        self.printer = printer
        self.logger = logger
        self.tuner = LiveParameterTuner()
        
        # Define correction strategies
        # These are examples. TUNE THEM CAREFULLY.
        self.corrections = {
            'warping': [
                {'cmd': 'M140 S+5', 'threshold': 0.80, 'desc': 'Raise bed temp'},
                {'cmd': 'M220 S90', 'threshold': 0.90, 'desc': 'Slow to 90%'}
            ],
            'stringing': [
                {'cmd': 'M104 S-5', 'threshold': 0.75, 'desc': 'Lower hotend temp'},
                {'cmd': 'M106 S255', 'threshold': 0.85, 'desc': 'Max fan'}
            ],
            'spaghetti': [
                {'cmd': 'M112', 'threshold': 0.85, 'desc': 'Emergency stop'}
            ],
            'layer_skip': [
                {'cmd': 'M112', 'threshold': 0.80, 'desc': 'Stop print'}
            ],
            'overhang_stringing': [
                {'cmd': 'M220 S80', 'threshold': 0.80, 'desc': 'Slow to 80%'}
            ],
            'anomaly': [ # From default YOLO
                {'cmd': 'M112', 'threshold': 0.90, 'desc': 'Emergency stop'}
            ]
        }
        print("[CORRECTOR] Correction Engine initialized.")

    def apply_live_correction(self, defect):
        """
        Apply corrections based on live detection, checking cooldowns.
        """
        defect_type = defect['type']
        
        if defect_type not in self.corrections:
            print(f"[CORRECTOR] No correction strategy found for defect: {defect_type}")
            return
            
        if not self.tuner.is_cooldown_over():
            print(f"[CORRECTOR] Cooldown active. Skipping correction for {defect_type}.")
            return

        for correction in self.corrections[defect_type]:
            if defect['confidence'] > correction['threshold']:
                
                # Parse the dynamic command
                cmd = self.parse_dynamic_command(correction['cmd'])
                
                if cmd is None:
                    print(f"[CORRECTOR] Could not parse dynamic command: {correction['cmd']}")
                    continue
                
                print(f"[CORRECTOR] Applying: {correction['desc']} (G-code: {cmd})")
                
                # Send the command
                self.printer.send_live(cmd)
                
                # Log and reset cooldown
                self.logger.log_correction(defect, cmd)
                self.tuner.reset_cooldown()
                
                # Only apply the first (highest priority) matching correction
                break
    
    def parse_dynamic_command(self, cmd_template):
        """
        Parse commands with live values (e.g., S+5, S-10).
        """
        try:
            if 'S+' in cmd_template or 'S-' in cmd_template:
                # Get current temps
                temps = self.printer.get_live_temp()
                if temps is None:
                    print("[CORRECTOR] Cannot apply dynamic temp: M105 failed.")
                    return None

                delta = int(re.findall(r'[+-]\d+', cmd_template)[0])

                if 'M140' in cmd_template: # Bed temp
                    current = temps['bed_target'] # Adjust target, not actual
                    new_temp = current + delta
                    return f"M140 S{new_temp}"
                
                elif 'M104' in cmd_template: # Hotend temp
                    current = temps['hotend_target'] # Adjust target, not actual
                    new_temp = current + delta
                    return f"M104 S{new_temp}"
            
            else:
                # Static command (e.g., M112, M220 S80)
                return cmd_template
                
        except Exception as e:
            print(f"[CORRECTOR] Error parsing dynamic command '{cmd_template}': {e}")
            return None

class LiveParameterTuner:
    """
    Manages correction frequency and hysteresis.
    Based on: Live Adaptive Parameters
    """
    def __init__(self):
        self.correction_cooldown_sec = 30  # Seconds between corrections
        self.last_correction_time = 0
        print(f"[TUNER] Parameter Tuner initialized. Cooldown: {self.correction_cooldown_sec}s")
    
    def is_cooldown_over(self):
        """Prevent rapid correction spam"""
        return (time.time() - self.last_correction_time) > self.correction_cooldown_sec
        
    def reset_cooldown(self):
        """Call this after a successful correction."""
        self.last_correction_time = time.time()