## MaMoth Mouse
### Installation
1. This add-in requires `pygame` to be installed: locate your FUSION 360 python distribution. This will be in folder `%localappdata%/AutoDesk/webdeploy/production/(random shit string)/Python/python.exe`

> For a user called "xoapb" the example command would be `C:/Users/xopab/AppData/Local/Autodesk/webdeploy/production/c4a5520f9bb0f0174c02662af8bd1ab67cee6298/Python/python.exe -m pip install pygame`

2. Add add-in to your addins folder
3. 😎

### Running
1. Make sure MaMoth mouse is plugged in
2. Run the add-in
> If the mouse isn't plugged in when the add-in is launched, you will have to relaunch.

### Configuration
Upon first launch a `mm_runtime_settings.ini` file is created inside the add-in folder.
Here is what each value means:
```ini
[Joystick] <-- Values in this section control which joystick (MMouse) axisId controls which camera axis
x = 0    
y = 2
z = 4
rx = 5
ry = 7
rz = 6

[Deadzones] <- Change lower deadzones of the joystick
x = 0.36
y = 0.36
z = 0.36
rx = 0.36
ry = 0.36
rz = 0.36

[UpperLimits] <- Change upper limits of the joystick
x = 0.9
y = 0.9
z = 0.9
rx = 0.9
ry = 0.9
rz = 0.9

[CameraSpeeds]
pan = 10    <-- Up/down, left/right speed
zoom = 10    <--- Forward/backward speed
rotation = 1    <--- Rotation speed
zoom_dependend_dampening = 0.5  <--- When zoomed in, the camera gets slower. The higher this number, the more it will slow down. Range of this param is (0-1)
x = 1  <--- "x" to "rz" are individual axis speeds for granular control (doesnt make much sense for others than the rotation ones tho...)
y = 1
z = 1
rx = 1
ry = 1
rz = 1
```
> When changing settings, you will have to relaunch the add-in in order for the settings to refresh.
