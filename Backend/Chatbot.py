# Import required libraries and modules
from groq import Groq
from json import load, dump
import datetime
from dotenv import load_dotenv
from os import environ

# Load environment variables
load_dotenv()

# Initialize the Groq API client
client = Groq(api_key=environ.get('GroqAPIKey'))

# Define system message
System = (
    f"Hello, I am {environ.get('Username', 'User')}, you are a very accurate and advanced AI chatbot named {environ.get('AssistantName', 'Jarvis')} "
    f"which also has real-time up-to-date information from the internet.\n"
    "*** Do not tell time unless I ask, do not talk too much, just answer the question. ***\n"
    "*** Provide answers in a professional way. Make sure to use proper grammar with full stops, commas, and question marks. ***\n"
    "*** Reply in the same language as the question: Hindi in Hindi, English in English. ***\n"
    "*** Do not mention your training data or provide notes in the output. Just answer the question. ***"
)

SystemChatBot = [{'role': 'system', 'content': System}]

DefaultMessage = [
    {'role': 'user', 'content': f"Hello {environ.get('AssistantName', 'Jarvis')}, how are you?"},
    {'role': 'assistant', 'content': f"Welcome back {environ.get('Username', 'User')}, I am doing well. How may I assist you?"}
]

# Load chat history
try:
    with open('ChatLog.json', 'r') as f:
        messages = load(f)
except (FileNotFoundError, ValueError):  # ValueError in case of corrupted JSON
    messages = DefaultMessage
    with open('ChatLog.json', 'w') as f:
        dump(messages, f, indent=4)

def Information():
    """Provides real-time date and time information."""
    now = datetime.datetime.now()
    return (
        f"Use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H:%M:%S')}\n"
    )

def AnswerModifier(answer):
    """Removes empty lines from the answer."""
    return '\n'.join(line.strip() for line in answer.split('\n') if line.strip())

def ChatBotAI(prompt):
    """Processes chatbot responses using Groq API."""
    global messages  # Ensure we modify the global chat history

    try:
        # Append user input to the chat history
        messages.append({'role': 'user', 'content': prompt})

        # Call the Groq API
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=SystemChatBot + [{'role': 'system', 'content': Information()}] + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1
        )

        # Extract response text
        answer = response.choices[0].message.content.strip()

        # Append assistant's response
        messages.append({'role': 'assistant', 'content': answer})

        # Save chat history
        with open('ChatLog.json', 'w') as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred. Please try again."

if __name__ == '__main__':
    while True:
        user_input = input('Enter Your Question: ')
        if user_input.lower() in ['exit', 'quit']:
            break
        print(ChatBotAI(user_input))
