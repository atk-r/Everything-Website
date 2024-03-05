import google.ai.generativelanguage as glm
import google.generativeai as genai
from datetime import datetime
import os
import ast
from config import config
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup

genai.configure(api_key=config["AI_API_KEY"])

def scrape_webpage(url):
  response = requests.get(url)

  if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')

      text = soup.get_text()

      return text
  else:
      print("Failed to fetch the webpage. Status code:", response.status_code)
      return None

def scrape_google(query):
  url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
  header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
  data = requests.get(url, headers=header)
  
  if data.status_code == 200:
      soup = BeautifulSoup(data.content, "html.parser")
      results = []
      for g in soup.find_all('div',  {'class':'g'}):
          anchors = g.find_all('a')
          if anchors:
              link = anchors[0]['href']
              title = g.find('h3').text
              try:
                  description = g.find('div', {'data-sncf':'2'}).text
              except Exception as e:
                  description = "-"
              results.append(str(title)+";"+str(link)+';'+str(description))
      return results
  return "Error"

def safe_eval(expression):
  try:
      parsed_expr = ast.parse(expression, mode='eval')
      allowed_nodes = {ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Name, ast.Load}
      for node in ast.walk(parsed_expr):
          if type(node) not in allowed_nodes:
              raise ValueError("Invalid expression")
      result = eval(expression)
      return result
  except Exception as e:
      return "Error"

functions = {
  "datetime": {
      "tool": glm.Tool(
        function_declarations=[
          glm.FunctionDeclaration(
            name='now',
            description="Returns the current UTC date and time."
          )
        ]
      ),
      "generator": lambda: glm.FunctionResponse(
        name="now",
        response={"datetime": datetime.now.strftime("%Y-%m-%d %H:%M:%S")}
      )
  },
  "calculator": {
    "tool": glm.Tool(
      function_declarations=[
        glm.FunctionDeclaration(
          name="calculator",
          description="Calculates a simple expression",
          parameters=glm.Schema(
            type=glm.Type.STRING,
            properties={
              'equation': glm.Schema(type=glm.Type.STRING)
            },
            required=['equation']
          )
        )
      ]
    ),
    "generator": lambda equation: glm.FunctionResponse(
        name="ai",
        response={"result": safe_eval(equation)}
      )
    },
  # "ai": {
  #   "tool": glm.Tool(
  #     function_declarations=[
  #       glm.FunctionDeclaration(
  #         name="ai",
  #         description="Gets a response from AI",
  #         parameters=glm.Schema(
  #           type=glm.Type.STRING,
  #           properties={
  #             'prompt': glm.Schema(type=glm.Type.STRING)
  #           },
  #           required=['prompt']
  #         )
  #       )
  #     ]
  #   ),
  #   "generator": lambda prompt: glm.FunctionResponse(
  #       name="ai",
  #       response={"result": genai.GenerativeModel('gemini-pro').generate_content(prompt).text}
  #   )
  # },
  # "google": {
  #   "tool": glm.Tool(
  #     function_declarations=[
  #       glm.FunctionDeclaration(
  #         name="google",
  #         description="Searches google for a query",
  #         parameters=glm.Schema(
  #           type=glm.Type.STRING,
  #           properties={
  #             'query': glm.Schema(type=glm.Type.STRING)
  #           },
  #           required=['query']
  #         )
  #       )
  #     ]
  #   ),
  #   "generator": lambda query: glm.FunctionResponse(
  #       name="google",
  #       response={"result": scrape_google(query)}
  #   )
  # },
  # "scraper": {
  #   "tool": glm.Tool(
  #     function_declarations=[
  #       glm.FunctionDeclaration(
  #         name="scraper",
  #         description="Scrapes a webpage given the url",
  #         parameters=glm.Schema(
  #           type=glm.Type.STRING,
  #           properties={
  #             'url': glm.Schema(type=glm.Type.STRING)
  #           },
  #           required=['url']
  #         )
  #       )
  #     ]
  #   ),
  #   "generator": lambda url: glm.FunctionResponse(
  #       name="scraper",
  #       response={"result": scrape_webpage(url)}
  #   )
  # }
}

def processCandidates(candidates) -> glm.Content:
  aiFunction = candidates[0].content.parts[0].function_call
  function = functions.get(aiFunction.name)
  if function:
    result = function["generator"](**aiFunction.args)
    print(f"used {aiFunction.name}")
    return glm.Content(
      parts=[
        glm.Part(
          function_response=result
        )
      ]
    )
  else:
    return glm.Content(
      parts=[
        glm.Part(
          function_response=glm.FunctionResponse(
            name=aiFunction.name,
            response={"error": "Function not found"}
          )
        )
      ]
    )