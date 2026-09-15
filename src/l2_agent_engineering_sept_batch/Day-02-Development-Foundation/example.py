"""Session 2: make one Ollama call and read the response it sends back."""

import sys

import ollama

#sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


MODEL = "gpt-oss:120b-cloud"

request = input("Enter an IT request: ")

response = ollama.chat(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Classify the request in one word."},
        {"role": "user", "content": request},
    ],
)

#print("Category:", response["message"]["content"])

print(response)
