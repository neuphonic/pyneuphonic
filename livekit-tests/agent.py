from dotenv import load_dotenv
from livekit.agents import JobContext, JobProcess, AgentServer, cli, Agent, AgentSession, inference
from livekit.plugins import silero, neuphonic
import os
import asyncio

load_dotenv()

server = AgentServer()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3-general"),
        llm=inference.LLM(model="openai/gpt-5-mini"),
        # tts=inference.TTS(model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
        tts=neuphonic.TTS(api_key=os.getenv("NEUPHONIC_API_KEY")),
        vad=ctx.proc.userdata["vad"],
        allow_interruptions=False,
    )

    await session.start(
        agent=Agent(
            instructions="You are a helpful assistant."
        ),
        room=ctx.room
    )
    await ctx.connect()
    
    asyncio.create_task(shutdown_after_timeout())
    await session.say("Hello, how are you?")

    print("Integration Test Success!", flush=True)

async def shutdown_after_timeout():
    await asyncio.sleep(10)
    print("\n10 seconds elapsed, shutting down...")
    os._exit(0)
    
if __name__ == "__main__":
    cli.run_app(server)
