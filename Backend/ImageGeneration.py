import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from time import sleep

# Load environment variables
load_dotenv()
API_KEY = os.getenv("HuggingFaceAPIKey")

# Check if API key is loaded correctly
if not API_KEY:
    raise ValueError("API key not found. Please check your .env file.")

headers = {"Authorization": f"Bearer {API_KEY}"}
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = "Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores

    # Generate the filenames for the images
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 sec before showing the next image
        except IOError:
            print(f"Unable to open {image_path}")

# Async function to send a query to the Hugging Face API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    tasks = []
    os.makedirs("Data", exist_ok=True)  # Ensure Data folder exists

    # Create 4 image generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High Details, high resolution",
            "parameters": {"seed": randint(0, 1000000)}
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    images_bytes_list = await asyncio.gather(*tasks)

    # Save the generated images to files
    for i, image_bytes in enumerate(images_bytes_list):
        image_path = os.path.join("Data", f"{prompt.replace(' ', '_')}{i + 1}.jpg")
        with open(image_path, "wb") as f:
            f.write(image_bytes)

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Main loop to monitor for image generation requests
while True:
    try:
        # Read the status and prompt from the data file
        with open(r"Frontend/Files/ImageGeneration.data", "r") as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            print(f"Read Data: {line}")  # Debugging line
            try:
                prompt, status = line.split(",")
            except ValueError:
                print(f"Invalid data format: {line}")
                continue
            
            # If the status indicates an image generation request
            if status.strip().lower() == "true":
                print("Generating Images....")
                GenerateImages(prompt.strip())

                # Reset the status in the file after generating images
                with open(r"Frontend/Files/ImageGeneration.data", "w") as f:
                    f.write("False,False\n")
                break  # Exit the loop
        sleep(1)
    except Exception as e:
        print(f"Error: {e}")
