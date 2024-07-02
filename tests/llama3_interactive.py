import ollama
import asyncio
from pyneuphonic import TTSStreamer
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s'
)


def check_ollama_working_fine():
    # TODO
    return True


async def async_llama_chat_stream(user_input):
    def llama_chat_stream(user_input):
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

    for chunk in llama_chat_stream(user_input):
        yield chunk


async def conversational_loop(tts):
    if check_ollama_working_fine():
        while True:
            user_input = input('Type your question: ')
            if user_input.lower() in ['exit', 'quit']:
                break
            text_generator = async_llama_chat_stream(user_input)
            try:
                await asyncio.wait_for(tts.stream(text_generator), timeout=60)
            except Exception as e:
                print(f'Error in conversational loop: {e}')
    else:
        print('Ollama process not running, please check')


if __name__ == '__main__':
    print('Ask me anything!')
    tts = TTSStreamer()
    asyncio.run(conversational_loop(tts))
