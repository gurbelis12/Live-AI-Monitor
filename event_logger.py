"""
================================================================================
PROJECT: Live AI 3D Printer Monitor
FILE: event_logger.py
PURPOSE: Simple event logger for system, defects, and corrections.
Based on: Mention of 'LiveEventLogger' in SECTION 1
================================================================================
"""

import logging
import time

class LiveEventLogger:
    """
    A simple wrapper for Python's logging module to create a
    structured log file for all monitor events.
    """
    def __init__(self, log_file='print_monitor.log'):
        self.log_file = log_file
        
        # Set up the logger
        self.logger = logging.getLogger('LiveMonitor')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers if re-initialized
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        # Create file handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - (%(threadName)s) - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # Add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
        self.logger.info("="*30)
        self.logger.info("LiveEventLogger initialized.")
        self.logger.info(f"Logging to: {log_file}")
        self.logger.info("="*30)

    def log_system(self, message):
        """Log a general system message."""
        self.logger.info(f"SYSTEM: {message}")
        
    def log_defect(self, defect):
        """Log a detected defect."""
        msg = f"DEFECT: Type={defect['type']}, " \
              f"Conf={defect['confidence']:.2f}, " \
              f"BBox={defect['bbox']}"
        self.logger.warning(msg)

    def log_correction(self, defect, command):
        """Log a corrective action."""
        msg = f"CORRECTION: Applied '{command}' for " \
              f"defect '{defect['type']}' " \
              f"(Conf: {defect['confidence']:.2f})"
        self.logger.critical(msg)