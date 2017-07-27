import asyncio
import xknx
import voluptuous as vol

from custom_components.xknx import DATA_XKNX, XKNXSensor

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv

CONF_ADDRESS = 'address'
CONF_VALUE_TYPE = 'value_type'

DEFAULT_NAME = 'XKNX Sensor'
DEPENDENCIES = ['xknx']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ADDRESS): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_VALUE_TYPE): cv.string,
})

@asyncio.coroutine
def async_setup_platform(hass, config, add_devices, \
        discovery_info=None):
    """Setup the XKNX light platform."""
    if DATA_XKNX not in hass.data \
            or not hass.data[DATA_XKNX].initialized:
        return False

    if discovery_info is not None:
        yield from add_devices_from_component(hass, add_devices)
    else:
        yield from add_devices_from_platform(hass, config, add_devices)

    return True

@asyncio.coroutine
def add_devices_from_component(hass, add_devices):
    entities = []
    for device in hass.data[DATA_XKNX].xknx.devices:
        if isinstance(device, xknx.Sensor) and \
				not hasattr(device, "already_added_to_hass"):
            entities.append(XKNXSensor(hass, device))
    add_devices(entities)

@asyncio.coroutine
def add_devices_from_platform(hass, config, add_devices):
    from xknx import Sensor
    sensor = Sensor(hass.data[DATA_XKNX].xknx,
                    name= \
                        config.get(CONF_NAME),
                    group_address= \
                        config.get(CONF_ADDRESS),
                    value_type= \
                        config.get(CONF_VALUE_TYPE))
    sensor.already_added_to_hass = True
    hass.data[DATA_XKNX].xknx.devices.add(sensor)
    add_devices([XKNXSensor(hass, sensor)])