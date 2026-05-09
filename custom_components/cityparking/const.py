"""Constants for the shell_recharge integration."""

from datetime import timedelta
from enum import IntFlag
from enum import Enum

DOMAIN = "cityparking"
SerialNumber = str
Origin = str
UPDATE_INTERVAL = timedelta(minutes=5)
CONF_ORIGIN = "origin"
CONF_API_MODE = "api_mode"
CONF_API_KEY = "api_key"
API_MODE_LEGACY = "legacy"
API_MODE_OFFICIAL = "official"
