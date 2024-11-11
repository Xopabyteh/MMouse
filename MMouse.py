# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusionAddInUtils as futil
from .MMCamera import *
from .MMDebugWindow import *
import adsk.core, adsk.fusion, adsk.cam, traceback
import pygame
import threading


running = False
stopping = False

def run(context):
    global pyScreen, font, running
    running = True

    try:
        commands.start()
        futil.log('MMouse run')

        # Init joystick
        pygame.init()
        pygame.joystick.init()

        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        # Create a thread to run the joystick loop
        thread = threading.Thread(target=joystick_loop_wrapper, args=(joystick,))
        thread.start()

        futil.log('MMouse running')            

    except:
        futil.handle_error('run')

def joystick_loop_wrapper(joystick: pygame.joystick.JoystickType):
    try:
        joystick_loop(joystick, debugWindow=None)
    except:
        futil.handle_error('joystick_loop_wrapper')

def joystick_loop(joystick: pygame.joystick.JoystickType, debugWindow : MMDebugWindow = None):
    # This function runs in a separate thread
    global running
    futil.log('Joystick loop start, running:' + str(running))
    
    # Get viewport
    app = adsk.core.Application.get()
    viewport = app.activeViewport

    # Initialize virtual camera
    mmCamera = MMCamera(viewport)

    # Used to calculate delta time
    lastTime = pygame.time.get_ticks()

    # Main loop
    while running:
        # Keep the event queue clear
        pygame.event.pump()

        # Read joystick axis
        joystickAxis = read_joystick_axis(joystick)

        # Show debug window (if available) 
        if debugWindow:
            debugWindow.show_debug(joystickAxis, mmCamera, viewport)

        # Get delta time
        currentTime = pygame.time.get_ticks()
        deltaTime = (currentTime - lastTime) / 1000 # In seconds
        lastTime = currentTime

        # Handle camera movement
        handle_camera_movement(joystickAxis, viewport, mmCamera, deltaTime)

        # Sleep for a bit to avoid hogging the CPU
        pygame.time.wait(10)

    # -> Broke out of loop
    # stop(None)


def handle_camera_movement(joystickAxis: list[float], viewport : adsk.core.Viewport, mmCamera : MMCamera, deltaTime: float):
    # If all axis are zero, return
    if (joystickAxis[0] + joystickAxis[1] + joystickAxis[2] + joystickAxis[3] + joystickAxis[4] + joystickAxis[5]) == 0:
        return
    
    panSpeed = 10 * deltaTime
    zoomSpeed = 100 * deltaTime
    rotationSpeed = 1 * deltaTime
    # Get camera copy
    cameraCopy = viewport.camera
    cameraCopy.isSmoothTransition = False

    # Apply modified mmCamera:
    # Translation by:
    # x: Left/Right (Pan)
    # y: Forward/Backward (Zoom)
    # z: Up/Down (Pan)
    mmCamera.pan_by(
        joystickAxis[0] * panSpeed,
        joystickAxis[1] * panSpeed
    )
    mmCamera.zoom_by(
        joystickAxis[2] * zoomSpeed
    )
    mmCamera.rotate_by(
        -joystickAxis[3] * rotationSpeed, # Joystick rX
        joystickAxis[5] * rotationSpeed, # Joystick rZ note: [4] and [5] are swapped
        joystickAxis[4] * rotationSpeed # Joystick rY
    )
    mmCamera.apply_to_camera(cameraCopy)    
    
    # Update viewport   
    viewport.camera = cameraCopy
    viewport.refresh()
    return

# Reads 6 MMouse joystick axis and returns a normalized
# list of floats between -1 and 1
def read_joystick_axis(joystick: pygame.joystick.JoystickType):
    # 0-Based index MMouse joystick axis:
    # 0: X 1: X
    # 2: Y 3: Y
    # 4: Z 5: RX
    # 6: RY 7: RZ

    x = joystick.get_axis(0)
    y = joystick.get_axis(2)
    z = joystick.get_axis(4)
    rx = joystick.get_axis(5)
    ry = joystick.get_axis(6)
    rz = joystick.get_axis(7)

    # Apply deadzones
    deadzonedAxis = map(apply_deadzone_and_remap, [x, y, z, rx, ry, rz])

    return list(deadzonedAxis)


def apply_deadzone_and_remap(value, deadzone=0.36):
    # Ensure the input is within the expected range
    if value < -1 or value > 1:
        raise ValueError("Input must be between -1 and 1")

    # Apply the deadzone
    if -deadzone <= value <= deadzone:
        return 0  # Value within the deadzone

    # Map values outside the deadzone
    if value > deadzone:
        # Map from [deadzone, 1] to [0, 1]
        return (value - deadzone) / (1 - deadzone)
    else:
        # Map from [-deadzone, -1] to [0, -1]
        return (value + deadzone) / (1 - deadzone)
    
def stop(context):
    global stopping, running
    if stopping: # Ensure idepotency
        return
    
    stopping = True
    futil.log('MMouse stopping')
    
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.stop()

        running = False
        pygame.quit()

        futil.log('MMouse stopped')
    except:
        futil.handle_error('stop')

    
