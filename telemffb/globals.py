"""Stand-in for TelemFFB's application globals.

The vendored hardware modules import ``telemffb.globals`` for a few
optional values - the device role, the system settings store, and the
minimum DirectLink version - and read each one through ``getattr`` with a
default.  The tester has no settings store and no device role, so leaving
them undefined selects the defaults: the joystick role, the device's
native X/Y axes, and no minimum DirectLink version.

Keep this module free of those names unless the tester gains a real
equivalent; defining one here changes how the hardware layer behaves.
"""
