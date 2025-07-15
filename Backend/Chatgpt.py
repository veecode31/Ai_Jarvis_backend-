import os
import requests
import base64
import datetime
from json import load, dump
from dotenv import load_dotenv
from rich import print

load_dotenv()

class LLM:
    def __init__(self, messages=None, model='gpt-3.5-turbo', temperature=0.0, max_tokens=2048, verbose=False):
        self.api_key = os.getenv('GoogleAiStudio', '')  # Load API key from .env
        if not self.api_key:
            raise ValueError("API key is missing. Please set it in the .env file.")

        self.session = requests.Session()
        self.messages = messages or []
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.verbose = verbose

    def run(self, prompt=None):
        if prompt:
            self.add_message('user', prompt)

        # Correct API URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateText?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            'temperature': self.temperature,
            'prompt': {
                'text': prompt
            },
            'max_output_tokens': self.max_tokens
        }

        try:
            response = self.session.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['candidates'][0]['output']  # Correct JSON key
        except requests.exceptions.RequestException as e:
            try:
                error_message = response.json().get('error', {}).get('message', 'An error occurred')
            except Exception:
                error_message = str(e)
            print(f"Error: {error_message}")
            if "not found" in error_message.lower():
                print("The specified model does not exist or you do not have access to it.")
            return "An error occurred while connecting to the API."

    def add_message(self, role, content=''):
        self.messages.append({'role': role, 'content': content})

def ChatBotAI(prompt):
    try:
        with open('ChatLog.json', 'r') as f:
            messages = load(f)
    except FileNotFoundError:
        messages = []

    llm = LLM(messages=[{'role': 'system', 'content': "You are an AI assistant."}], model='gpt-3.5-turbo')

    llm.add_message('user', content=prompt)
    answer = llm.run(prompt)

    messages.append({'role': 'assistant', 'content': answer})
    with open('ChatLog.json', 'w') as f:
        dump(messages, f, indent=4)

    return answer

if __name__ == '__main__':
    print(ChatBotAI('What can you see in the image?'))
