from langgraph.graph import StateGraph, END
from loader import load_document, chunk_documents, store_vector
from retriever import check_compliance
from generator import generate_report, convert_json_to_txt
from mailer import send_report_email



def node_load_and_chunk(state):
    doc_path = state["doc_path"]
    print("📂 Loading document...")
    docs = load_document(doc_path)

    print("✂️ Chunking document...")
    chunks = chunk_documents(docs)

    print("💾 Storing in VectorDB...")
    store_vector(chunks, db_type="docs")

    return {"chunks": chunks}


def node_check_compliance(state):
    print("⚖️ Running compliance checks...")
    flagged = []
    for chunk in state["chunks"]:
        result = check_compliance(chunk.page_content)
        flagged.append({
            "chunk": chunk.page_content,
            "result": result
        })
    return {"flagged": flagged}


def node_generate_report(state):
    print("📝 Generating report...")
    report_json = generate_report(state["flagged"])
    report_txt = convert_json_to_txt(report_json)
    return {"report_json": report_json, "report_txt": report_txt}


def node_send_email(state):
    print("📧 Sending report via email...")
    try:
        send_report_email(
            to_email="ary4nrajput2004@gmail.com",  
            subject="Compliance Report",
            body="Hello, please find attached the compliance report for your contract.",
            attachment_path=state["report_txt"]
        )
        return {"email_status": "sent"}
    except Exception as e:
        return {"email_status": f"failed: {e}"}


# --- BUILD GRAPH ---
def build_graph():
    graph = StateGraph(dict)

    graph.add_node("load_chunk", node_load_and_chunk)
    graph.add_node("check", node_check_compliance)
    graph.add_node("report", node_generate_report)
    graph.add_node("email", node_send_email)

    graph.set_entry_point("load_chunk")
    graph.add_edge("load_chunk", "check")
    graph.add_edge("check", "report")
    graph.add_edge("report", "email")
    graph.add_edge("email", END)

    return graph.compile()

if __name__ == "__main__":
    doc_path = "data/ChromaDB_docs/sample_contract.txt" 
    app = build_graph() 
    result = app.invoke({"doc_path": doc_path})
    print("\n=== COMPLIANCE PIPELINE COMPLETE ===")
    print(result)
