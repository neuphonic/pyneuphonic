import asyncio
import os
from pathlib import Path
import aiohttp
from livekit import rtc
from livekit.agents import JobContext, JobProcess, Agent, AgentSession, inference
from livekit.plugins import silero, neuphonic
from dotenv import load_dotenv

load_dotenv()

async def test_neuphonic_tts_simple(text: str = "Hello, this is a test of the Neuphonic text to speech system."):
    """
    Simple direct test of Neuphonic TTS.
    Synthesizes text to speech and saves it to a file.
    
    Args:
        text: The text to synthesize
    """
    print("=" * 60)
    print("Testing Neuphonic TTS")
    print("=" * 60)
    print(f"Text to synthesize: {text}")
    
    api_key = os.getenv("NEUPHONIC_API_KEY")
    if not api_key:
        raise ValueError("NEUPHONIC_API_KEY not found in environment variables")
    
    # Create HTTP session for the TTS plugin
    # This is required when using TTS outside of agent worker context
    async with aiohttp.ClientSession() as session:
        # Create TTS instance with the session
        tts = neuphonic.TTS(api_key=api_key, http_session=session)
        
        print("\nSynthesizing speech...")
        
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("test_output")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / "tts_test_output.wav"
            
            # Synthesize speech
            stream = tts.synthesize(text)
            
            # Collect audio frames (raw PCM data)
            audio_frames = []
            sample_rate = None
            num_channels = None
            
            async for chunk in stream:
                # chunk.frame is an AudioFrame object with raw PCM data
                audio_frames.append(chunk.frame)
                if sample_rate is None:
                    sample_rate = chunk.frame.sample_rate
                    num_channels = chunk.frame.num_channels
            
            if not audio_frames:
                raise ValueError("No audio frames generated")
            
            # Combine all audio frames into one
            # Concatenate the raw audio data from all frames
            all_audio_data = b''.join([frame.data.tobytes() for frame in audio_frames])
            
            # Create a single AudioFrame with all the data and convert to WAV
            from livekit import rtc
            combined_frame = rtc.AudioFrame(
                data=all_audio_data,
                sample_rate=sample_rate,
                num_channels=num_channels,
                samples_per_channel=len(all_audio_data) // (num_channels * 2)  # 2 bytes per sample (16-bit)
            )
            
            # Convert to WAV bytes and save
            wav_data = combined_frame.to_wav_bytes()
            with open(output_file, 'wb') as f:
                f.write(wav_data)
            
            print(f"Speech synthesized successfully!")
            print(f"Collected {len(audio_frames)} audio chunks")
            print(f"Saved to: {output_file}")
            print(f"File size: {output_file.stat().st_size} bytes")
            
            return str(output_file)
            
        except Exception as e:
            print(f"Error during synthesis: {e}")
            raise


async def test_neuphonic_agent_initialization(text: str = "This is an initialization test of the agent with Neuphonic TTS."):
    """
    initialization test: Test Neuphonic TTS within an agent session context.
    This doesn't require a full LiveKit room connection.
    
    Args:
        text: The text for the agent to speak
    """
    print("\n" + "=" * 60)
    print("Testing Neuphonic TTS in Agent Session (initialization)")
    print("=" * 60)
    print(f"Text: {text}")
    
    api_key = os.getenv("NEUPHONIC_API_KEY")
    if not api_key:
        raise ValueError("NEUPHONIC_API_KEY not found in environment variables")
    
    # Load VAD
    print("\nLoading VAD model...")
    vad = silero.VAD.load()
    print("VAD loaded")
    
    # Create the agent session with Neuphonic TTS
    print("\nCreating agent session with Neuphonic TTS...")
    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3-general"),
        llm=inference.LLM(model="openai/gpt-5-mini"),
        tts=neuphonic.TTS(api_key=api_key),
        vad=vad,
        allow_interruptions=False,
    )
    print("Agent session created")    
    return session


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Unit tests for Neuphonic TTS")
    parser.add_argument("--simple", action="store_true", help="Run simple TTS test")
    parser.add_argument("--initialization", action="store_true", help="Run initialization test (no room)")
    parser.add_argument("--text", type=str, help="Custom text to synthesize")
    
    args = parser.parse_args()
    
    # Default to simple test if no flags provided
    if not any([args.simple, args.initialization]):
        args.simple = True
    
    try:
        if args.simple:
            text = args.text or "Hello, this is a test of the Neuphonic text to speech system."
            asyncio.run(test_neuphonic_tts_simple(text))
        
        if args.initialization:
            text = args.text or "This is an initialization test of the agent with Neuphonic TTS."
            asyncio.run(test_neuphonic_agent_initialization(text))
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
