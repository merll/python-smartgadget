import codecs
import logging

from bluepy import btle

from .constants import NOTIFICATION_DESCRIPTOR_UUID, NOTIFICATION_ON, NOTIFICATION_OFF

DEFAULT_TIMEOUT = 1

log = logging.getLogger(__name__)


class InvalidHandleError(Exception):
    pass


class BTLEConnection(btle.DefaultDelegate):
    _char_handles = {}
    _notify_handles = {}

    def __init__(self, mac, retries=2):
        super().__init__()
        self._conn = None
        self._mac = mac
        self._callbacks = {}
        self._retries = retries

    def __enter__(self):
        self._conn = btle.Peripheral()
        self._conn.setDelegate(self)
        log.debug("Trying to connect to %s", self._mac)
        self._try(self._conn.connect, self._mac, btle.ADDR_TYPE_RANDOM)
        log.debug("Connected to %s", self._mac)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.disconnect()
            self._conn = None

    def _try(self, fun: callable, *args, **kwargs):
        attempt = 0
        while True:
            attempt += 1
            try:
                return fun(*args, **kwargs)
            except btle.BTLEException as ex:
                log.debug("Unable to send request to the device %s: %s", self._mac, ex)
                if attempt <= self._retries:
                    log.debug("Retrying.")
                else:
                    raise ex

    def _get_char_handle(self, uuid):
        char_handles = self.__class__._char_handles
        handle = char_handles.get(uuid)
        if handle is None:
            try:
                c = self._try(self._conn.getCharacteristics, uuid=uuid)[0]
            except IndexError:
                raise InvalidHandleError("No characteristic found for UUID {}.".format(uuid))
            char_handles[uuid] = handle = c.getHandle()
        return handle

    def _get_notify_handle(self, uuid):
        notify_handles = self.__class__._notify_handles
        handle = notify_handles.get(uuid)
        if handle is None:
            ch = self._get_char_handle(uuid)
            try:
                c = self._try(self._conn.getCharacteristics, ch, ch)[0]
            except IndexError:
                raise InvalidHandleError("No characteristic found for UUID {}.".format(uuid))
            try:
                descriptor = self._try(c.getDescriptors, NOTIFICATION_DESCRIPTOR_UUID)[0]
            except IndexError:
                raise InvalidHandleError("No notification descriptor found for UUID {}.".format(uuid))
            notify_handles[uuid] = handle = descriptor.handle
        return handle

    def handleNotification(self, handle, data):
        log.debug("Got notification from %s: %s", handle, codecs.encode(data, 'hex'))
        callback = self._callbacks.get(handle)
        if callable(callback):
            callback(data)

    def set_callback(self, handle, function):
        self._callbacks[handle] = function

    def remove_callback(self, handle):
        del self._callbacks[handle]

    @property
    def mac(self):
        return self._mac

    @property
    def retries(self):
        return self._retries

    @retries.setter
    def retries(self, value):
        self._retries = value

    def subscribe_characteristic(self, uuid):
        handle = self._get_notify_handle(uuid)
        self._try(self._conn.writeCharacteristic, handle, NOTIFICATION_ON)
        return handle

    def unsubscribe_characteristic(self, uuid):
        handle = self._get_notify_handle(uuid)
        self._try(self._conn.writeCharacteristic, handle, NOTIFICATION_OFF)
        return handle

    def read_characteristic(self, uuid):
        handle = self._get_char_handle(uuid)
        return self._try(self._conn.readCharacteristic, handle)
