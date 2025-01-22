import asyncio
import aioconsole

from pyneuphonic.client import Neuphonic
from pyneuphonic.models import APIResponse, AgentResponse, AgentConfig, WebsocketEvents
from pyneuphonic.player import AsyncAudioPlayer, AsyncAudioRecorder


def default_on_message(message: APIResponse[AgentResponse]):
    """
    Default callback function to handle messages from the server.

    Parameters
    ----------
    message : APIResponse[AgentResponse]
        The message received from the server, containing the type and text.
    """
    if message.data.type == 'user_transcript':
        print(f'User: {message.data.text}')
    elif message.data.type == 'llm_response':
        print(f'Agent: {message.data.text}')


class Agent:
    def __init__(
        self, client: Neuphonic, mute=False, on_message=default_on_message, **kwargs
    ):
        """
        Initialize an Agent instance.

        Parameters
        ----------
        client : Neuphonic
            The Neuphonic client instance.
        mute : bool, optional
            If True, the agent will not play audio responses. Default is False.
        on_message : callable, optional
            A callback function to handle messages from the server. Default is default_on_message.
        **kwargs
            Additional keyword arguments to configure the agent. See the `AgentConfig` model for a
            full list of agent configuration parameters.
        """
        self.config = AgentConfig(**kwargs)
        self.mute = mute

        self.ws = client.agents.AsyncWebsocketClient()

        self.player = None
        if not self.mute:
            self.player = AsyncAudioPlayer()

        if 'asr' in self.config.mode:
            # passing in the websocket object will automatically forward audio to the server
            self.recorder = AsyncAudioRecorder(
                sampling_rate=self.config.incoming_sampling_rate,
                websocket=self.ws,
                player=self.player,
            )

        self.on_message_hook = on_message
        self._tasks = []

    async def on_message(self, message: APIResponse[AgentResponse]):
        """
        Handle incoming messages from the server.

        Parameters
        ----------
        message : APIResponse[AgentResponse]
            The message received from the server, containing the type and content.
        """
        # server will return 3 types of messages: audio_response, user_transcript, llm_response
        if message.data.type == 'audio_response':
            if not self.mute:
                await self.player.play(message.data.audio)

        if self.on_message_hook is not None and callable(self.on_message_hook):
            self.on_message_hook(message)

    async def start(self):
        """
        Start the agent, opening necessary connections and handling user input.
        """
        self.ws.on(WebsocketEvents.MESSAGE, self.on_message)
        self.ws.on(WebsocketEvents.CLOSE, self.on_close)

        async def run_agent():
            if not self.mute:
                await self.player.open()
            await self.ws.open(self.config)

            if 'asr' in self.config.mode:
                await self.recorder.record()

                try:
                    while True:
                        await asyncio.sleep(0.01)
                except KeyboardInterrupt:
                    await self.close()

            else:
                while True:
                    user_text = await aioconsole.ainput(
                        "\nEnter text to speak (or 'quit' to exit): "
                    )

                    if user_text.lower() == 'quit':
                        break

                    await self.ws.send({'text': user_text})
                    await asyncio.sleep(1)  # simply for formatting

            await self.close()

        run_task = asyncio.create_task(run_agent())
        self._tasks.append(run_task)

    async def on_close(self):
        """
        Handle the closing of connections and cleanup resources.
        """
        if not self.mute:
            await self.player.close()
        if 'asr' in self.config.mode:
            await self.recorder.close()

    async def stop(self):
        """
        Close the agent, including websocket and any active resources.
        """
        for task in self._tasks:
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

        await self.ws.close()
        await self.on_close()
