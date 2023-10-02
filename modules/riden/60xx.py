"""The Riden class of the riden package can be used as-is. Therefore,
this module only contains a small usage example."""

import logging
import sys
import time

from riden import Riden
import serial


def main(serial_port: str) -> int:
    logging.basicConfig(level=logging.INFO)

    try:
        r = Riden(port=serial_port, baudrate=115200, address=1)
        logging.info(f'Serial Number: {r.get_sn()}')
        logging.info(f'Firmware: {r.get_fw()}')
        r.set_output(True)
        for voltage in [24, 36, 48, 60]:
            for amperage in [0.3, 0.5, 1]:
                logging.info(f'Current voltage setting: {r.get_v_set()}')
                logging.info(f'Current amperage setting: {r.get_i_set()}')
                r.set_v_set(voltage)
                r.set_i_set(amperage)

                r.update()
                logging.info(f'New voltage: {r.v_set}')
                logging.info(f'New amperage: {r.i_set}')
        time.sleep(1)
        r.set_output(False)
        return 0
    except (FileNotFoundError, serial.SerialException):
        logging.error(f'Could not open {serial_port}. Device connected?')
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'))
