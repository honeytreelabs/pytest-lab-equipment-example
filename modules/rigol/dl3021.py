from ipaddress import IPv4Address
import logging
import sys

import pyvisa


class DCLoad:

    def __init__(self, ip: IPv4Address) -> None:
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(f"TCPIP0::{ip}::INSTR")
        logging.info(self.inst.query("*IDN?"))

    @property
    def resistance(self) -> float:
        self.inst.write(":SOURCE:FUNCTION RESISTANCE")
        return float(self.inst.query(f":SOURCE:RESISTANCE:LEVEL:IMMEDIATE?").strip())

    @resistance.setter
    def resistance(self, value: float) -> None:
        # Set to constant resistance mode
        self.inst.write(":SOURCE:FUNCTION RESISTANCE")
        # Set to 3 Ohms
        self.inst.write(f":SOURCE:RESISTANCE:LEVEL:IMMEDIATE {value:.2f}")
        # Enable electronic load

    @property
    def active(self) -> bool:
        return int(self.inst.query(":SOURCE:INPUT:STATE?").strip()) == 1

    @active.setter
    def active(self, value: bool) -> None:
        value_str = "On" if value else "Off"
        self.inst.write(f":SOURCE:INPUT:STATE {value_str}")

    @property
    def voltage(self) -> float:
        return float(self.inst.query(":MEASURE:VOLTAGE?").strip())

    @property
    def current(self) -> float:
        return float(self.inst.query(":MEASURE:CURRENT?").strip())

    @property
    def power(self) -> float:
        return float(self.inst.query(":MEASURE:POWER?").strip())


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    try:
        dc_load = DCLoad(IPv4Address('192.168.87.14'))
        logging.info(f'DC Load is {"" if dc_load.active else "not "}active')
        dc_load.resistance = 3.0
        dc_load.active = True

        logging.info(f'DC Load is {"" if dc_load.active else "not "}active')
        logging.info(f'Voltage: {dc_load.voltage}')
        logging.info(f'Current: {dc_load.current}')
        logging.info(f'Power: {dc_load.power}')

        return 0
    except pyvisa.errors.VisaIOError as exc:
        logging.error(f"An error occurred: {exc}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
