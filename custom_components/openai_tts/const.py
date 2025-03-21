"""Consts module."""

from homeassistant.const import Platform

################################
# Do not change! Will be set by release workflow
INTEGRATION_VERSION = "main"  # git tag will be used
MIN_REQUIRED_HA_VERSION = "0.0.0"  # set min required version in hacs.json
################################

PLATFORMS = [Platform.TTS]

DOMAIN = "openai_tts"
VERSION = "1.0.0"

DEFAULT_VOICE = "echo"
CONF_MODEL = "model"
DEFAULT_MODEL = "gpt-4o-mini-tts"

# OpenAI TTS Models
OPENAI_MODELS = [
    "gpt-4o-mini-tts",  # Default model
]

# New OpenAI-specific parameters
CONF_INSTRUCTIONS = "instructions"
DEFAULT_INSTRUCTIONS = ""
CONF_RESPONSE_FORMAT = "response_format"
DEFAULT_RESPONSE_FORMAT = "mp3"

# OpenAI voice options
OPENAI_VOICES = [
    "alloy",
    "echo",
    "fable",
    "onyx",
    "nova",
    "shimmer",
    "coral",
    "sage",
    "ash",
    "ballad",
]

# Output format options
OUTPUT_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"] 