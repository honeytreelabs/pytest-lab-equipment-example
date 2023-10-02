import logging

from peaktech.dmm_2025 import DMM


def test_dmm(peaktech_2025: DMM) -> None:
    measurement = peaktech_2025.read_measurement()

    logging.info(f'Measurement: {measurement}')

    assert measurement.value >= 0, "actual value must be greater than zero"
    assert measurement.unit == "VDC", "only volts DC are supported by this test"
