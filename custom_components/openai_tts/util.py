"""Utility functions for OpenAI TTS."""
import logging

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