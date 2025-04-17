# Neuphonic Agents - LiveKit Integration Guide

This demo illustrates how to integrate Neuphonic with LiveKit to create an interactive and intelligent
voice agent capable of real-time audio processing and conversation handling.
This demo utilises the [Python LiveKit plugin](https://pypi.org/project/livekit-plugins-neuphonic/)

- [Neuphonic Agents - LiveKit Integration Guide](#neuphonic-agents---livekit-integration-guide)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
    - [Environment Setup](#environment-setup)
    - [Running the Demos](#running-the-demos)
  - [Next Steps](#next-steps)

## Prerequisites
Before getting started, ensure you have:
- A Neuphonic API Key
- A [LiveKit account](https://livekit.io/) with API Credentials.
- Python 3.9 or higher
- An OpenAI API Key and a Deepgram API Key. These demos use OpenAI as the LLM and Deepgram as for
  STT, but you can switch these out for something else if you prefer.

## Setup
### Environment Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment:
   ```bash
   cp .env.example .env
   ```

   Add the following variables to your `.env` file:
   - `NEUPHONIC_API_TOKEN`: Found on the [Neuphonic portal](https://app.neuphonic.com/)
   - `LIVEKIT_URL`, `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET`: Available in your LiveKit portal, in the settings
   - `OPENAI_API_KEY`: For your LLM
   - `DEEPGRAM_API_KEY`: For speech recognition

### Running the Demos
The demo includes several example agents that showcase different capabilities:

1. Quickstart Agent:
   ```bash
   python quickstart_agent.py download-files  # only needs to be run once
   python quickstart_agent.py console
   ```
   This demonstrates basic voice interaction capabilities, converse away!

2. Web Search Agent:
   ```bash
   python web_search_agent.py download-files  # only needs to be run once
   python web_search_agent.py console
   ```
   This demo builds on the previous one and adds web search capabilities.
   As the agent about the latest news on your favourite topic!

## Next Steps
This demo provides a foundation for integrating Neuphonic Agents with LiveKit. To explore more advanced features and capabilities:

- Check out the [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- Visit the [Neuphonic Documentation](https://docs.neuphonic.com/quickstart) for additional integration guides and examples
- Explore the [livekit-agents](https://github.com/livekit/agents) repository for more examples and features
