from .lib import fusionAddInUtils as futil
import adsk.core, adsk.fusion, adsk.cam

class MMCamera:
    def __init__(self, viewport: adsk.core.Viewport):
        self.viewport = viewport

        # Create a virtual target infront of the camear
        cameraPos = viewport.camera.eye
        cameraTarget = viewport.camera.target
        posToTarget = cameraPos.vectorTo(cameraTarget)

        self.forwardEyeToTargetLength = posToTarget.length

        posToTarget.normalize()

        # Where is the virtual target relative to the camera.eye
        self.virtualTargetForward = posToTarget
        self.virtualEye = cameraPos.asVector()

        futil.log('MMCamera created')    
    
    def calc_absolute_target(self):
        # Eye + virtualTargetDirection * forwardEyeToTargetLength
        multipliedDirection = self.virtualTargetForward.copy()
        multipliedDirection.scaleBy(self.forwardEyeToTargetLength)

        absoluteTarget = self.virtualEye.copy()
        absoluteTarget.add(multipliedDirection)

        return absoluteTarget

    def calc_virtual_cam_right(self):
        return self.virtualTargetForward.crossProduct(adsk.core.Vector3D.create(0, 0, 1))

    def calc_virtual_cam_up(self, right: adsk.core.Vector3D):
        return right.crossProduct(self.virtualTargetForward)
        
    # Sets the other cameras eye to this cameras eye
    # Sets the other cameras target to this cameras target (camera.eye + virtualTargetOffset)
    def apply_to_camera(self, otherCamera: adsk.core.Camera):
        otherCamera.eye = self.virtualEye.asPoint()
        otherCamera.target = self.calc_absolute_target().asPoint()

    
    def pan_by(self, x: float, z: float):
        # Move the virtual eye in it's local directions by the movementAxis
        vRight = self.calc_virtual_cam_right()
        vUp = self.calc_virtual_cam_up(vRight)

        vRight.scaleBy(x)
        vUp.scaleBy(z)

        self.virtualEye.add(vRight)
        self.virtualEye.add(vUp)

    def zoom_by(self, y: float):
        pass
        # Increase distance from eye to target
        # and move the virtual camera backwards
        self.forwardEyeToTargetLength += y
        
        translationVector = self.virtualTargetForward.copy()
        translationVector.scaleBy(-y)
        self.virtualEye.add(translationVector)

    def rotate_by(self, xAxisRad: float, yAxisRad: float, zAxisRad: float):
      pass