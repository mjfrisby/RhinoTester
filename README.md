# Rhino Tester

A utility for trying out force feedback effects, alone or in combination, on a VPforce Rhino or other VPforce-based DIY FFB device. With DirectLink installed it also drives generic DirectInput FFB devices, such as a Microsoft SideWinder Force Feedback 2.

## Running it

`Rhino Tester.exe` is a single file with nothing to install.

To run from source you need Python 3.12 or later and the packages in `requirements.txt`:

    pip install -r requirements.txt
    python "Rhino Tester.py"

To build the exe, run `python -m PyInstaller "Rhino Tester.spec"`. Pointing PyInstaller at `Rhino Tester.py` instead overwrites the spec with a generic one.

## DirectInput devices

Install DirectLink from https://directlink.flyfrisby.com with its installer. The tester loads DirectLink from the location the installer records, and DirectInput FFB devices then appear in the device list with a [DI] prefix. Without DirectLink, only VPforce devices are listed.

## The window

The effect controls are on the left: Periodic, Constant force and Singular effects. The axis view is in the middle. The queue and the running effects are on the right, with Start Checked and Queued under the queue and Stop All Effects at the bottom.

## Connecting

Pick a device from the list at the top and press Connect. At startup the tester connects on its own if the device you used last time is plugged in, or if it finds only one device.

## Periodic and constant effects

Periodic and constant effects are additive, so any number can play at once.

1. Set up the effect in the Periodic or Constant force box: direction, intensity, and for a periodic effect the waveform, frequency, phase and duration. A duration of 0 plays until stopped.
2. Press Add to Queue in that box. Repeat to build up a set.
3. Press Start Checked and Queued, under the queue, to start everything in it together.

The queue stays after you start it. Pressing Start again skips effects that are still playing and starts the ones that were stopped, have finished, or were added since.

To change an effect, select it in Queued effects. Its settings load into the controls, the box you are editing says so, and any change you make goes to the device straight away, even while the effect is playing. Changing the waveform restarts the effect. With nothing selected, or several entries selected, the controls only set up the next effect you add. Remove Selected and Clear Queue take entries out of the queue but leave playing effects running.

### Direction

The direction dial shows the value sent to the device, drawn where it pushes the stick: 0° back (B), 90° left (L), 180° forward (F) and 270° right (R). Click or drag to point it, and hold Shift to snap to 15°. The mouse wheel and arrow keys change it by 1°, Page Up and Page Down by 15°, and Home returns it to 0°.

## Damper, inertia, friction and spring

Each of these has its own box with a short description of what it does. Only one of each exists at a time, so starting one again updates it rather than adding a second.

Press the box's own Start button to run that effect on its own, whatever its Include checkbox says. Include is for starting several at once: Start Checked and Queued runs every included effect along with the queue.

Moving an intensity slider while the effect is playing sends the new value to the device straight away.

Override applies to VPforce devices only. It starts a spring that external DirectInput commands cannot override.

### Force trim release

While a spring is running, holding a button on the device releases it. The spring stops, so the stick is free to move, and when you let the button go the spring starts again centered where the stick is.

Buttons already held when the spring started are ignored, so a multi-position lever resting in one of its positions does not trigger it. Moving such a lever to a different position while the spring runs does look like a button press, because its new position was not held when the spring started. Press Start again to record what is held now.

## Axis view

The grid shows the stick's X and Y travel, with up on the grid as forward. The center lines mark the axis center and the edges mark full deflection.

The red crosshair follows the stick's actual position. Once a device is connected, the tester reads it about every 10 ms, so the crosshair moves as you move the stick or as an effect pushes it.

The other crosshair is the spring's center point. It is blue and can be dragged while a spring is running, and grey when there is no spring to move. Click or drag anywhere on the grid to move the center, and the device pulls the stick toward it in real time. A force trim release moves it too. When the spring stops, the crosshair stays where you left it, and the next spring you start is centered there.

### Device

The box below the axis view reads the same input reports about 20 times a second:

- **Position** is the stick's X and Y, the numbers behind the red crosshair.
- **Center** is the spring center the device reports, and shows a dash when no spring is running.
- **Centering error** is how far the stick sits from that center on each axis, as a percentage of full travel, so 0% is dead on the center.
- **Buttons** and **Hats** list whatever is pressed.
- **Force out** is the force the device reports it is applying. It only appears on VPforce devices; DirectInput devices do not report it.

## Active effects

Every running effect is listed under Active effects with its own Stop button. Stop All Effects stops and frees everything.

## Device menu

Reset All Effects frees every effect the device is holding, including any the tester did not create, such as leftovers from a program that was killed. It asks first, because it also clears effects other software owns.

The tester frees its own effects when it closes, so this is for clearing up after something else.

## View menu

Log (Ctrl+L) shows everything the tester has logged since it started, including errors. You can filter it by level, copy the text, save it to a file, or clear it.

Theme switches between System, Light and Dark. `--darkmode` and `--lightmode` on the command line override the saved choice for that run.

The theme and the last connected device are saved under `HKEY_CURRENT_USER\Software\VPforce\RhinoTester`.

## Use with care

The device *will* do what you tell it to, as fast as you tell it to. Dragging the spring center point is where this bites: the stick tries to move as quickly as you drag the crosshair. A constant force is the other one to watch, since it starts pushing the moment it does and keeps pushing until you stop it. Abusing either may cause unintended W-F or damage to the device.

Use at your own discretion.
