from anthropic import Anthropic
import openai
from abc import ABC, abstractmethod
from prompt import SYSTEM_PROMPT

class ChatHandler(ABC):
    @abstractmethod
    def get_response(self, messages, message_placeholder):
        pass

MAX_TOKENS = 4096
class ClaudeHandler(ChatHandler):
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)

    def get_response(self, messages, message_placeholder):
        try:
            full_messages = [
                                {"role": "assistant", "content": SYSTEM_PROMPT}
                            ] + messages
            with self.client.messages.stream(
                    max_tokens=MAX_TOKENS,
                    messages=[
                        {"role": m["role"], "content": m["content"]} for m in full_messages
                    ],
                    model="claude-3-5-sonnet-20241022"
            ) as stream:
                full_response = ""
                for text in stream.text_stream:
                    full_response += text
                    message_placeholder.markdown(
                        f'<div class="assistant-message">{full_response}</div>',
                        unsafe_allow_html=True
                    )
                return full_response
        except Exception as e:
            error_message = f"An error occurred with Claude: {str(e)}"
            message_placeholder.error(error_message)
            return error_message


class ChatGPTHandler(ChatHandler):
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def get_response(self, messages, message_placeholder):
        try:
            full_messages = [
                                {"role": "system", "content": SYSTEM_PROMPT}
                            ] + messages
            stream = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": m["role"], "content": m["content"]} for m in full_messages],
                stream=True
            )

            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(
                        f'<div class="assistant-message">{full_response}</div>',
                        unsafe_allow_html=True
                    )
            return full_response
        except Exception as e:
            error_message = f"An error occurred with ChatGPT: {str(e)}"
            message_placeholder.error(error_message)
            return error_message