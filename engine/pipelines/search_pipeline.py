"""
engine/pipelines/search_pipeline.py

Ties retrieval + generation into one call: embed the question,
search the vector store (across all ingested documents, or scoped
to one via document_id), build the grounded prompt, generate the
answer, and extract citations. This is what the PyQt UI's query
box should call.
"""

from pathlib import Path

try:
    from ..embeddings.encoder import embed_query
    from ..embeddings.vector_store import query as vector_query
    from ..generation.prompt_builder import build_prompt
    from ..generation.response_generator import generate_answer
    from ..generation.citations import extract_citations, format_sources_block
    from ..conversation.memory import ConversationMemory
except ImportError:
    import sys
    base = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(base / "embeddings"))
    sys.path.insert(0, str(base / "generation"))
    sys.path.insert(0, str(base / "conversation"))
    from encoder import embed_query
    from vector_store import query as vector_query
    from prompt_builder import build_prompt
    from response_generator import generate_answer
    from citations import extract_citations, format_sources_block
    from memory import ConversationMemory

DEFAULT_TOP_K = 5


def ask(
    question: str,
    document_id: str | None = None,
    top_k: int = DEFAULT_TOP_K,
    conversation_history: list[dict] | None = None,
) -> dict:
    """
    Answers a question grounded in the ingested documents.

    document_id: if given, restricts search to that one document
    (e.g. user picked "search only this file" in the UI). If None,
    searches across every ingested document - this is the
    multi-document reasoning case from the README.

    Returns:
      {
        "answer": str,              # the raw generated answer text (with [n] markers)
        "sources": list[dict],      # structured source info, one per citation actually used
        "sources_block": str,       # human-readable "Sources:" text, ready to display
        "retrieved_count": int,     # how many chunks were retrieved before generation
      }
    """
    q_vec = embed_query(question)
    retrieved = vector_query(q_vec, top_k=top_k, document_id=document_id)

    if not retrieved:
        return {
            "answer": "I couldn't find this information in your uploaded sources.",
            "sources": [],
            "sources_block": "",
            "retrieved_count": 0,
        }

    prompt, used_chunks = build_prompt(question, retrieved, conversation_history=conversation_history)
    answer = generate_answer(prompt)
    sources = extract_citations(answer, used_chunks)
    sources_block = format_sources_block(sources)

    return {
        "answer": answer,
        "sources": sources,
        "sources_block": sources_block,
        "retrieved_count": len(retrieved),
    }


def ask_with_memory(
    memory: ConversationMemory,
    question: str,
    document_id: str | None = None,
    top_k: int = DEFAULT_TOP_K,
) -> dict:
    """
    Same as ask(), but pulls conversation history from `memory`
    automatically and records this exchange into it afterward. This
    is what the UI should call for an ongoing chat session - ask()
    stays available directly for one-off/stateless queries.

    Note: retrieval itself still searches using only the raw
    question text, not a history-resolved version of it - so a
    follow-up like "summarize that" may retrieve weakly on its own,
    even though the LLM can still resolve "that" from the history
    included in the prompt. Good enough for now; a query-rewriting
    step (using history to rewrite the question before embedding)
    would improve retrieval on pronoun-heavy follow-ups later.
    """
    history = memory.get_context_for_prompt()
    result = ask(question, document_id=document_id, top_k=top_k, conversation_history=history)

    memory.add_user_message(question)
    memory.add_assistant_message(result["answer"])

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python search_pipeline.py <question1> [question2] [question3] ...")
        print("Each question is asked in sequence within the SAME conversation, so later")
        print("questions can reference earlier ones (e.g. 'summarize that').")
        sys.exit(1)

    memory = ConversationMemory()

    for q in sys.argv[1:]:
        print(f"\n>>> {q}")
        result = ask_with_memory(memory, q)
        print(result["answer"])
        print(result["sources_block"])