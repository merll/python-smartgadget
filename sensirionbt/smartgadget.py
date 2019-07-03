import logging
import struct

from .connection import BTLEConnection
from .constants import (SHT3X_TEMPERATURE_NOTIFICATIONS_UUID, SHT3X_HUMIDITY_NOTIFICATIONS_UUID,
                        BATTERY_LEVEL_CHARACTERISTIC_UUID, MANUFACTURER_NAME_CHARACTERISTIC_UUID,
                        MODEL_NUMBER_CHARACTERISTIC_UUID, FIRMWARE_REVISION_CHARACTERISTIC_UUID)


log = logging.getLogger(__name__)


def _get_value(c: BTLEConnection, uuid: str, sformat: str):
    raw = c.read_characteristic(uuid)
    val = struct.unpack(sformat, raw)[0]
    return val


def _get_str(c: BTLEConnection, uuid: str):
    return c.read_characteristic(uuid).decode('utf-8')


def _get_temperature(c: BTLEConnection):
    temperature = _get_value(c, SHT3X_TEMPERATURE_NOTIFICATIONS_UUID, '<f')
    log.debug('Temperature:   %.2f', temperature)
    return temperature


def _get_humidity(c: BTLEConnection):
    humidity = _get_value(c, SHT3X_HUMIDITY_NOTIFICATIONS_UUID, '<f')
    log.debug('Humidity:      %.2f', humidity)
    return humidity


def _get_battery_level(c: BTLEConnection):
    battery_level = _get_value(c, BATTERY_LEVEL_CHARACTERISTIC_UUID, 'b')
    log.debug('Battery level: %d', battery_level)
    return battery_level


class SmartGadget:
    def __init__(self, mac, connection_cls=BTLEConnection):
        self._initialized = False

        self._manufacturer = None
        self._model = None
        self._firmware_version = None

        self._conn = connection_cls(mac)

    def _read_id(self, c):
        self._manufacturer = _get_str(c, MANUFACTURER_NAME_CHARACTERISTIC_UUID)
        log.debug('Manufacturer:  %s', self._manufacturer)
        self._model = _get_str(c, MODEL_NUMBER_CHARACTERISTIC_UUID)
        log.debug('Model:         %s', self._model)
        self._firmware_version = _get_str(c, FIRMWARE_REVISION_CHARACTERISTIC_UUID)
        log.debug('Firmware:      %s', self._firmware_version)
        self._initialized = True

    def init(self):
        with self._conn as c:
            self._read_id(c)

    @property
    def manufacturer(self) -> str:
        if not self._initialized:
            self.init()
        return self._manufacturer

    @property
    def model(self) -> str:
        if not self._initialized:
            self.init()
        return self._model

    @property
    def firmware_version(self) -> str:
        if not self._initialized:
            self.init()
        return self._firmware_version

    def get_temperature(self) -> float:
        with self._conn as c:
            return _get_temperature(c)

    def get_humidity(self) -> float:
        with self._conn as c:
            return _get_humidity(c)

    def get_battery_level(self) -> int:
        with self._conn as c:
            return _get_battery_level(c)

    def get_values(self, init_static=False) -> dict:
        with self._conn as c:
            if not self._initialized and init_static:
                self._read_id(c)
            temperature = _get_temperature(c)
            humidity = _get_humidity(c)
            battery_level = _get_battery_level(c)
        return {
            'temperature': temperature,
            'humidity': humidity,
            'battery_level': battery_level,
        }
