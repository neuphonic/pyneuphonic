"""
This script defines a Wikipedia chatbot that fetches the main body of a specified Wikipedia article,
processes the content to remove reference superscripts, and creates a chatbot using the Neuphonic API.
The chatbot can answer questions about the article's content in a succinct manner.

The script includes the following main components:
1. WikipediaHTMLParser: A custom HTML parser to extract text from <p> tags.
2. get_wikipedia_main_body: A function to fetch and process the main body of a Wikipedia article.

To use this script, set the WIKIPEDIA_ARTICLE_TITLE variable to the desired Wikipedia article title.
Ensure that the NEUPHONIC_API_TOKEN environment variable is set with your Neuphonic API token.
"""

import httpx
import html.parser
import re
import os
import asyncio

# See AgentConfig model for full list of parameters to configure the agent
from pyneuphonic import Neuphonic, Agent, AgentConfig  # noqa: F401

# You can change this to any Wikipedia article title you want to fetch.
WIKIPEDIA_ARTICLE_TITLE = 'Python (programming language)'


class WikipediaHTMLParser(html.parser.HTMLParser):
    """
    A simple HTML parser that extracts text from <p> tags without nested <p> tags.

    This parser processes HTML content and collects the text contained within
    <p> tags, ensuring that only top-level <p> tags are considered (i.e., <p> tags
    that do not contain other <p> tags).

    Attributes
    ----------
    is_in_paragraph : bool
        Indicates whether the parser is currently inside a valid <p> tag.
    current_paragraph : list of str
        Stores the content of the currently processed paragraph.
    paragraphs : list of str
        Stores the text content of all valid paragraphs.
    """

    def __init__(self):
        super().__init__()
        self.is_in_paragraph = False
        self.current_paragraph = []
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        """
        Handle the start of an HTML tag.

        Parameters
        ----------
        tag : str
            The name of the tag (e.g., "p").
        attrs : list of tuple
            A list of attributes for the tag.
        """
        if tag == 'p':
            if not self.is_in_paragraph:  # Start a new paragraph
                self.is_in_paragraph = True
                self.current_paragraph = []

    def handle_endtag(self, tag):
        """
        Handle the end of an HTML tag.

        Parameters
        ----------
        tag : str
            The name of the tag (e.g., "p").
        """
        if tag == 'p' and self.is_in_paragraph:  # End of the current paragraph
            self.is_in_paragraph = False
            self.paragraphs.append(''.join(self.current_paragraph).strip())

    def handle_data(self, data):
        """
        Handle textual data within an HTML tag.

        Parameters
        ----------
        data : str
            The textual data encountered within a tag.
        """
        if self.is_in_paragraph:
            self.current_paragraph.append(data)

    def get_paragraphs(self):
        """
        Retrieve all collected paragraphs.

        Returns
        -------
        list of str
            A list of strings, each representing a paragraph's text.
        """
        return self.paragraphs


def extract_text_from_html(html):
    """
    Extracts text from <p> tags in the given HTML content using the built-in HTML parser.

    Filters out nested <p> tags and removes extra whitespace and reference
    superscripts (e.g., [1], [2], etc.).

    Parameters
    ----------
    html : str
        The HTML content to parse.

    Returns
    -------
    str
        The cleaned text content of all valid <p> tags, joined by double line breaks.
    """
    parser = WikipediaHTMLParser()
    parser.feed(html)
    parser.close()

    # Get the text content of all valid <p> tags
    paragraphs = parser.get_paragraphs()

    # Remove reference superscripts (e.g., [1], [2], etc.) and clean up each paragraph
    clean_paragraphs = [re.sub(r'\[\d+\]', '', p).strip() for p in paragraphs]

    # Combine paragraphs into a single text block
    return '\n\n'.join(clean_paragraphs)


def get_wikipedia_main_body(title):
    """
    Fetch the main body of a Wikipedia article using the MediaWiki API and httpx.

    This function queries the MediaWiki API for the specified article's content,
    extracts the HTML of the main body, and processes it to retrieve the cleaned
    text from valid <p> tags.

    Parameters
    ----------
    title : str
        The title of the Wikipedia article to fetch.

    Returns
    -------
    str
        The cleaned text content of the article's main body.
    """
    API_URL = 'https://en.wikipedia.org/w/api.php'

    # Parameters for the MediaWiki API
    params = {
        'action': 'parse',
        'page': title,
        'prop': 'text',
        'format': 'json',
        'formatversion': 2,
        'redirects': 1,
        'disabletoc': 1,
        'disablelimitreport': 1,
    }

    # Fetch the data using httpx
    with httpx.Client() as client:
        response = client.get(API_URL, params=params)
        response.raise_for_status()  # Raise an error if the request fails
        data = response.json()

    # Extract the HTML content of the main body
    if 'parse' in data and 'text' in data['parse']:
        html_content = data['parse']['text']
        return extract_text_from_html(html_content)
    else:
        return ''  # Return an empty string if the data is not available


async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

    wikipedia_article_text = get_wikipedia_main_body(WIKIPEDIA_ARTICLE_TITLE)
    wikipedia_article_text = ' '.join(wikipedia_article_text.split(' ')[0:1000])

    prompt = f"""
    You are a helpful chatbot. Below is the main body of a wikipedia article titled:
    "{WIKIPEDIA_ARTICLE_TITLE}". Please answer any questions about this, keep your answers
    succinct.

    ```
    {wikipedia_article_text}
    ```
    """

    agent_id = client.agents.create(
        name='Wikipedia Chatbot',
        prompt=prompt,
        greeting=f'Hi, what would you like to know about the wikipedia article titled "{WIKIPEDIA_ARTICLE_TITLE}"',
    ).data['id']

    # All additional keyword arguments (such as `agent_id` and `tts_model`) are passed as
    # parameters to the model. See AgentConfig model for full list of parameters.
    agent = Agent(client, agent_id=agent_id, tts_model='neu_hq')

    await agent.start()


asyncio.run(main())
