# Use a supported Linkam heater

There are two Linkam sample heaters already configured for use 
with the USAXS instrument and bluesky.  Talk with the instrument 
scientist to verify the heater you wish to use is in operation.

Device | Controller type | EPICS PV prefix
--- | --- | ---
`linkam_ci94` | Linkam_CI94 (the old one) | `9idcLAX:ci94:`
`linkam_tc1`  | Linkam_T96 | `9idcLINKAM:tc1:`

While the basic controls are the same for either controller type,
the additional features are different.  Consult the 
[source code](/profile_bluesky/startup/10-devices.py)
if you need more information.  Search for the controller type 
by name in that file.

## Basic Controls

The basic controls (derived from 
[`apstools.devices.PVPositionerSoftDoneWithStop`](https://bcda-aps.github.io/apstools/api/_devices.html#apstools.devices.positioner_soft_done.PVPositionerSoftDoneWithStop))
are described in the table below.  Temperature is in degrees C.

### Basic features

description | object
------ | ------
Measured temperature | `linkam.temperature.position` (same as `linkam.temperature.readback.get()`)
Desired temperature | `linkam.temperature.setpoint`
Ramp rate (degrees C/min) | `linkam.temperature.setpoint`
Done moving? | `linkam.temperature.done`  (See `.inposition` below)
_In position_ (at temperature) tolerance | `linkam.temperature.tolerance`

Controller is deemed _in position_ when:

    abs(readback - setpoint) <= tolerance

In the examples below, use either `linkam = linkam_tc1`
or `linkam = linkam_ci94`.

There's a difference when _setting_ on object on the ipython
command line setting the object in a bluesky plan.  In a plan, we are instructing the bluesky `RunEngine` what to do, so the command is different.

When _reading_ an object, the command is the same for both command line and plan use.

### Controls Examples

description | example
------ | ------
Linkam at desired temperature? | `linkam.temperature.inposition` (True or False)
Set the controller to 85 C (plan) and wait for `.inposition` | `yield from bps.mv(linkam.temperature, 85)`
Set the controller to 85 C (plan), do NOT wait | `yield from bps.mv(linkam.temperature.setpoint, 85)`
Change the _in position_ tolerance (plan) | `yield from bps.mv(linkam.temperature.tolerance, 1.0)`
Change the ramp rate (plan) | `yield from bps.mv(linkam.temperature.ramp, 20)`
Set the controller to 85 C (command line) and wait for `.inposition` | `linkam.temperature.move(85)`
Set the controller to 85 C (command line), do NOT wait | `linkam.temperature.setpoint.put(85)`
Change the _in position_ tolerance (command line) | `linkam.temperature.tolerance.put(1.0)`
Change the ramp rate (command line) | `linkam.temperature.ramp.put(20)`

## Example plan

This example defines a (bluesky) plan to measure USAXS/SAXS/WAXS 
at a sequence of temperatures.  Place this example code in a python 
file named `tseq.py` in your current working directory.

```python
"""Temperature sequence"""

def my_temperature_sequence(sx, sy, thickness, sample_name, t_start, t_end, t_step, md={}):
    summary = "USAXS/SAXS/WAXS temperature sequence"
    archive = instrument_archive(summary)

    md = {
        "summary": summary, 
        "archive": archive,
        "temperature_start": t_start,
        "temperature_end": t_end,
        "temperature_step": t_step,
    }
    yield from bps.mv(linkam.temperature.ramp, 100)  # degrees C/minute

    sign = 1            # assume ascending temperature
    if t_end < t_start:
        sign = -1        # Aha! Descending temperature
    t_lo = min(t_start, t_end)
    t_hi = max(t_start, t_end)
    temperature = t_start  # degrees C

    while t_lo <= temperature <= t_hi:
        t0 = time.time()
        md["temperature_set_point"] = temperature
        yield from bps.mv(linkam.temperature, temperature)
        print(f"Reached {temperature:.1f}C in {time.time() - t0:.3f}s")
        md["temperature_settling_time"] = time.time() - t0
        
        md["temperature_actual"] = linkam.temperature.position
        yield from FlyScan(sx, sy, thickness, sample_name, md=md)
        
        md["temperature_actual"] = linkam.temperature.position
        yield from SAXS(sx, sy, thickness, sample_name, md=md)
        
        md["temperature_actual"] = linkam.temperature.position
        yield from WAXS(sx, sy, thickness, sample_name, md=md)
        
        print(
            "All scans complete"
            f" at {linkam.temperature.position:.1f}C"
            f" in {time.time() - t0:.3f}s"
        )
        temperature += sign * abs(t_step)
```

## Load your python code

Load your code into the bluesky (ipython) session 
with: `%run -i tseq.py`

Be sure to use the percent sign and the `-i` terms as they are 
important to your code working with the other instrument components.

TIP: Any time you edit your python file, you can reload it 
using the same command:  `%run -i tseq.py`

### Test

Test this plan with: `summarize_plan(my_temperature_sequence(10, 20, 0.85, "PS bar", 50, 80, 5))`

Note:  Use your own values for sample and temperature values.

### Run

Run this plan with: `RE(my_temperature_sequence(10, 20, 0.85, "PS bar", 50, 80, 5))`
