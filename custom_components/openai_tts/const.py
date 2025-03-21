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
    "tts-1",            # Standard voice generation
    "tts-1-hd",         # High-definition voice generation
]

# Legacy ElevenLabs parameters (keeping for backward compatibility)
CONF_STABILITY = "stability"
DEFAULT_STABILITY = 0.75
CONF_SIMILARITY = "similarity"
DEFAULT_SIMILARITY = 0.9
CONF_OPTIMIZE_LATENCY = "optimize_streaming_latency"
DEFAULT_OPTIMIZE_LATENCY = 0
CONF_STYLE = "style"
DEFAULT_STYLE = 0.2
CONF_USE_SPEAKER_BOOST = "use_speaker_boost"
DEFAULT_USE_SPEAKER_BOOST = True

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