# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusionAddInUtils as futil
from .MMCamera import *
from .MMDebugWindow import *
from .MMInputService import *
from .MMSettingsTransient import *
import adsk.core, adsk.fusion, adsk.cam, traceback
import pygame
import threading


running = False
stopping = False

def run(context):
    global running
    running = True

    try:
        commands.start()
        futil.log('MMouse run')

        # Init joystick
        pygame.init()
        pygame.joystick.init()

        # Create a thread to run the joystick loop
        thread = threading.Thread(target=mmouse_loop_wrapper,)
        thread.start()

        futil.log('MMouse running')            

    except:
        futil.handle_error('run')

# Ran on a separate thread
def mmouse_loop_wrapper():
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        inputService = MMInputService(joystick)

        settings = MMSettingsTransient()

        debugWindow = None
        # debugWindow = MMDebugWindow()

        mmouse_loop(inputService, settings, debugWindow)
    except:
        futil.handle_error('joystick_loop_wrapper')

def mmouse_loop(inputService : MMInputService, mmSettings : MMSettingsTransient, debugWindow : MMDebugWindow = None):
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

        # Get delta time
        currentTime = pygame.time.get_ticks()
        deltaTime = (currentTime - lastTime) / 1000 # In seconds
        lastTime = currentTime

        # Ensure settings are loaded
        mmSettings.ensure_settings()

        # Read joystick axis
        joystickAxis = inputService.read_joystick_axis()

        # Show debug window (if available) 
        if debugWindow:
            debugWindow.show_debug(joystickAxis, mmCamera, viewport)

        # Handle camera movement
        handle_camera_movement(joystickAxis, viewport, mmCamera, mmSettings, deltaTime)

        # Sleep for a bit to avoid hogging the CPU
        pygame.time.wait(10)

    # -> Broke out of loop
    # stop(None)


def handle_camera_movement(
        joystickAxis: list[float],
        viewport : adsk.core.Viewport,
        mmCamera : MMCamera,
        mmSettings : MMSettingsTransient,
        deltaTime: float):
    # If all axis are zero, return
    if (joystickAxis[0] + joystickAxis[1] + joystickAxis[2] + joystickAxis[3] + joystickAxis[4] + joystickAxis[5]) == 0:
        return

    # Load camera from viewport (if the user has changed the camera without MMouse)
    mmCamera.load_from_camera(viewport.camera)

    panSpeed = mmSettings.camera_speeds['pan'] * deltaTime
    zoomSpeed = mmSettings.camera_speeds['zoom'] * deltaTime
    rotationSpeed = mmSettings.camera_speeds['rotation'] * deltaTime

    # Slows down the camera movement based on how zoomed in we are
    zoomDependendDampening = mmSettings.camera_speeds['zoom_dependend_dampening']
    zoom = mmCamera.get_virtual_zoom()
    panSpeed = zoom_dampen(panSpeed, zoom, zoomDependendDampening)
    zoomSpeed = zoom_dampen(zoomSpeed, zoom, zoomDependendDampening)
    rotationSpeed = zoom_dampen(rotationSpeed, zoom, zoomDependendDampening)

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
        joystickAxis[4] * rotationSpeed, # Joystick rY
        joystickAxis[5] * rotationSpeed # Joystick rZ
    )
    mmCamera.apply_to_camera(cameraCopy)    
    
    # Update viewport   
    viewport.camera = cameraCopy
    viewport.refresh()
    return

def zoom_dampen(moveSpeed: float, cameraDistance: float, zoomDependendDampening: float):
    # Dampening is value from 0 to 1 (0 = no dampening, 1 = full dampening)

    # Remap cameraDistance from 0-50 to 0-1 & clamp
    cameraDistance = cameraDistance / 50
    cameraDistance = max(0, min(1, cameraDistance))
    zoom = 1 - cameraDistance # 1 = zoomed in, 0 = zoomed out

    # Calculate dampening (the less camera distance, the less moveSpeed)
    dampening = zoomDependendDampening * zoom
    moveSpeed = moveSpeed * (1 - dampening)
    
    return moveSpeed


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

    
