from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables from the .env file
env_vars = dotenv_values('.env')

# Get the input language setting from the environment variables
InputLanguage = env_vars.get("InputLanguage", "en")  # Default to English if not found

# Define the HTML code for the speech recognition interface.
Htmlcode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script> 
        const output = document.getElementById("output");
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "{InputLanguage}";
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            }};

            recognition.onend = function() {{
                recognition.start();
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            recognition.stop();
            output.innerHTML = "";
        }}
    </script>
</body>
</html>'''

# Write the modified HTML code to a file.
os.makedirs("Data", exist_ok=True)  # Ensure directory exists
with open("Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(Htmlcode)

# Get the current working directory.
current_directory = os.getcwd() 
# Generate the file path for the HTML file.
Link = os.path.join(current_directory, "Data", "Voice.html")

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless")  # Fixed: Used correct headless argument

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = os.path.join(current_directory, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)  # Ensure directory exists

# Function to set the assistant's status by writing to a file.
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whose', 'whom', 'can you', "what's", "where's", "how's"]

    if any((word + ' ' in new_query for word in question_words)):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '?'
        else:
            new_query += '?'
        return new_query.capitalize()

    if query_words[-1][-1] in ['.', '?', '!']:
        new_query = new_query[:-1] + '.'
    else:
        new_query += '.'

    return new_query.capitalize()

# Function to translate text into English using the mtranslate library.
def UniversalTranslator(text):
    try:
        return mt.translate(text, "en")
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Function to perform speech recognition.
def SpeechRecognition():
    driver.get("file:///" + Link)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text

            if Text:
                driver.find_element(By.ID, "end").click()

                if "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating ...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception:
            pass

def STT():
    """Wrapper for the SpeechRecognition function."""
    return STT()

# Main execution block.
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
