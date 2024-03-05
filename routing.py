import os
import markdown
from flask import render_template, redirect, request
from ai import aiResponse
from config import config


def strip_file_extension(filename):
  last_dot_index = filename.rfind('.')
  if last_dot_index != -1:
    return filename[:last_dot_index]
  return filename


def find_file(query: str) -> str | None:
  query = query.lower()

  current_dir = os.getcwd()

  templates_dir = os.path.join(current_dir, 'templates')

  if os.path.exists(templates_dir) and os.path.isdir(templates_dir):
    template_files = os.listdir(templates_dir)

    for file_name in template_files:
      if file_name.lower().startswith(query):
        return os.path.join(templates_dir, file_name)

  return None


def kebab_case(string: str) -> str:
  string = string.replace("_", "-")
  string = string.lower()
  return string


def getWebpage(route: str) -> str:
  formatted_route = kebab_case(route)

  if config["ALLOW_COMPOUND_ROUTES"] and "/" in route:
    formatted_route = formatted_route.replace("/", "-")

  if formatted_route in ("/", "index", "index.html"):
    return render_template("index.html")

  file_path = find_file(formatted_route)

  if file_path:
    with open(file_path, 'r') as file:
      return file.read()

  ai = aiResponse(formatted_route)

  if ai == "REFUSED":
    return "Not allowed."

  md = markdown.markdown(ai)
  return render_template("base.html", content=md)
