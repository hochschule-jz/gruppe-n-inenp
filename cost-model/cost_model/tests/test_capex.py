from cost_model.capex import capex_for, controllers_for
from cost_model.config import Capex

C = Capex(
    sensor_eur=2.0,
    wiring_eur_per_spot=3.0,
    install_eur_per_spot=10.0,
    sensors_per_controller=16,
    controller_eur=15.0,
    network_fixed_eur=1000.0,
    cloud_setup_eur=2000.0,
)


def test_controllers_stepwise():
    assert controllers_for(16, 16) == 1
    assert controllers_for(17, 16) == 2
    assert controllers_for(200, 16) == 13  # ceil(200/16)


def test_total_is_sum_of_parts():
    b = capex_for(200, C)
    assert b.total == (b.sensors + b.wiring + b.install + b.controllers + b.network_fixed + b.cloud_setup)


def test_per_spot_components_scale_linearly():
    b1 = capex_for(200, C)
    b2 = capex_for(400, C)
    assert b2.sensors == 2 * b1.sensors
    assert b2.wiring == 2 * b1.wiring
    assert b2.network_fixed == b1.network_fixed  # fixed, does not scale
