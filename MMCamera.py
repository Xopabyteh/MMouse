import math
from .lib import fusionAddInUtils as futil
import adsk.core, adsk.fusion, adsk.cam

class MMCamera:
    def __init__(self, viewport: adsk.core.Viewport):
        self.viewport = viewport
        self.upVector = adsk.core.Vector3D.create(0, 0, 1)

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
        return self.virtualTargetForward.crossProduct(self.upVector)

    # Sets the other cameras eye to this cameras eye
    # Sets the other cameras target to this cameras target (camera.eye + virtualTargetOffset)
    def apply_to_camera(self, otherCamera: adsk.core.Camera):
        otherCamera.eye = self.virtualEye.asPoint()
        otherCamera.target = self.calc_absolute_target().asPoint()
        otherCamera.upVector = self.upVector
    
    def pan_by(self, x: float, z: float):
        # Move the virtual eye in it's local directions by the movementAxis
        vRight = self.calc_virtual_cam_right()
        vUp = self.upVector.copy()

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
        def rotation_matrix(axis, theta):
            axis = axis.copy()
            axis.normalize()
            a = math.cos(theta / 2.0)
            b, c, d = -axis.x * math.sin(theta / 2.0), -axis.y * math.sin(theta / 2.0), -axis.z * math.sin(theta / 2.0)
            return [
                [a*a + b*b - c*c - d*d, 2*(b*c - a*d), 2*(b*d + a*c)],
                [2*(b*c + a*d), a*a + c*c - b*b - d*d, 2*(c*d - a*b)],
                [2*(b*d - a*c), 2*(c*d + a*b), a*a + d*d - b*b - c*c]
            ]
        
        def apply_rotation(vector, rot_matrix):
            x = vector.x * rot_matrix[0][0] + vector.y * rot_matrix[0][1] + vector.z * rot_matrix[0][2]
            y = vector.x * rot_matrix[1][0] + vector.y * rot_matrix[1][1] + vector.z * rot_matrix[1][2]
            z = vector.x * rot_matrix[2][0] + vector.y * rot_matrix[2][1] + vector.z * rot_matrix[2][2]
            return adsk.core.Vector3D.create(x, y, z)
        
        # Rotate around the x-axis (pitch)
        rightVector = self.calc_virtual_cam_right()
        rot_matrix = rotation_matrix(rightVector, xAxisRad)
        self.virtualTargetForward = apply_rotation(self.virtualTargetForward, rot_matrix)
        self.upVector = apply_rotation(self.upVector, rot_matrix)

        # Rotate around the y-axis (yaw)
        rot_matrix = rotation_matrix(self.upVector, yAxisRad)
        self.virtualTargetForward = apply_rotation(self.virtualTargetForward, rot_matrix)

        # Rotate around the z-axis (roll)
        rot_matrix = rotation_matrix(self.virtualTargetForward, zAxisRad)
        self.upVector = apply_rotation(self.upVector, rot_matrix)
        rightVector = apply_rotation(rightVector, rot_matrix) # Recalculate right vector for consistency

        # Normalize vectors after transformations
        self.virtualTargetForward.normalize()
        self.upVector.normalize()
        rightVector.normalize()