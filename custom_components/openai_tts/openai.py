"""OpenAI TTS API client."""
import logging
from typing import Any, Dict, List, Optional, Tuple

import openai
from openai import OpenAI

from homeassistant.components.tts import ATTR_AUDIO_OUTPUT, ATTR_VOICE, Voice
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .const import (
    CONF_INSTRUCTIONS,
    CONF_MODEL,
    CONF_RESPONSE_FORMAT,
    DEFAULT_INSTRUCTIONS,
    DEFAULT_MODEL,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_VOICE,
    DOMAIN,
    OPENAI_VOICES,
)

_LOGGER = logging.getLogger(__name__)

class OpenAIClient:
    """A class to handle the connection to the OpenAI API."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry = None, api_key=None
    ) -> None:
        """Initialize the client."""
        _LOGGER.debug("Initializing OpenAI client")

        if api_key is None and config_entry is None:
            raise ValueError("Either 'api_key' or 'config_entry' must be provided.")

        self.config_entry = config_entry
        if api_key is not None:
            self._api_key = api_key
        else:
            self._api_key = config_entry.data[CONF_API_KEY]

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self._api_key)
        
        # Create Voice objects for UI
        self.voices = [Voice(voice_id=voice, name=voice.capitalize()) for voice in OPENAI_VOICES]

    async def get_voices(self) -> List[str]:
        """Get voices from the API.
        
        For OpenAI, these are hardcoded as they're predefined by the API.
        This method validates the API key by making a test request.
        """
        # Validate the API key by listing models - this is a lightweight call
        try:
            # Use sync method in async context as it's just for validation
            models = self.client.models.list()
            return OPENAI_VOICES
        except openai.OpenAIError as e:
            _LOGGER.error("Error validating OpenAI API key: %s", e)
            raise

    async def get_voice_by_name_or_id(self, identifier: str) -> Dict[str, Any]:
        """Get a voice by its name or ID."""
        _LOGGER.debug("Looking for voice with identifier %s", identifier)
        
        # Normalize the identifier to lowercase
        identifier = identifier.lower()
        
        # Check if it's one of our supported voices
        if identifier in OPENAI_VOICES:
            return {"voice_id": identifier, "name": identifier}
        
        # If not found, log a warning
        _LOGGER.warning("Could not find voice with identifier %s", identifier)
        return {}

    async def get_tts_audio(
        self, message: str, options: Dict[str, Any] = None
    ) -> Tuple[str, bytes]:
        """Get text-to-speech audio for the given message."""
        _LOGGER.debug("Getting TTS audio for message: %s", message)
        
        if not options:
            options = {}
            
        # Get options with defaults
        voice_opt = (
            options.get(ATTR_VOICE)
            or self.config_entry.options.get(ATTR_VOICE)
            or DEFAULT_VOICE
        )
        
        model = (
            options.get(CONF_MODEL)
            or self.config_entry.options.get(CONF_MODEL)
            or DEFAULT_MODEL
        )
        
        # Explicitly handle empty string for instructions
        if CONF_INSTRUCTIONS in options:
            instructions = options.get(CONF_INSTRUCTIONS)
        elif CONF_INSTRUCTIONS in self.config_entry.options:
            instructions = self.config_entry.options.get(CONF_INSTRUCTIONS)
        else:
            instructions = DEFAULT_INSTRUCTIONS
        
        response_format = (
            options.get(CONF_RESPONSE_FORMAT)
            or self.config_entry.options.get(CONF_RESPONSE_FORMAT)
            or DEFAULT_RESPONSE_FORMAT
        )
        
        # Ensure voice is valid
        voice = await self.get_voice_by_name_or_id(voice_opt)
        voice_id = voice.get("voice_id", DEFAULT_VOICE)
        
        # Log the request details
        _LOGGER.debug(
            "TTS Request - model: %s, voice: %s, format: %s, instructions: %s",
            model, voice_id, response_format, instructions if instructions else "None"
        )
        
        try:
            # Create the request
            kwargs = {
                "model": model,
                "input": message,
                "voice": voice_id,
                "response_format": response_format,
            }
            
            # Only add instructions if not empty
            if instructions:
                kwargs["instructions"] = instructions
                
            # Make the API call
            response = self.client.audio.speech.create(**kwargs)
            
            # Get the audio content
            audio_content = response.content
            
            return response_format, audio_content
            
        except openai.OpenAIError as e:
            _LOGGER.error("Error calling OpenAI TTS API: %s", e)
            raise 