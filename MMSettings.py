import os

from . import commands
from .lib import fusionAddInUtils as futil
from .MMCamera import *
from .MMDebugWindow import *
import adsk.core, adsk.fusion, adsk.cam, traceback
import pygame
import configparser


# Singleton instance
# Handles settings for the MMouse add-in
# Stores 6 axis ids for the joystick
# Stores deadzones and limits for each axis
# Stores the camera pan speed
# Stores the camera zoom speed
# Stores the camera rotation speed
# Displays settings in fusion UI
class MMSettings:
    addin_path = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(addin_path, 'mm_runtime_settings.ini')

    _instance = None
    axisNames = ['x', 'y', 'z', 'rx', 'ry', 'rz']

    # Singleton pattern implementation
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MMSettings, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):  # To avoid reinitialization
            return
        self.settingsLoaded = False 
        

    def ensure_settings(self):
        if self.settingsLoaded:
            return
        
        if not os.path.exists(self.settings_path):
            self.create_default_settings()
        
        self.load_settings()

    def create_default_settings(self):
        config = configparser.ConfigParser()
        config['Joystick'] = {
            'x': '0',
            'y': '2',
            'z': '4',
            'rx': '5',
            'ry': '7', # Note: swapped with rZ
            'rz': '6',
        }
        config['Deadzones'] = {
            'x': '0.36',
            'y': '0.36',
            'z': '0.36',
            'rx': '0.36',
            'ry': '0.36',
            'rz': '0.36',
        }
        config['UpperLimits'] = {
            'x': '0.9',
            'y': '0.9',
            'z': '0.9',
            'rx': '0.9',
            'ry': '0.9',
            'rz': '0.9',
        }
        config['CameraSpeeds'] = {
            'pan': '10',
            'zoom': '100',
            'rotation': '1',
            'x': 1,
            'y': 1,
            'z': 1,
            'rx': 1,
            'ry': 1,
            'rz': 1,
        }
        with open(self.settings_path, 'w') as configfile:
            config.write(configfile)

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read(self.settings_path)
        
        # Dictionaries (e.x, to get the deadzone for the x-axis: self.deadzones['x'])
        self.joystick = {axis: int(value) for axis, value in config['Joystick'].items()}
        self.deadzones = {axis: float(value) for axis, value in config['Deadzones'].items()}
        self.upper_limits = {axis: float(value) for axis, value in config['UpperLimits'].items()}

        # Camera speeds (pan, zoom, rotation)
        self.camera_speeds = {key: float(value) for key, value in config['CameraSpeeds'].items()}

        self.settingsLoaded = True

    # X -> 0, rY -> 7
    def get_joystick_axisId(self, axisName):
        return self.joystick[axisName]
    
    def get_deadzone(self, axisName):
        return self.deadzones[axisName]
    
    def get_upper_limit(self, axisName):
        return self.upper_limits[axisName]

    def invalidate_cache(self):
        # Clear cached settings
        self.settingsLoaded = False