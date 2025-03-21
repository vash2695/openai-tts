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
        return await self._client.get_tts_audio(message, options)

    def get_cache_key_base(self, message: str, language: str, options: dict | None = None) -> str:
        """Get base for generating cache key."""
        if options is None:
            options = {}

        # Make a copy to avoid modifying the original
        options_copy = dict(options)
        
        # Ensure consistent handling of empty instructions
        if CONF_INSTRUCTIONS in options_copy:
            if not options_copy[CONF_INSTRUCTIONS] or options_copy[CONF_INSTRUCTIONS].strip() == "":
                # Empty instruction is significant and should be part of the key
                options_copy[CONF_INSTRUCTIONS] = ""
        
        # Convert to JSON for cache key
        options_json = json.dumps(
            options_copy, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )
        
        key_base = f"{message}_{language}_{options_json}"
        return hashlib.sha1(key_base.encode("utf-8")).hexdigest()

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