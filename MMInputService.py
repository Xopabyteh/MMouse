from . import commands
from .lib import fusionAddInUtils as futil
from .MMCamera import *
from .MMDebugWindow import *
from .MMSettings import MMSettings
import adsk.core, adsk.fusion, adsk.cam
import pygame

class MMInputService:

    def __init__(self, joystick: pygame.joystick.JoystickType):
        self.joystick = joystick
        self.settings = MMSettings()

    # Reads 6 MMouse joystick axis and returns a normalized
    # list of floats between -1 and 1
    def read_joystick_axis(self):
        # 0-Based index MMouse joystick axis:
        # 0: X 1: X
        # 2: Y 3: Y
        # 4: Z
        # 5: RX
        # 6: RY
        #  7: RZ


        axisIds = [self.settings.get_joystick_axisId(axisName) for axisName in MMSettings.axisNames]

        # Read axis values
        axisValues = [self.joystick.get_axis(axisId) for axisId in axisIds]

        # Return normalized axis using map function
        normalizedAxis = map(
            lambda axisValue,
            axisName: MMInputService.normalize_axis(axisValue, axisName, self.settings),
            axisValues,
            MMSettings.axisNames
        )

        return list(normalizedAxis)
        

    @staticmethod
    def apply_deadzone(value, deadzone=0.36):
        # Ensure the input is within the expected range
        if value < -1 or value > 1:
            raise ValueError("Input must be between -1 and 1")

        # Apply the deadzone
        if -deadzone <= value <= deadzone:
            return 0  # Value within the deadzone
        
        return value

    @staticmethod
    def apply_upper_limit(value, limit=1):
        if value > limit:
            return limit
        return value

    @staticmethod
    def normalize_axis(value, axisName, settings : MMSettings):
        # Apply deadzone
        deadzone = settings.get_deadzone(axisName)
        upperLimit = settings.get_upper_limit(axisName)

        value = MMInputService.apply_deadzone( value, deadzone)

        # Apply upper limit
        value = MMInputService.apply_upper_limit(value, upperLimit)

        # Remap from deadzone-limit to -1 to 1:
        # deadzone is now 0, upperLimit is now 1 (or -1)
        # Remap from deadzone-upperLimit to -1 to 1:
        if value > 0:
            value = (value - deadzone) / (upperLimit - deadzone)
        elif value < 0:
            value = (value + deadzone) / (upperLimit - deadzone)
        
        return value