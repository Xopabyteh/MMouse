# Assuming you have not changed the general structure of the template no modification is needed in this file.
from .MMCamera import *
from .MMDebugWindow import *
import adsk.core, adsk.fusion
import pygame


class MMDebugWindow:
    def __init__(self):
        pygame.display.init()
        pygame.self.font.init()
        self.pyScreen = pygame.display.set_mode((800, 480))
        self.font = pygame.self.font.self.font(None, 36)
    
    def show_debug(self, joystickAxis, mmCamera, viewport):
        self.pyScreen.fill((0, 0, 0))
        self.display_joystick_axis(joystickAxis, 0, 0)
        self.display_mm_camera(mmCamera, 300, 0)
        self.dispaly_camera(viewport.camera, 0, 300)
        pygame.display.flip()

    def display_joystick_axis(self, joystickAxis: list[float], start_x: int, start_y: int):
        # Show header
        self.pyScreen.blit(self.font.render('Joystick axis', True, (255, 255, 255)), (start_x, start_y))

        # Show axis
        axis_labels = ['x', 'y', 'z', 'rx', 'ry', 'rz']
        for index, label in enumerate(axis_labels):
            value = joystickAxis[index]
            text = f'{label}: {value:.2f}'
            self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, index * 36 + 40 + start_y))

    def display_mm_camera(self, mmCamera: MMCamera, start_x: int, start_y: int):
        # Show header
        self.pyScreen.blit(self.font.render('MMCamera', True, (255, 255, 255)), (start_x, start_y))

        # Show camera eye
        eye = mmCamera.virtualEye
        text = f'V Eye: {eye.x:.2f}, {eye.y:.2f}, {eye.z:.2f}'
        self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 36 + start_y))

        # Show virtual target direction
        vtOffset = mmCamera.virtualTargetForward
        text = f'VT forward: {vtOffset.x:.2f}, {vtOffset.y:.2f}, {vtOffset.z:.2f}'
        self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 72 + start_y))

        # Show virtual camera forward length
        virtualCamForward = mmCamera.forwardEyeToTargetLength
        text = f'VT fw length: {virtualCamForward:.2f}'
        self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 108 + start_y))

        # Show absolute virtual target
        absoluteTarget = mmCamera.calc_absolute_target()
        text = f'VT Absolute: {absoluteTarget.x:.2f}, {absoluteTarget.y:.2f}, {absoluteTarget.z:.2f}'
        self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 142 + start_y))

        # Show up vector
        up = mmCamera.upVector
        text = f'Up: {up.x:.2f}, {up.y:.2f}, {up.z:.2f}'
        self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 178 + start_y))


    def dispaly_camera(self, camera: adsk.core.Camera, start_x: int, start_y: int):
        # Show header
        self.pyScreen.blit(self.font.render('Camera', True, (255, 255, 255)), (start_x, start_y))

        # Show eye
        eye = camera.eye
        text = f'Eye: {eye.x:.2f}, {eye.y:.2f}, {eye.z:.2f}'
        self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 36 + start_y))

        # Show target
        target = camera.target
        text = f'Target: {target.x:.2f}, {target.y:.2f}, {target.z:.2f}'
        self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 72 + start_y))

        # Show extents (tuple bool float float)
        # or perspective angle (depending on camera type)
        if camera.cameraType == adsk.core.CameraTypes.PerspectiveCameraType:
            text = f'Perspective angle: {camera.perspectiveAngle:.2f}'
            self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 108 + start_y))
        else:
            extents = camera.getExtents()
            text = f'Extents: {extents[0]}, {extents[1]:.2f}, {extents[2]:.2f}'
            self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 108 + start_y))

        # Show up vector
        up = camera.upVector
        text = f'Up: {up.x:.2f}, {up.y:.2f}, {up.z:.2f}'
        self.pyScreen.blit(self.font.render(text, True, (255, 255, 255)), (start_x, 144 + start_y))

