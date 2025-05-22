from pyneuphonic import Neuphonic
from pyneuphonic.player import AudioPlayer
import os
import asyncio
import aioconsole


async def main():
    """A simple application that echos whatever the user enters into the terminal."""
    client = Neuphonic(api_key=os.environ.get("NEUPHONIC_API_KEY"))
    sse = client.tts.SSEClient()

    with AudioPlayer() as player:
        while True:
            user_text = await aioconsole.ainput(
                "Enter text to speak (or 'quit' to exit): "
            )

            if user_text.lower() == "quit":
                break

            response = sse.send(user_text)
            player.play(response)


if __name__ == "__main__":
    asyncio.run(main())
