from json import load, dump
from dotenv import dotenv_values
from os import environ
from googlesearch import search
from groq import Groq
import datetime

# Load environment variables
env_vars = dotenv_values('.env')

# Globals
api_key = environ.get('GroqAPIKey')
if not api_key:
    raise ValueError("API key not found in environment variables.")
client = Groq(api_key=api_key)
default_messages = [{'role': 'user', 'content': f"Hello {environ['AssistantName']}, How are you?"}, 
                    {'role': 'assistant', 'content': f"Welcome Back {environ['Username']}, I am doing well. How may I assist you?"}]

# Load or create chat log
try:
    with open('ChatLog.json', 'r') as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    with open('ChatLog.json', 'w') as f:
        json.dump(default_messages, f, indent=4)
    messages = default_messages

def GoogleSearch(query: str) -> str:
    """Performs a Google search and returns formatted results."""
    results = list(search(query, advanced=True, num_results=5))
    answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    answer += "[end]"
    return answer

def AnswerModifier(answer: str) -> str:
    """Cleans up the AI's answer, removing unnecessary line breaks and content."""
    lines = answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def RealTimeChatBotAI(prompt: str) -> str:
    """Processes the user query, performs a real-time search, and returns the chatbot's response."""
    global messages
    
    # Load messages (redundancy removed)
    try:
        with open('ChatLog.json', 'r') as f:
            messages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        messages = default_messages
    
    # Add Google Search results to SystemChat
    search_results = GoogleSearch(prompt)
    system_message = {'role': 'system', 'content': f"Search results for '{prompt}':\n{search_results}"}
    system_chat = [{'role': 'system', 'content': f"Hello, I am {environ['Username']}, You are a very accurate and advanced AI chatbot named {environ['AssistantName']} which has real-time up-to-date information from the internet.\n*** Just answer the question from the provided data in a professional way. ***"}]
    system_chat.append(system_message)

    # Send request to Groq API
    try:
        completion = client.chat.completions.create(
            model='llama3-70b-8192',  # Updated model
            messages=system_chat + messages, 
            temperature=0.7, 
            max_tokens=2048, 
            top_p=1, 
            stream=True, 
            stop=None
        )
        
        # Process the AI response in chunks
        answer = ''
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = answer.strip().replace('</s>', '')
        
        # Append the response to messages
        messages.append({'role': 'assistant', 'content': answer})
        
        # Save updated chat log
        with open('ChatLog.json', 'w') as f:
            json.dump(messages, f, indent=4)
        
        return AnswerModifier(answer)
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    while True:
        prompt = input("Enter your query: ")
        print(RealTimeChatBotAI(prompt))
