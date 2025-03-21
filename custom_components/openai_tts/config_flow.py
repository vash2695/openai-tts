from homeassistant import config_entries, exceptions
from homeassistant.components.tts import ATTR_VOICE
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import logging
import openai
import voluptuous as vol

from .const import (
    CONF_INSTRUCTIONS,
    CONF_MODEL,
    CONF_RESPONSE_FORMAT,
    DEFAULT_INSTRUCTIONS,
    DEFAULT_MODEL,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_VOICE,
    DOMAIN,
    OPENAI_MODELS,
    OPENAI_VOICES,
    OUTPUT_FORMATS,
)
from .openai import OpenAIClient

_LOGGER = logging.getLogger(__name__)

class OpenAITTSSetupFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input: dict = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            # Validate the provided API key
            resp = await self._validate_api_key(user_input[CONF_API_KEY])
            if resp is not None:
                errors[CONF_API_KEY] = resp

            if not errors:
                return self.async_create_entry(title="OpenAI TTS", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OpenAITTSOptionsFlowHandler(config_entry)

    async def _validate_api_key(self, api_key) -> str:
        """Perform API key validation.
        
        Returns None if the key is valid, otherwise returns an error message.
        """
        client = OpenAIClient(self.hass, api_key=api_key)
        try:
            await client.get_voices()
        except openai.AuthenticationError:
            return "invalid_auth"
        except openai.RateLimitError:
            return "rate_limit"
        except openai.APIError:
            return "cannot_connect"
        except openai.OpenAIError as e:
            return f"openai_error: {str(e)}"
        except Exception as e:
            return f"unknown_error: {str(e)}"
        return None


class OpenAITTSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle TTS options."""

    def __init__(self, entry):
        """Initialize TTS options flow."""
        self._entry = entry
        _LOGGER.debug("Initializing options flow for entry: %s", entry.entry_id)
        if entry.options:
            _LOGGER.debug("Current entry options: %s", 
                         {k: v for k, v in entry.options.items() if k != CONF_API_KEY})

    async def async_step_init(self, user_input=None):
        """Manage the TTS options."""
        if user_input is not None:
            _LOGGER.debug("Received options user_input: %s", 
                         {k: v for k, v in user_input.items() if k != CONF_API_KEY})
            
            # Explicitly handle empty instructions
            if CONF_INSTRUCTIONS in user_input:
                if user_input[CONF_INSTRUCTIONS] == "" or user_input[CONF_INSTRUCTIONS] is None:
                    _LOGGER.debug("Empty instructions detected, storing as empty string")
                    user_input[CONF_INSTRUCTIONS] = ""
            
            data = {**user_input}
            _LOGGER.debug("Saving options: %s", 
                         {k: v for k, v in data.items() if k != CONF_API_KEY})
            return self.async_create_entry(title="", data=data)

        # Get current instructions or empty string (not None)
        current_instructions = self._entry.options.get(CONF_INSTRUCTIONS)
        _LOGGER.debug("Current instructions value: '%s' (type: %s)", 
                     current_instructions, 
                     type(current_instructions).__name__ if current_instructions is not None else "None")
        
        # Normalize to empty string
        if current_instructions is None:
            current_instructions = ""
            _LOGGER.debug("Normalized None instructions to empty string for form")

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_API_KEY,
                    default=self._entry.data.get(CONF_API_KEY),
                ): str,
                vol.Optional(
                    ATTR_VOICE,
                    default=self._entry.options.get(
                        ATTR_VOICE, DEFAULT_VOICE
                    ),
                ): vol.In(OPENAI_VOICES),
                vol.Optional(
                    CONF_MODEL,
                    default=self._entry.options.get(
                        CONF_MODEL, DEFAULT_MODEL
                    ),
                ): vol.In(OPENAI_MODELS),
                vol.Optional(
                    CONF_INSTRUCTIONS,
                    default=current_instructions,
                ): str,
                vol.Optional(
                    CONF_RESPONSE_FORMAT,
                    default=self._entry.options.get(
                        CONF_RESPONSE_FORMAT, DEFAULT_RESPONSE_FORMAT
                    ),
                ): vol.In(OUTPUT_FORMATS),
            }
        )
        
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth.""" 