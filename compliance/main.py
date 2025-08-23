# orchestrator.py
from loader import load_document, chunk_documents, store_vector
from retriever import check_compliance
from generator import generate_report, convert_json_to_txt

def process_document(doc_path: str):
    """
    Full compliance pipeline:
    1. Load & chunk document
    2. Store in ChromaDB
    3. Run compliance checks
    4. Generate report
    """
    print("📂 Loading document...")
    docs = load_document(doc_path)

    print("✂️ Chunking document...")
    chunks = chunk_documents(docs)

    print("💾 Storing in VectorDB...")
    vectordb = store_vector(chunks, db_type="docs")

    print("⚖️ Running compliance checks...")
    flagged = []

    for chunk in chunks:
        
        result = check_compliance(chunk.page_content)
        flagged.append({
            "chunk": chunk.page_content,
            "result": result
        })

    print("📝 Generating report...")
    report = generate_report(flagged)
    txt_report = convert_json_to_txt(report)

    print("\n✅ Compliance check complete!")
    return report



if __name__ == "__main__":
    
    doc_path = "data/ChromaDB_docs/sample_contract.txt"
    report = process_document(doc_path)

    print("\n=== COMPLIANCE REPORT ===\n")
    print(report)
