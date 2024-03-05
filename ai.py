import google.generativeai as genai
import google.ai.generativelanguage as glm
from datetime import datetime
import os
from functions import functions
from functions import processCandidates
from config import config

genai.configure(api_key=config["AI_API_KEY"])
tools = list(map(lambda function: function["tool"] ,functions.values()))
model = genai.GenerativeModel('gemini-pro', tools=tools)
prompt = ""

def aiResponse(query) -> str:
  
  #aiResponse = model.generate_content(messages)
  chat = model.start_chat()#history=messages)
  #aiResponse = chat.send_message(config["AI"]["PROMPT"].replace("{{ topic }}", query.replace("-", " ")))
  aiResponse = chat.send_message(query.replace("-", " "))
  for rating in aiResponse.prompt_feedback.safety_ratings:
    if not str(rating.probability).endswith("NEGLIGIBLE"):
      return "REFUSED"
  while not aiResponse.candidates[0].content.parts[0].text:
    result = processCandidates(aiResponse.candidates)
    #messages.append({
    #  "role": "model"
    #})
    aiResponse = chat.send_message(result)
  return aiResponse.text