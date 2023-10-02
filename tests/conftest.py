"""
The fixtures defined in this local pytest plugin allow for re-using
the instances of the classes representing our lab equipment across
different tests by defining a sceope.
"""

from ipaddress import IPv4Address
from typing import Callable, Dict, Iterator
import pytest

from peaktech.dmm_2025 import DMM
from rigol.dl3021 import DCLoad
from riden import Riden


@pytest.fixture(scope='session')
def peaktech_2025() -> Iterator[DMM]:
    try:
        dmm = DMM()
        measurement = dmm.read_measurement()
        if measurement.unit != 'VDC':
            pytest.fail(reason='DMM dial has not been set to VDC.')
        yield dmm
    except RuntimeError as exc:
        pytest.fail(reason=f'Problem constructing DMM: {exc}')


@pytest.fixture(scope='session')
def rigol_dl3021_factory() -> Iterator[Callable[[IPv4Address], DCLoad]]:

    digital_loads: Dict[IPv4Address, DCLoad] = {}

    def create_dl(ip: IPv4Address) -> DCLoad:
        if ip in digital_loads:
            return digital_loads[ip]
        load = DCLoad(ip)
        digital_loads[ip] = load
        return load

    yield create_dl


@pytest.fixture(scope='session')
def riden_6018_factory() -> Iterator[Callable[[str], Riden]]:

    ridens: Dict[str, Riden] = {}

    def create_riden(serial_port: str) -> Riden:
        if serial_port in ridens:
            return ridens[serial_port]
        psu = Riden(port=serial_port, baudrate=115200, address=1)
        ridens[serial_port] = psu
        return psu

    yield create_riden
