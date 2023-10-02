from typing import Iterator
from ipaddress import IPv4Address
import logging
import time

import pytest

from peaktech.dmm_2025 import DMM
from rigol.dl3021 import DCLoad
from riden import Riden


@pytest.fixture(scope='module')
def rigol_dl3021(rigol_dl3021_factory) -> Iterator[DCLoad]:
    """Concrete instance of our dc load shared across multiple tests."""
    dl = rigol_dl3021_factory(IPv4Address('192.168.87.14'))
    yield dl
    dl.active = False


@pytest.fixture(scope='module')
def riden_6018(riden_6018_factory) -> Iterator[Riden]:
    """Concrete instance of our lab power supply shared across multiple tests."""
    r = riden_6018_factory('/dev/ttyUSB0')
    yield r
    r.set_output(False)


@pytest.mark.parametrize("input_voltage", [24, 36, 48])  # Volts
@pytest.mark.parametrize("input_amperage", [.5, 1.5, 3])  # Ampere
@pytest.mark.parametrize("dc_load", [.35, .5, 1, 3])  # Ohms
def test_dc_dc_converter_parametrized(
    peaktech_2025: DMM,
    rigol_dl3021: DCLoad,
    riden_6018: Riden,
    input_voltage: int,
    input_amperage: int,
    dc_load: int,
) -> None:
    dc_load_watts = 12 / (dc_load * dc_load)
    logging.info(
        f'Input Voltage: {input_voltage} V, Input Amperage: {input_amperage} A, DC Load: {dc_load_watts:.2f} W'
    )

    riden_6018.set_v_set(input_voltage)
    riden_6018.set_i_set(input_amperage)
    riden_6018.set_output(True)

    rigol_dl3021.resistance = dc_load
    rigol_dl3021.active = True

    time.sleep(5)

    measurement = peaktech_2025.read_measurement()
    logging.info(f'DMM: {measurement}')
    assert measurement.unit == "VDC", "DMM dial is not set to VDC"
    assert measurement.value < 13, "DC-DC converter output voltage outside expected range"
    if dc_load_watts <= input_amperage * input_amperage:
        assert measurement.value > 11, "DC-DC converter output voltage outside expected range"
