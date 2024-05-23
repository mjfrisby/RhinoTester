A simple utility for testing various combinations of FFB effects with the VPforce Rhino FFB Joystick or other VPforce enabled DIY FFB devices.

Use:
To connect to a device, enter the USB PID value that is configured for the device and press connect (Rhino default is 2055)

To start a given effect:
- Enable the checkbox for the effect you want to start
- Configure the applicable settings for the effect
- Press the 'Start New Effects' button

To stop *all* effects, press the 'Stop All Effects' button

Periodic and Constant effect types can be layered on top of one another.  So you can, for example, start a periodic effect of 10hz with a direction of 0 degrees, and then change the settings to 15hz at 90 degrees and press the start effecs button again.
This would result in both effects playing at the same time.

Damper, Inertia, Friction and Spring are singular effects, meaning that only one instance of each effect exists at any given time. Changing the value of an effect and selecting "start new effects" changes the force of the existing effect, it does not create a new effect.

You may start a single effect type, or multiple types with a single click of "Start New Effects".

The axis position indicator also has a blue crosshair.  If you start a spring effect, you are able to drag the crosshair around the axis map with your mouse. Doing so will adjust the centerpoint offset of the spring effect in real time, which will result in the device mirroring the movement of the crosshairs.