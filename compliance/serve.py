from fastapi import FastAPI
from pydantic import BaseModel
from graph import build_graph
from loader import load_document, chunk_documents, store_vector

rules_path = "data/ChromaDB_rules/sample_rules.txt"
rules_docs = load_document(rules_path)
rules_chunks = chunk_documents(rules_docs)
rules_db = store_vector(rules_chunks, db_type="rules")
print(f"📊 Rules DB documents: {rules_db._collection.count()}")

chain = build_graph()

class PolicyCheckInput(BaseModel):
    documents: str

class PolicyCheckOutput(BaseModel):
    result: str

app = FastAPI(
    title="Policy Checker API",
    version="1.0",
    description="Agentic AI policy checker powered by Groq + LangServe"
)

@app.post("/policy-checker", response_model=PolicyCheckOutput)
def inject_rules_db(inputs):
    print("📩 Incoming inputs:", inputs)

    retrieved_rules = rules_db.as_retriever(search_kwargs={"k": 3}).get_relevant_documents(inputs)
    print("📚 Retrieved rules:", retrieved_rules)

    inputs["rules"] = retrieved_rules
    result = chain.invoke(inputs)
    print("✅ Chain output:", result)

    return result


@app.get("/")
def root():
    return {"message": "✅ Policy Checker API is running with Groq!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

