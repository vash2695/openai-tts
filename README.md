# OpenAI TTS for Home Assistant

This integration allows you to use OpenAI's Text-to-Speech API as a text-to-speech provider for Home Assistant. It is a complete rework based on the [ElevenLabs TTS](https://github.com/carleeno/elevenlabs_tts) integration made by carleeno.

Disclaimer: This repo, the code within, and the maintainer/owner of this repo are in no way affiliated with OpenAI.

Privacy disclaimer: Data is transmitted to OpenAI when using this TTS service, do not use it for text containing sensitive information.

You can find OpenAI's privacy policy [here](https://openai.com/policies/privacy-policy)

## Installation

This component is available via HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) which is the recommended method of installation.

You can also copy `custom_components/openai_tts` to your `custom_components` folder in HomeAssistant if you prefer to install manually.

## Setup

Go to Settings -> Devices & Services -> ADD INTEGRATION, and select OpenAI TTS

Enter your API key from your OpenAI account and click Submit.

### Options:

To customize the default options, in Devices & Services, click CONFIGURE on the OpenAI TTS card.

- `Voice` - Choose one of the available voices (echo, alloy, onyx, nova, shimmer, etc.)
- `Model` - Select which model to use (currently only supports gpt-4o-mini-tts)
- `Instructions` - Optional instructions to control aspects of speech like accent, emotional range, intonation, etc.
- `Response Format` - Audio format for the response (mp3, opus, aac, flac, wav, pcm)

## API key

To get an API key, create an account at openai.com, and go to API Keys to create a new key.

Note that using this extension will count against your API usage quota and you may be charged based on your OpenAI plan.

## Caching

This integration inherently uses caching for the responses, meaning that if the text and options are the same as a previous service call, the response audio likely will be a replay of the previous response.

## Example service call

```yaml
service: tts.speak
data:
  cache: true
  media_player_entity_id: media_player.bedroom_speaker
  message: Hello, how are you today?
  options:
    voice: echo
    model: gpt-4o-mini-tts
    instructions: Speak in a cheerful and positive tone.
    response_format: mp3
target:
  entity_id: tts.openaitts
```

The parameters in `options` are fully optional, and override the defaults specified in the integration config.

## Voice Options

The integration provides 11 built-in voices to control how speech is rendered from text:

- alloy
- ash
- ballad
- coral
- echo
- fable
- onyx
- nova
- sage
- shimmer

## Supported Languages

The TTS model generally follows the Whisper model in terms of language support. It supports many languages including but not limited to:

English, Japanese, Chinese, German, Hindi, French, Korean, Portuguese, Italian, Spanish, and many more.
