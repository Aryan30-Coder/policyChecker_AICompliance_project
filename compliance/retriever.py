from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import json


from loader import HuggingFaceEmbeddings

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
embedder = HuggingFaceEmbeddings(model = "all-MiniLM-L6-v2")


def load_vectordb(db_type="docs"):
    persist_directory = f"data/ChromaDB_{db_type}"
    embedder = HuggingFaceEmbeddings(model = "all-MiniLM-L6-v2")
    return Chroma(
        embedding_function=embedder,  
        persist_directory=persist_directory
    )

docs_db = load_vectordb("docs")
rules_db = load_vectordb("rules")
print("Loaded rules:", len(rules_db._collection.get()['documents']))
print("📊 Rules DB documents:", rules_db._collection.count())


llm = ChatGroq(model="llama3-70b-8192", api_key = groq_api_key)

compliance_prompt = ChatPromptTemplate.from_template("""
You are a compliance checker.  
Compare this contract section to the compliance rule.  

Section:
{doc_chunk}

Rule:
{rule_chunk}

Answer:
1. Is it compliant? (Yes/No)
2. If No, explain why.
3. Suggest a corrected version of the text.
""")

def check_compliance(doc_text: str):
    results = rules_db.similarity_search(doc_text, k=1)
    rule_match = results[0].page_content if results else "⚠️ No matching rule found."

    prompt = compliance_prompt.format_messages(
        doc_chunk=doc_text,
        rule_chunk=rule_match
    )
    response = llm.invoke(prompt)

    content = response.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "compliant": False,
            "reason": "LLM returned invalid JSON.",
            "suggestion": content
        }


def run_checker():
    doc_chunks = docs_db.similarity_search("all", k=5)  
    for chunk in doc_chunks:
        result = check_compliance(chunk.page_content)
        print("📄 Doc:", chunk.page_content[:200], "...")
        print("✅ Result:", result)
        print("-" * 80)