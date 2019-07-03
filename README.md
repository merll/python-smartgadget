# Sensirion-SmartGadget

Python library for reading temperature, humidity, and battery level from
a SHT31 Smart Gadget Development Kit by Sensirion.

# Supported features

* Direct reading of SHT31 sensor values and device battery level.
* Subscription to notifications on value changes.
* Output of manufacturer, model name, and firmware version.

# Currently not supported

* Downloading data from the integrated data logger.
* Setup of data logger interval.

# Installation

```bash
pip install sensirion-smartgadget
```

# Usage

```python
from sensirionbt import SmartGadget

sensor = SmartGadget('CA:FE:12:34:56:78')
print(sensor.get_values(init_static=True))
# 'init_static' is optional; it fetches following values immediately.
print("Manufacturer:", sensor.manufacturer)
print("Model:", sensor.model)
print("Firmware:", sensor.firmware_version)
```

# Notes

* The device only allows one connection at a time. If the connection
keeps failing, make sure you have disconnected other services, e.g.
the smartphone app.
* On a connection failure, transmission will be re-attempted, depending
on the 'retries' argument or property. The default is to retry twice. 
* The first connection and value readings take a few seconds. The reason
for this is that characteristics are discovered by UUID, then handles
are cached and reused for subsequent calls.
