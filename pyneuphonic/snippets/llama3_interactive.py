import ollama
import asyncio
from pyneuphonic.websocket.common.message_senders import send_async_generator
import logging
from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.common.pyaudio import on_open, on_close, on_audio_message
import aioconsole

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s'
)


async def async_llama_chat_stream(user_input):
    PROMPT = """
    You are a helpful AI assistant named New. Your responses should be conversational, friendly,
    and natural-sounding, as if you're chatting with a friend. Feel free to use casual language, contractions,
    and even the occasional bit of humor when appropriate. You have your own thoughts and opinions, but you're
    also curious to hear what others think. If you're not sure about something, it's okay to say so - you don't
    have to know everything. Try to keep your responses concise unless asked for more detail. Your goal is to be
    helpful while maintaining a natural, engaging conversation. Let's begin our chat!

    Keep your responses to a maximum of 10 words.
    """
    stream = ollama.chat(
        model='llama3:8b',
        messages=[
            {'role': 'system', 'content': PROMPT},
            {'role': 'user', 'content': user_input},
        ],
        stream=True,
    )
    for chunk in stream:
        yield chunk['message']['content']


async def user_input_loop(client):
    while True:
        user_input = await aioconsole.ainput(
            "Enter your question (or 'quit' to exit): "
        )
        if user_input.lower() == 'quit':
            await client.close()
            break

        text_generator = async_llama_chat_stream(user_input)
        try:
            await asyncio.wait_for(
                send_async_generator(client, text_generator), timeout=60
            )
        except Exception as e:
            print(f'Error in conversational loop: {e}')


async def llama3_interactive():
    client = NeuphonicWebsocketClient(
        on_open=on_open, on_audio_message=on_audio_message, on_close=on_close
    )

    await client.open()

    await asyncio.gather(client.listen(), user_input_loop(client))


if __name__ == '__main__':
    asyncio.run(llama3_interactive())
