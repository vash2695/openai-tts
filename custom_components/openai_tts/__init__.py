"""OpenAI TTS Custom Integration"""

import logging

import openai

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_INSTRUCTIONS, DEFAULT_VOICE, DOMAIN, PLATFORMS
from .openai import OpenAIClient

_LOGGER = logging.getLogger(__name__)


def normalize_instructions(instructions):
    """Normalize instructions value to ensure consistent behavior."""
    if instructions is None:
        _LOGGER.debug("normalize_instructions: Converting None to empty string")
        return ""
    if instructions == "":
        _LOGGER.debug("normalize_instructions: Empty string preserved")
        return ""
    if isinstance(instructions, str) and instructions.strip() == "":
        _LOGGER.debug("normalize_instructions: Converting whitespace-only to empty string")
        return ""
    _LOGGER.debug("normalize_instructions: Keeping non-empty value: '%s'", instructions)
    return instructions


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the OpenAI TTS component from a config entry."""
    _LOGGER.debug("Setting up OpenAI TTS integration for entry: %s", entry.entry_id)
    
    # Normalize any entry options
    if entry.options and CONF_INSTRUCTIONS in entry.options:
        # Don't modify the entry directly, but handle normalization when accessing
        instructions_value = entry.options.get(CONF_INSTRUCTIONS)
        normalized = normalize_instructions(instructions_value)
        if normalized != instructions_value:
            _LOGGER.debug(
                "Instruction value in config entry needed normalization: '%s' -> '%s'",
                instructions_value, normalized
            )
    
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