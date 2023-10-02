from dataclasses import dataclass
from typing import Optional
import logging
import sys

import pyudev


def find_dmm() -> Optional[str]:
    context = pyudev.Context()

    for device in context.list_devices(subsystem="hidraw"):
        usb_device = device.find_parent("usb", "usb_device")
        if usb_device == None:
            continue
        if usb_device.get("ID_VENDOR_ID") == "2571" and usb_device.get("ID_MODEL_ID") == "4100":
            if not device.device_node:
                raise ValueError('unknown device node')
            return device.device_node
    return None


def extract_value(frame: bytes) -> float:
    if frame[1] == 0x4C and frame[2] == 0x4F:
        value = float("inf")
    else:
        value = float((frame[1] >> 4) * 1000 + (frame[1] & 0xF) * 100 + (frame[2] >> 4) * 10 + (frame[2] & 0xF))
    if frame[0] & 1:
        value /= 1000
    elif frame[0] & 2:
        value /= 100
    elif frame[0] & 4:
        value /= 10
    if frame[0] & 0x40:
        value *= -1

    if frame[4] & 2:
        value *= 1e-9
    elif frame[5] & 0x10:
        value *= 1e6
    elif frame[5] & 0x20:
        value *= 1e3
    elif frame[5] & 0x40:
        value *= 1e-3
    elif frame[5] & 0x80:
        value *= 1e-6

    return value


def extract_unit(frame: bytes) -> str:
    unit = "unknown"
    if frame[5] & 0x04:  # (!) do not reorder, frame[6] & 0x80 will be set
        unit = "Vdiode"
    elif frame[6] & 0x80:
        unit = "V"
    elif frame[6] & 0x40:
        unit = "A"
    elif (frame[7] & 0x3D) == 0x3D:
        unit = "Ω"
    elif frame[6] & 1:
        unit = "°F"
    elif frame[6] & 2:
        unit = "°C"
    elif frame[6] & 4:
        unit = "F"
    elif frame[6] & 8:
        unit = "Hz"
    elif frame[6] & 0x10:
        unit = "hFE"

    if frame[3] & 0x08:
        unit += "AC"
    elif frame[3] & 0x10:
        unit += "DC"

    return unit


@dataclass
class Measurement:
    value: float
    unit: str

    def __repr__(self) -> str:
        return f'{self.value} {self.unit}'


class DMM:

    def __init__(self) -> None:
        dmm_path = find_dmm()
        if not dmm_path:
            raise RuntimeError('Could not find PeakTech 2025.')
        self.fd = open(dmm_path, 'rb')

    def __del__(self) -> None:
        if hasattr(self, 'fd') and not self.fd.closed:
            self.fd.close()

    def __read_frame(self) -> bytes:
        return self.fd.read(8)

    def read_measurement(self) -> Measurement:
        frame = self.__read_frame()
        return Measurement(extract_value(frame), extract_unit(frame))


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    try:
        dmm = DMM()

        for _ in range(5):
            measurement = dmm.read_measurement()
            logging.info(f'Measurement: {measurement}')

        return 0
    except RuntimeError as exc:
        logging.error(f"An error occurred: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
