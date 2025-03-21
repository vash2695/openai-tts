from homeassistant import config_entries, exceptions
from homeassistant.components.tts import ATTR_VOICE
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import openai
import voluptuous as vol

from .const import (
    CONF_INSTRUCTIONS,
    CONF_MODEL,
    CONF_OPTIMIZE_LATENCY,
    CONF_RESPONSE_FORMAT,
    CONF_SIMILARITY,
    CONF_STABILITY,
    CONF_STYLE,
    CONF_USE_SPEAKER_BOOST,
    DEFAULT_INSTRUCTIONS,
    DEFAULT_MODEL,
    DEFAULT_OPTIMIZE_LATENCY,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_SIMILARITY,
    DEFAULT_STABILITY,
    DEFAULT_STYLE,
    DEFAULT_USE_SPEAKER_BOOST,
    DEFAULT_VOICE,
    DOMAIN,
    OPENAI_MODELS,
    OPENAI_VOICES,
    OUTPUT_FORMATS,
)
from .openai import OpenAIClient


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

    def __init__(self, config_entry):
        """Initialize TTS options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the TTS options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_API_KEY,
                        default=self.config_entry.data.get(CONF_API_KEY),
                    ): str,
                    vol.Optional(
                        ATTR_VOICE,
                        default=self.config_entry.options.get(
                            ATTR_VOICE, DEFAULT_VOICE
                        ),
                    ): vol.In(OPENAI_VOICES),
                    vol.Optional(
                        CONF_MODEL,
                        default=self.config_entry.options.get(
                            CONF_MODEL, DEFAULT_MODEL
                        ),
                    ): vol.In(OPENAI_MODELS),
                    vol.Optional(
                        CONF_INSTRUCTIONS,
                        default=self.config_entry.options.get(
                            CONF_INSTRUCTIONS, DEFAULT_INSTRUCTIONS
                        ),
                    ): str,
                    vol.Optional(
                        CONF_RESPONSE_FORMAT,
                        default=self.config_entry.options.get(
                            CONF_RESPONSE_FORMAT, DEFAULT_RESPONSE_FORMAT
                        ),
                    ): vol.In(OUTPUT_FORMATS),
                    # Legacy options kept for compatibility
                    vol.Optional(
                        CONF_STABILITY,
                        default=self.config_entry.options.get(
                            CONF_STABILITY, DEFAULT_STABILITY
                        ),
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0, max=1),
                    ),
                    vol.Optional(
                        CONF_SIMILARITY,
                        default=self.config_entry.options.get(
                            CONF_SIMILARITY, DEFAULT_SIMILARITY
                        ),
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0, max=1),
                    ),
                    vol.Optional(
                        CONF_OPTIMIZE_LATENCY,
                        default=self.config_entry.options.get(
                            CONF_OPTIMIZE_LATENCY, DEFAULT_OPTIMIZE_LATENCY
                        ),
                    ): vol.All(int, vol.Range(min=0, max=4)),
                    vol.Optional(
                        CONF_STYLE,
                        default=self.config_entry.options.get(
                            CONF_STYLE, DEFAULT_STYLE
                        ),
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0, max=1),
                    ),
                    vol.Optional(
                        CONF_USE_SPEAKER_BOOST,
                        default=self.config_entry.options.get(
                            CONF_USE_SPEAKER_BOOST, DEFAULT_USE_SPEAKER_BOOST
                        ),
                    ): bool,
                }
            ),
        )


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth.""" 