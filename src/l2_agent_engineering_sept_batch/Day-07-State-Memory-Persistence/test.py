from dotenv import load_dotenv

load_dotenv()

#MODEL = "gpt-oss:120b-cloud"
#from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini-2025-04-14",
)


response = llm.invoke("HEy model ,could you talk about Sachin?")

print(response.content)


response = llm.invoke("could you help me with his age?")

print(response.content)