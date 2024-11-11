# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusionAddInUtils as futil
from .MMCamera import *
import adsk.core, adsk.fusion, adsk.cam, traceback
import pygame
import threading

pyScreen : pygame.Surface | None = None
font: pygame.font.Font | None = None
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

        # Screen
        pygame.display.init()
        pygame.font.init()
        pyScreen = pygame.display.set_mode((800, 480))
        font = pygame.font.Font(None, 36)

        # Create a thread to run the joystick loop
        thread = threading.Thread(target=joystick_loop_wrapper, args=(joystick,))
        thread.start()

        futil.log('MMouse running')            

    except:
        futil.handle_error('run')

def joystick_loop_wrapper(joystick: pygame.joystick.JoystickType):
    try:
        joystick_loop(joystick)
    except:
        futil.handle_error('joystick_loop_wrapper')

def joystick_loop(joystick: pygame.joystick.JoystickType):
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
        
        # Show axis on the screen
        pyScreen.fill((0, 0, 0))
        display_joystick_axis(joystickAxis, 0, 0)
        display_mm_camera(mmCamera, 300, 0)
        dispaly_camera(viewport.camera, 0, 300)
        
        pygame.display.flip()

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

axis_labels = ['x', 'y', 'z', 'rx', 'ry', 'rz']
def display_joystick_axis(joystickAxis: list[float], start_x: int, start_y: int):
    # Show header
    pyScreen.blit(font.render('Joystick axis', True, (255, 255, 255)), (start_x, start_y))

    # Show axis
    for index, label in enumerate(axis_labels):
        value = joystickAxis[index]
        text = f'{label}: {value:.2f}'
        pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, index * 36 + 40 + start_y))

def display_mm_camera(mmCamera: MMCamera, start_x: int, start_y: int):
    # Show header
    pyScreen.blit(font.render('MMCamera', True, (255, 255, 255)), (start_x, start_y))

    # Show camera eye
    eye = mmCamera.virtualEye
    text = f'V Eye: {eye.x:.2f}, {eye.y:.2f}, {eye.z:.2f}'
    pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 36 + start_y))

    # Show virtual target direction
    vtOffset = mmCamera.virtualTargetForward
    text = f'VT forward: {vtOffset.x:.2f}, {vtOffset.y:.2f}, {vtOffset.z:.2f}'
    pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 72 + start_y))

    # Show virtual camera forward length
    virtualCamForward = mmCamera.forwardEyeToTargetLength
    text = f'VT fw length: {virtualCamForward:.2f}'
    pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 108 + start_y))

    # Show absolute virtual target
    absoluteTarget = mmCamera.calc_absolute_target()
    text = f'VT Absolute: {absoluteTarget.x:.2f}, {absoluteTarget.y:.2f}, {absoluteTarget.z:.2f}'
    pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 142 + start_y))

    # Show up vector
    up = mmCamera.upVector
    text = f'Up: {up.x:.2f}, {up.y:.2f}, {up.z:.2f}'
    pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 178 + start_y))


def dispaly_camera(camera: adsk.core.Camera, start_x: int, start_y: int):
    # Show header
    pyScreen.blit(font.render('Camera', True, (255, 255, 255)), (start_x, start_y))

    # Show eye
    eye = camera.eye
    text = f'Eye: {eye.x:.2f}, {eye.y:.2f}, {eye.z:.2f}'
    pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 36 + start_y))

    # Show target
    target = camera.target
    text = f'Target: {target.x:.2f}, {target.y:.2f}, {target.z:.2f}'
    pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 72 + start_y))

    # Show extents (tuple bool float float)
    # or perspective angle (depending on camera type)
    if camera.cameraType == adsk.core.CameraTypes.PerspectiveCameraType:
        text = f'Perspective angle: {camera.perspectiveAngle:.2f}'
        pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 108 + start_y))
    else:
        extents = camera.getExtents()
        text = f'Extents: {extents[0]}, {extents[1]:.2f}, {extents[2]:.2f}'
        pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 108 + start_y))

    # Show up vector
    up = camera.upVector
    text = f'Up: {up.x:.2f}, {up.y:.2f}, {up.z:.2f}'
    pyScreen.blit(font.render(text, True, (255, 255, 255)), (start_x, 144 + start_y))

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

    
