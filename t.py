import google.generativeai as genai
import google.ai.generativelanguage as glm
from datetime import datetime
import os
from functions import functions
from functions import processCandidates
from config import config

genai.configure(api_key=config["AI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')
prompt = ""

chat = model.start_chat()
print(chat.send_message("hello"))