import logging
import hashlib
import json

from homeassistant.components.tts import (
    ATTR_AUDIO_OUTPUT,
    ATTR_VOICE,
    TextToSpeechEntity,
    TtsAudioType,
    Voice,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import normalize_instructions
from .const import (
    CONF_INSTRUCTIONS,
    CONF_MODEL,
    CONF_RESPONSE_FORMAT,
    DOMAIN,
    OUTPUT_FORMATS,
)
from .openai import OpenAIClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAI TTS speech to text."""
    client: OpenAIClient = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            OpenAITTSProvider(config_entry, client),
        ]
    )


class OpenAITTSProvider(TextToSpeechEntity):
    """The OpenAI TTS API provider."""

    def __init__(self, config_entry: ConfigEntry, client: OpenAIClient) -> None:
        """Initialize the provider."""
        self._client = client
        self._config_entry = config_entry
        self._name = "OpenAI TTS"

        self._attr_unique_id = f"{config_entry.entry_id}-tts"
        _LOGGER.debug("Initialized TTS provider with unique_id: %s", self._attr_unique_id)
        
        # Log configuration options
        if config_entry.options:
            _LOGGER.debug(
                "TTS provider initialized with options: %s", 
                {k: v for k, v in config_entry.options.items() if k != CONF_API_KEY}
            )

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        # This is for gpt-4o-mini-tts, may need updating
        return [
            "en",  # English
            "ja",  # Japanese
            "zh",  # Chinese
            "de",  # German
            "hi",  # Hindi
            "fr",  # French
            "ko",  # Korean
            "pt",  # Portuguese
            "it",  # Italian
            "es",  # Spanish
            "id",  # Indonesian
            "nl",  # Dutch
            "tr",  # Turkish
            "fil",  # Filipino
            "pl",  # Polish
            "sv",  # Swedish
            "bg",  # Bulgarian
            "ro",  # Romanian
            "ar",  # Arabic
            "cs",  # Czech
            "el",  # Greek
            "fi",  # Finnish
            "hr",  # Croatian
            "ms",  # Malay
            "sk",  # Slovak
            "da",  # Danish
            "ta",  # Tamil
            "uk",  # Ukrainian
            "vi",  # Vietnamese
            "hu",  # Hungarian
            "no",  # Norwegian
        ]

    @property
    def default_options(self):
        """Return a dict include default options."""
        return {ATTR_AUDIO_OUTPUT: "mp3"}

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return [
            ATTR_VOICE,
            CONF_MODEL,
            CONF_INSTRUCTIONS,
            CONF_RESPONSE_FORMAT,
            CONF_API_KEY,
            ATTR_AUDIO_OUTPUT,
        ]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict | None = None
    ) -> TtsAudioType:
        """Load TTS from the OpenAI API."""
        _LOGGER.debug("async_get_tts_audio called with message: %s, language: %s, options: %s", 
                     message[:20] + "..." if len(message) > 20 else message, 
                     language, 
                     options)
                     
        # Get the current config_entry options for debugging
        if self._config_entry.options:
            _LOGGER.debug("Current config_entry options: %s", 
                         {k: v for k, v in self._config_entry.options.items() if k != CONF_API_KEY})
        
        return await self._client.get_tts_audio(message, options)

    def get_cache_key_base(self, message: str, language: str, options: dict | None = None) -> str:
        """Get base for generating cache key."""
        if options is None:
            options = {}

        _LOGGER.debug("Getting cache key for options: %s", options)
        
        # Make a copy to avoid modifying the original
        options_copy = dict(options)
        
        # Include config entry options that aren't overridden in the service call
        if self._config_entry and self._config_entry.options:
            # Only include specific TTS options, not all config entry options
            for opt in self.supported_options:
                if opt not in options_copy and opt in self._config_entry.options:
                    options_copy[opt] = self._config_entry.options[opt]
                    _LOGGER.debug("Added config entry option %s: %s to cache key", 
                                 opt, 
                                 options_copy[opt])
        
        # Ensure consistent handling of instructions using the normalize_instructions function
        if CONF_INSTRUCTIONS in options_copy:
            original_value = options_copy[CONF_INSTRUCTIONS]
            options_copy[CONF_INSTRUCTIONS] = normalize_instructions(original_value)
            if original_value != options_copy[CONF_INSTRUCTIONS]:
                _LOGGER.debug("Normalized instructions for cache key from '%s' to '%s'", 
                             original_value, options_copy[CONF_INSTRUCTIONS])
        
        # Convert to JSON for cache key
        options_json = json.dumps(
            options_copy, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )
        
        key_base = f"{message}_{language}_{options_json}"
        cache_key = hashlib.sha1(key_base.encode("utf-8")).hexdigest()
        
        _LOGGER.debug("Generated cache key: %s from options_json: %s", 
                     cache_key, options_json)
        
        return cache_key

    def async_get_supported_voices(self, language: str) -> list[Voice] | None:
        """Return a list of supported voices for a language."""
        return self._client.voices

    @property
    def name(self) -> str:
        """Return provider name."""
        return self._name

    @property
    def extra_state_attributes(self) -> dict:
        """Return provider attributes."""
        return {"provider": self._name} 