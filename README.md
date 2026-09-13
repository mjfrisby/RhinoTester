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

## Connecting

Pick a device from the list and press Connect. At startup the tester connects on its own if the device you used last time is plugged in, or if it finds only one device.

## Periodic and constant effects

Periodic and constant effects are additive, so any number can play at once.

1. Set up the effect with the Periodic or Constant controls: direction, intensity, and for a periodic effect the waveform, frequency, phase and duration. A duration of 0 plays until stopped.
2. Press Add Periodic to Queue or Add Constant to Queue. Repeat to build up a set.
3. Press Start Checked and Queued to start everything in the queue together.

The queue stays after you start it. Pressing Start again skips effects that are still playing and starts the ones that were stopped, have finished, or were added since.

To change an effect, select it in Queued Effects. Its settings load into the controls, and any change you make goes to the device straight away, even while the effect is playing. Changing the waveform restarts the effect. With nothing selected, or several entries selected, the controls only set up the next effect you add. Remove Selected and Clear Queue take entries out of the queue but leave playing effects running.

### Direction

The direction dial shows the value sent to the device: 0° forward (F), 90° right (R), 180° back (B) and 270° left (L). Click or drag to point it, and hold Shift to snap to 15°. The mouse wheel and arrow keys change it by 1°, Page Up and Page Down by 15°, and Home returns it to 0°.

## Damper, inertia, friction and spring

These are singular effects, so only one of each exists at a time. Tick the effect, set its intensity, and press Start Checked and Queued. Starting it again updates the existing effect.

Override applies to VPforce devices only. It starts a spring that external DirectInput commands cannot override.

## Axis view

The grid shows the stick's X and Y travel, with up on the grid as forward. The center lines mark the axis center and the edges mark full deflection.

The red crosshair follows the stick's actual position. Once a device is connected, the tester reads it about every 10 ms, so the crosshair moves as you move the stick or as an effect pushes it.

The blue crosshair is the spring's center point. It only responds while a spring is running: click or drag anywhere on the grid to move the center, and the device pulls the stick toward it in real time. When the spring stops, the blue crosshair stays where you left it, and the next spring you start is centered there.

## Active effects

Every running effect is listed under Active Effects with its own Stop button. Stop All Effects stops and frees everything.

## View menu

Log (Ctrl+L) shows everything the tester has logged since it started, including errors. You can filter it by level, copy the text, save it to a file, or clear it.

Theme switches between System, Light and Dark. `--darkmode` and `--lightmode` on the command line override the saved choice for that run.

The theme and the last connected device are saved under `HKEY_CURRENT_USER\Software\VPforce\RhinoTester`.

## Use with care

The device *will* do what you tell it to, as fast as you tell it to. Dragging the spring center point is where this bites: the stick tries to move as quickly as you drag the crosshair. Abusing this may cause unintended W-F or damage to the device.

Use at your own discretion.
