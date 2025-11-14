### GOOGLE AI STUDIO PROJECT WITH DEPLOYEMENT 

##  Features

 Generate high-quality TTS audio using **Gemini 2.5 Flash TTS**  
 Supports **single** and **multi-speaker** modes  
 Choose different **voices**, **tones**, and **temperature** levels  
 Output in **WAV** and **MP3**  
 Automatically stores generated files in a `/tts_output` folder  OR
 you can also download output from website 

---

##  Requirements
before that you need to cretate  api key in google ai studio 
then i got a api like and i paste that link in my code 
API_KEY = "AIzaSyD7qMkVZublTcKUt1wle6BbP4D8CG5su-k"

# Flask and CORS
Flask==3.0.3
Flask-Cors==4.0.0

# Google Gemini API SDK 
google-genai==0.3.0

#  Audio Processing 
pydub==0.25.1

# Date and File Handling (included in Python) 
 datetime and wave are built-in modules — no need to install them

### 1. Install Dependencies

pip install flask google-genai pydub

### 2.Verify Python & recommended version
In this project i used python 3.11 supports the google ai stdio

Check Python:
python --version

### 3. Create & activate a virtual environment

python -m venv myenv
python -m venv myenv(for activate virtual env)

### 4. Upgrade pip & setuptools(optional but recommended)

pip install --upgrade pip setuptools wheel

### 5. Install FFmpeg (required by pydub for WAV/MP3 conversion)
         1 Go to https://www.gyan.dev/ffmpeg/builds/
         2️ Download “ffmpeg-release-essentials.zip”
         3️ Extract it to C:\ffmpeg
         4️ Add C:\ffmpeg\bin to your PATH
         5️ Verify installation:
              ffmpeg -version

### Verify everything works
       1.PYTHON:python --version
       2.Packages installed:pip list
       3.FFmpeg:ffmpeg -version

###  APP RUNS :
WE GOT THE LINK LIKE :http://127.0.0.1:7860



### 

### deployement steps:

STEP 1 — Make sure your project has these 3 files
   
   app.py
   requirements.txt
   Procfile (web: gunicorn app:app) we need to keep this 
    
STEP 2 — Push your project to GitHub

Run these commands one by one :
      git add .
      git commit -m "mention changes here "
      git push

STEP 3 — Open Render website
STEP 4 — Click “New” → “Web Service”
STEP 5 — Connect your GitHub account
STEP 6 — Configure your service

SET  the settings like this:
    
           Environment → Python
           Build Command:pip install -requirements.txt
           Start command:gunicorn app:app

STEP 7 — Click Deploy
STEP 8 — Wait until you see:

           "Deployment successful"
            "Live"
STEP 9 — Copy your Public URL
    https://your-app.onrender.com
    