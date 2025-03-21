"""OpenAI TTS Custom Integration"""

import logging

import openai

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DEFAULT_VOICE, DOMAIN, PLATFORMS
from .openai import OpenAIClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the OpenAI TTS component from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = OpenAIClient(hass, entry)

    hass.data[DOMAIN][entry.entry_id] = client

    try:
        await client.get_voices()
    except openai.AuthenticationError:
        _LOGGER.error("Authentication failed. Please check your API key.")
        return False
    except openai.OpenAIError as err:
        _LOGGER.error("Failed to connect to OpenAI API: %s", err)
        raise ConfigEntryNotReady from err
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise ConfigEntryNotReady from err

    voice = await client.get_voice_by_name_or_id(DEFAULT_VOICE)
    if not voice:
        _LOGGER.error("Default voice '%s' not found", DEFAULT_VOICE)
        return False

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenAI TTS."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
    if unload_ok:
        del hass.data[DOMAIN][entry.entry_id]

    return unload_ok 