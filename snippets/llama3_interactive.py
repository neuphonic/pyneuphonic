import ollama
import asyncio
from pyneuphonic.websocket.common.message_senders import send_async_generator
from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.common.pyaudio import on_open, on_close, on_message
import aioconsole


async def async_llama_chat_stream(user_input):
    PROMPT = """
    You are a helpful AI assistant named Neu. Your responses should be conversational,
    friendly, and natural-sounding, as if you're chatting with a friend.

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
        on_open=on_open, on_message=on_message, on_close=on_close
    )

    await client.open()
    await client.listen()
    await user_input_loop(client)
    await client.close()


if __name__ == '__main__':
    asyncio.run(llama3_interactive())
