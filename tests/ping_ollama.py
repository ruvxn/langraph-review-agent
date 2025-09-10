from langchain_community.chat_models import ChatOllama
llm = ChatOllama(model="llama3.2:latest", temperature=0, format="json")
resp = llm.invoke([{"role":"user","content":"Return exactly this JSON: {\"hello\":\"world\"}"}])
print("RAW:", resp.content)
