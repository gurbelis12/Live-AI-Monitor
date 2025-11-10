"""
================================================================================
PROJECT: Live AI 3D Printer Monitor
FILE: printer_control.py
PURPOSE: Live serial communication with 3D printer.
Based on: SECTION 3: LIVE PRINTER CONTROL STRUCTURE
================================================================================
"""

import serial
import time
import re

# Critical G-code Command Reference
COMMANDS = {
    'emergency_stop': 'M112',
    'get_temp': 'M105',
    'set_hotend_temp': 'M104 S{}', # S{temp}
    'set_bed_temp': 'M140 S{}', # S{temp}
    'adjust_speed': 'M220 S{}', # S{percentage}
    'adjust_flow': 'M221 S{}', # S{percentage}
    'set_fan': 'M106 S{}', # S{0-255}
    'pause_print': 'M25',
    'resume_print': 'M24',
    'home_all': 'G28',
    'move_to': 'G1 X{} Y{} Z{} F{}', # X, Y, Z, F{speed}
    'show_message': 'M117 {}' # {message}
}

class LivePrinterControl:
    """
    Handles serial connection, G-code sending, and response parsing.
    Includes auto-reconnect logic.
    Based on: Live Printer Serial Pattern
    """
    def __init__(self, port='COM3', baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None
        # Regex to parse: "ok T:205.1 /210.0 B:60.2 /70.0"
        self.temp_regex = re.compile(r"T:(\d+\.?\d*)\s?/(\d+\.?\d*)\s+B:(\d+\.?\d*)\s?/(\d+\.?\d*)")
        self.connect_live()
    
    def connect_live(self):
        """
        Attempt to connect to the printer.
        Includes auto-retry logic.
        """
        print(f"[PRINTER] Attempting to connect on {self.port} at {self.baud}...")
        while True:
            try:
                self.ser = serial.Serial(self.port, self.baud, timeout=2)
                time.sleep(2)  # Wait for bootloader
                response = self.ser.readline().decode().strip()
                print(f"[PRINTER] Connection established. Initial response: {response}")
                return
            except serial.SerialException as e:
                print(f"[PRINTER] Connection failed: {e}. Retrying in 5s...")
                time.sleep(5)
    
    def send_live(self, gcode):
        """
        Send a G-code command and wait for 'ok' response.
        Includes error recovery.
        """
        if self.ser is None or not self.ser.is_open:
            print("[PRINTER] Connection lost, attempting to reconnect...")
            self.connect_live()
            if self.ser is None: # Still failed
                print("[PRINTER] Reconnect failed. Command skipped.")
                return None

        try:
            # print(f"[PRINTER SEND] G-code: {gcode}") # Uncomment for verbose logging
            self.ser.write(gcode.encode() + b'\n')
            
            # Read lines until 'ok' or error
            response_buffer = ""
            while True:
                response = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if not response:
                    continue # Skip empty lines (timeout)
                
                # print(f"[PRINTER RECV] {response}") # Uncomment for verbose logging
                response_buffer += response + "\n" # Store for parsing
                
                if 'ok' in response:
                    return response_buffer # Command successful
                if 'error' in response.lower() or 'unknown command' in response.lower():
                    print(f"[PRINTER ERROR] Printer reported error for command: {gcode}")
                    return None
                    
        except serial.SerialException as e:
            print(f"[PRINTER] SerialException: {e}. Reconnecting...")
            self.connect_live()
            return None
        except Exception as e:
            print(f"[PRINTER] Unexpected error in send_live: {e}")
            return None

    def get_live_temp(self):
        """
        Get current temperatures by sending M105.
        Returns: dict {'hotend': float, ...} or None
        """
        resp = self.send_live(COMMANDS['get_temp'])
        
        if resp:
            match = self.temp_regex.search(resp)
            if match:
                try:
                    hotend_actual = float(match.group(1))
                    hotend_target = float(match.group(2))
                    bed_actual = float(match.group(3))
                    bed_target = float(match.group(4))
                    
                    return {
                        'hotend': hotend_actual, 
                        'hotend_target': hotend_target,
                        'bed': bed_actual,
                        'bed_target': bed_target
                    }
                except ValueError:
                    print(f"[PRINTER] Error parsing temp response: {resp}")
                    return None
        return None
    
    def emergency_stop_live(self):
        """Immediate stop - bypasses everything"""
        print("[PRINTER] EMERGENCY STOP (M112) TRIGGERED!")
        self.send_live(COMMANDS['emergency_stop'])
    
    def set_temp_live(self, hotend=None, bed=None):
        """Dynamic temperature adjustment"""
        if hotend is not None:
            self.send_live(COMMANDS['set_hotend_temp'].format(hotend))
        if bed is not None:
            self.send_live(COMMANDS['set_bed_temp'].format(bed))
    
    def adjust_speed_live(self, percentage):
        """Live speed override (percentage 0-100+)"""
        self.send_live(COMMANDS['adjust_speed'].format(percentage))
    
    def pause_live(self, reason="AI PAUSED"):
        """Pause print and show message on LCD"""
        self.send_live(COMMANDS['show_message'].format(reason.replace(" ", "_")))
        self.send_live(COMMANDS['pause_print'])
    
    def resume_live(self):
        """Resume from pause"""
        self.send_live(COMMANDS['show_message'].format("AI RESUMED"))
        self.send_live(COMMANDS['resume_print'])
        
    def close(self):
        """Safely close the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[PRINTER] Serial connection closed.")