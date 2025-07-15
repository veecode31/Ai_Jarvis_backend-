from groq import Groq #Importing the Groq library to use its API.
from json import load, dump # Importing functions to read and write JSON files.
import datetime #Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values
from openai import completions # Importing dotenv_values to read environment variables from a .env file.

 #Load environment variables from the env file.
env_vars = dotenv_values(".env") 

# Retrieve environment variables with fallback default values
Username = env_vars.get("Username") or "Vedant Dualm"
Assistantname = env_vars.get("Assistantname") or "Jarvis"
GroqAPIKey = env_vars.get("GroqAPIKey")

 #Initialize the Groq client using the provided API key.
client = Groq(api_key = GroqAPIKey) 

 #Initialize an empty list to store chat messages.
messages = [] 

 #Define a system message that provides context to the AI ChatBot about its role and Bheaviour.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

#A list of System instructions for the chatbot.
SystemChatBot = [
    {'role': 'system', 'content': System},
    {'role': 'user', 'content': 'Hi'},
    {'role': 'assistant', 'content': f'Hello {Username}, how can I help you?'}
]



# Attempt to load the chat log from a JSON file.
try:
    with open(r'Data\ChatLog.json', 'r') as f:
        messages = load(f)
except FileNotFoundError:
    # If the file does not exist, initialize the chat log with the system message.
    with open(r'Data\ChatLog.json', 'w') as f:
        dump([], f)

# Function to get real-time date and time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()  # Get current date and time
    day = current_date_time.strftime("%A")  # Full weekday name (e.g., Monday)
    date = current_date_time.strftime("%d")  # Day of the month (01-31)
    month = current_date_time.strftime("%B")  # Full month name (e.g., January)
    year = current_date_time.strftime("%Y")  # Year (e.g., 2024)
    hour = current_date_time.strftime("%H")  # Hour in 24-hour format (00-23)
    minute = current_date_time.strftime("%M")  # Minute (00-59)
    second = current_date_time.strftime("%S")  # Second (00-59)
    
    # Corrected formatted string
    data = f"Please use this real-time information if needed:\n" 
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n" 
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n" 
    return data


# Function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    lines = Answer.split("\n") # Split the answer into lines.
    non_empty_lines = [line.strip() for line in lines if line.strip()] # Remove empty lines.
    modified_answer = "\n".join(non_empty_lines) # Join the cleaned lines back together.
    return modified_answer

# Main chatbot function to handle user queries.
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    
    try:
        # Load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Append the user's query to the messages list.
        messages.append({"role": "user", "content": Query})

        # Make a request to the Groq API for a response.
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""  # Initialize an empty string to store the AI's response.

        # Process the streamed response chunks.
        for chunk in completion:
            if hasattr(chunk, 'choices') and chunk.choices:
                for choice in chunk.choices:
                    if hasattr(choice.delta, 'content') and choice.delta.content is not None:
                        Answer += choice.delta.content  # Append content safely

        Answer = Answer.replace("</s>", "")  # Clean up any unwanted tokens

        # Append the chatbot's response to the messages list.
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chat log to the JSON file.
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        # Return the formatted response.
        return AnswerModifier(Answer)

    except Exception as e:
        return f"An error occurred: {e}"


# main program entry point.
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ") # Get user input.
        print(ChatBot(Query = user_input)) # Call the chatbot function with the user's query.        