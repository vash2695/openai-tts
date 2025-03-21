Text to speech
The Audio API provides a speech endpoint based on our GPT-4o mini TTS (text-to-speech) model. It comes with 11 built-in voices and can be used to create high quality speech with low latency and high controllability.

Quickstart
The speech endpoint takes three key inputs:

1. The model you're using
2. The text to be turned into audio
3. The voice that will speak the output

Here's a simple request example:

Generate spoken audio from input text
<code_example>
from pathlib import Path
from openai import OpenAI

client = OpenAI()
speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="gpt-4o-mini-tts",
  voice="coral",
  input="Today is a wonderful day to build something people love!",
  instructions="Speak in a cheerful and positive tone.",
)
response.stream_to_file(speech_file_path)
</code_example>

By default, the endpoint outputs an MP3 of the spoken audio, but you can configure it to output any supported format.

Text-to-speech models
For intelligent realtime applications, use the gpt-4o-mini-tts model, our newest and most reliable text-to-speech model. You can prompt the model to control aspects of speech, including:
Accent
Emotional range
Intonation
Impressions
Speed of speech
Tone
Whispering

Our other text-to-speech models are tts-1 and tts-1-hd. The tts-1 model provides lower latency, but at a lower quality than the tts-1-hd model.

Voice options
The TTS endpoint provides 11 built‑in voices to control how speech is rendered from text. Hear and play with these voices in OpenAI.fm, our interactive demo for trying the latest text-to-speech model in the OpenAI API. Voices are currently optimized for English.

alloy
ash
ballad
coral
echo
fable
onyx
nova
sage
shimmer


Supported output formats
The default response format is mp3, but other formats like opus and wav are available.

MP3: The default response format for general use cases.
Opus: For internet streaming and communication, low latency.
AAC: For digital audio compression, preferred by YouTube, Android, iOS.
FLAC: For lossless audio compression, favored by audio enthusiasts for archiving.
WAV: Uncompressed WAV audio, suitable for low-latency applications to avoid decoding overhead.
PCM: Similar to WAV but contains the raw samples in 24kHz (16-bit signed, low-endian), without the header.

Supported languages
The TTS model generally follows the Whisper model in terms of language support. Whisper supports the following languages and performs well, despite voices being optimized for English:

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean, Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, and Welsh.

You can generate spoken audio in these languages by providing input text in the language of your choice.


<demo_code>
import asyncio

from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

openai = AsyncOpenAI()

input = """Ahoy there, traveler! Ye've secured yer lodgin' like a true seafarer, and I be here to confirm yer stay!\n\nArrr, ye be booked at The Golden Anchor Inn, checkin' in on the 12th o' the month and settin' sail on the 15th. Ye got a deluxe ocean-view cabin, fit for a captain, with a king-size bunk an' a stash o' fresh linens.\n\nBreakfast? Aye, included. Wi-Fi? Arrr, faster than a ship in a tailwind. Need to change yer plans? Just send a message via parrot—or, ye know, give us a ring.\n\nAll set, matey! Safe travels, and may yer nights be restful an' yer pillows as soft as a mermaid's song. Arrrr!"""

instructions = """Voice: Deep and rugged, with a hearty, boisterous quality, like a seasoned sea captain who's seen many voyages.\n\nTone: Friendly and spirited, with a sense of adventure and enthusiasm, making every detail feel like part of a grand journey.\n\nDialect: Classic pirate speech with old-timey nautical phrases, dropped \"g\"s, and exaggerated \"Arrrs\" to stay in character.\n\nPronunciation: Rough and exaggerated, with drawn-out vowels, rolling \"r\"s, and a rhythm that mimics the rise and fall of ocean waves.\n\nFeatures: Uses playful pirate slang, adds dramatic pauses for effect, and blends hospitality with seafaring charm to keep the experience fun and immersive."""

async def main() -> None:

    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="sage",
        input=input,
        instructions=instructions,
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

if __name__ == "__main__":
    asyncio.run(main())
</demo_code>