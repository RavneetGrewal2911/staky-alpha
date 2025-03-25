from flask import Flask, render_template,request
from groq import Groq
import markdown
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


# Initialize the Groq client
client = Groq( api_key=os.getenv('API_KEY')) 


app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/workshop")
def workshop():
    return render_template('workshop.html')

@app.route("/file_upload", methods=['POST'])
def file_upload():
    
    file = request.files['file']
    
    

   
    filename = file.filename # Replace with your audio file!

    # Open the audio file
    
        # Create a transcription of the audio file
    transcription = client.audio.transcriptions.create(
    file=(filename, file.read()), # Required audio file
    model="whisper-large-v3-turbo", # Required model to use for transcription
    
    )
        # Print the transcription text
    #print(transcription.text)
    
    
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "summarize the given data in in a well arranged manner. use headings and subheadings without overdoing it and make sure they are the best posible way to summarize the given data. do not use hr elements. do not include any message from your side. you are dealing with important data so make sure that you dont miss any inportant details in it.give your answer in markdown format ",
        },
        {
            "role": "user",
            "content": transcription.text,
        }
        ],
    model="llama3-70b-8192",
)

    
    result = chat_completion.choices[0].message.content 
    
    
    
    return render_template('result.html',result=markdown.markdown(result))

if __name__ == '__main__':
    app.run(debug=True)