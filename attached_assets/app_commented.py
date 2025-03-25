"""
Audio Transcription and Summarization Application - Original Prototype

This module demonstrates the basic functionality for transcribing and summarizing
audio files using the Groq API. This is the initial prototype that was expanded
into a full application in main.py.

Dependencies:
- Flask for web framework
- Groq for AI model access
- Markdown for formatting summaries
- Python-dotenv for environment variable management
"""

from flask import Flask, render_template, request
from groq import Groq
import markdown
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# This includes API keys for the Groq service
load_dotenv()

# Initialize the Groq client
# This client is used to access Groq's AI models for transcription and summarization
client = Groq(api_key=os.getenv('API_KEY'))

# Initialize Flask application
app = Flask(__name__)

@app.route("/")
def hello_world():
    """
    Landing page route
    Displays the main welcome page
    """
    return render_template('index.html')

@app.route("/workshop")
def workshop():
    """
    Transcription workshop route
    Displays the file upload interface
    """
    return render_template('workshop.html')

@app.route("/file_upload", methods=['POST'])
def file_upload():
    """
    File upload processing route
    
    Handles the audio file upload, sends it to Groq for transcription,
    then sends the transcription to Groq for summarization.
    
    This is a simplified version of the file_upload route in main.py,
    which includes more features like browser recording and database integration.
    """
    # Get the uploaded file from the request
    file = request.files['file']
    
    # Extract filename for processing
    filename = file.filename
    
    # Transcribe the audio file using Groq/Whisper API
    transcription = client.audio.transcriptions.create(
        file=(filename, file.read()),  # Pass filename and file content
        model="whisper-large-v3-turbo",  # Use Whisper large model for accuracy
    )
    
    # Generate a summary of the transcription using Groq's LLM
    chat_completion = client.chat.completions.create(
        messages=[
            {
                # System prompt to guide the AI in creating a well-structured summary
                "role": "system",
                "content": "summarize the given data in in a well arranged manner. use headings and subheadings without overdoing it and make sure they are the best posible way to summarize the given data. do not use hr elements. do not include any message from your side. you are dealing with important data so make sure that you dont miss any inportant details in it.give your answer in markdown format ",
            },
            {
                # User message containing the transcription to summarize
                "role": "user",
                "content": transcription.text,
            }
        ],
        model="llama3-70b-8192",  # Use Llama 3 70B model for high-quality summarization
    )
    
    # Extract the summary text from the AI response
    result = chat_completion.choices[0].message.content
    
    # Render the result page with the markdown-formatted summary
    return render_template('result.html', result=markdown.markdown(result))

# Run the Flask application in debug mode if directly executed
if __name__ == '__main__':
    app.run(debug=True)