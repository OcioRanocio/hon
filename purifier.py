from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)


import logging
from datetime import timedelta
from .const import DOMAIN, PURIFIER_MODE, PURIFIER_VOC_VALUE


_LOGGER = logging.getLogger(__name__)


class HonPurifierCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, hon, appliance):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="hOn Air Purifier",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self._hon = hon
        self._mac = appliance["macAddress"]
        self._type_name = appliance["applianceTypeName"]

    async def _async_update_data(self):
        return await self._hon.async_get_state(self._mac, self._type_name)


class HonPurifierEntity(CoordinatorEntity):
    def __init__(self, hass, entry, coordinator, appliance) -> None:
        super().__init__(coordinator)

        self._hon = hass.data[DOMAIN][entry.unique_id]
        self._hass = hass
        self._brand = appliance["brand"]

        if "nickName" in appliance:
            self._name = appliance["nickName"]
        else:
            self._name = "AirPurifier"

        self._mac = appliance["macAddress"]
        self._connectivity = appliance["connectivity"]
        self._model = appliance["modelName"]
        self._series = appliance["series"]
        self._model_id = appliance["applianceModelId"]
        self._type_name = appliance["applianceTypeName"]
        self._serial_number = appliance["serialNumber"]
        self._fw_version = appliance["fwVersion"]

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._mac)
            },
            "name": self._name,
            "manufacturer": self._brand,
            "model": self._model,
            "sw_version": self._fw_version,
        }

class HonPurifierMode(SensorEntity, HonPurifierEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(hass, entry, coordinator, appliance)

        self._coordinator = coordinator
        self._attr_unique_id = f"{self._mac}_machine_mode"
        self._attr_name = f"{self._name} Machine Mode"
        self._attr_icon = "mdi:air-filter"

    @callback
    def _handle_coordinator_update(self):

        # Get state from the cloud
        json = self._coordinator.data

        # No data returned by the Get State method (unauthorized...)
        if json is False:
            return

        mode = json["machMode"]["parNewVal"]

        if mode in PURIFIER_MODE:
            self._attr_native_value = PURIFIER_MODE[mode]
        else:
            self._attr_native_value = f"Unknown mode {mode}"

        self.async_write_ha_state()
        
class HonPurifierOnOff(BinarySensorEntity, HonPurifierEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(hass, entry, coordinator, appliance)

        self._coordinator = coordinator
        self._attr_unique_id = f"{self._mac}_on_off"
        self._attr_name = f"{self._name}"
        self._attr_device_class = BinarySensorDeviceClass.POWER
        self._attr_icon = "mdi:air-filter"

    @callback
    def _handle_coordinator_update(self):

        # Get state from the cloud
        json = self._coordinator.data

        # No data returned by the Get State method (unauthorized...)
        if json is False:
            return

        self._attr_is_on = json["onOffStatus"]["parNewVal"] == "1"
        self.async_write_ha_state()
        
class HonPurifierIndoorPM2p5(SensorEntity, HonPurifierEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(hass, entry, coordinator, appliance)

        self._coordinator = coordinator
        self._attr_unique_id = f"{self._mac}_indoor_pm2p5"
        self._attr_name = f"{self._name} Indoor PM 2.5"
        self._attr_device_class = SensorDeviceClass.PM25
        self._attr_icon = "mdi:air-filter"

    @callback
    def _handle_coordinator_update(self):

        # Get state from the cloud
        json = self._coordinator.data

        # No data returned by the Get State method (unauthorized...)
        if json is False:
            return

        self._attr_native_value = json["pm2p5ValueIndoor"]["parNewVal"]
        self.async_write_ha_state()
        
class HonPurifierIndoorPM10(SensorEntity, HonPurifierEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(hass, entry, coordinator, appliance)

        self._coordinator = coordinator
        self._attr_unique_id = f"{self._mac}_indoor_pm10"
        self._attr_name = f"{self._name} Indoor PM 10"
        self._attr_device_class = SensorDeviceClass.PM10
        self._attr_icon = "mdi:air-filter"

    @callback
    def _handle_coordinator_update(self):

        # Get state from the cloud
        json = self._coordinator.data

        # No data returned by the Get State method (unauthorized...)
        if json is False:
            return

        self._attr_native_value = json["pm10ValueIndoor"]["parNewVal"]
        self.async_write_ha_state()
        
class HonPurifierIndoorVOC(SensorEntity, HonPurifierEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(hass, entry, coordinator, appliance)

        self._coordinator = coordinator
        self._attr_unique_id = f"{self._mac}_indoor_VOC"
        self._attr_name = f"{self._name} Indoor VOC"
        self._attr_icon = "mdi:air-filter"

    @callback
    def _handle_coordinator_update(self):

        # Get state from the cloud
        json = self._coordinator.data

        # No data returned by the Get State method (unauthorized...)
        if json is False:
            return

        ivoc = json["vocValueIndoor"]["parNewVal"]

        if ivoc in PURIFIER_VOC_VALUE:
            self._attr_native_value = PURIFIER_VOC_VALUE[ivoc]
        else:
            self._attr_native_value = f"Unknown value {ivoc}"
        self.async_write_ha_state()