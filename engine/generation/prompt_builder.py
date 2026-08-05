"""
engine/generation/prompt_builder.py

Turns retrieved chunks + a user question into a prompt that forces
the LLM to answer only from the given context and to say so
explicitly when it can't. Also tags each chunk with a short
reference label (e.g. [1], [2]) so the model can cite inline and
we can map those labels back to real page/section info afterward.
"""

MAX_CONTEXT_CHARS = 3000  # keeps prompt small enough for fast CPU-bound generation


def build_prompt(question: str, chunks: list[dict], conversation_history: list[dict] | None = None) -> str:
    """
    chunks: list of result dicts from vector_store.query() (chunk_id,
    text, document_id, page_start, page_end, section, distance).

    conversation_history: optional list of {"role": "user"/"assistant",
    "content": str} from a prior turn, used to resolve references like
    "summarize that" or "compare it with X".

    Returns the full prompt string ready to send to the LLM.
    """
    context_block, used_chunks = _build_context_block(chunks)

    history_block = ""
    if conversation_history:
        history_lines = [
            f"{turn['role'].capitalize()}: {turn['content']}" for turn in conversation_history[-4:]
        ]
        history_block = "Conversation so far:\n" + "\n".join(history_lines) + "\n\n"

    prompt = f"""You are a research assistant that answers questions using ONLY the provided context.

Rules:
- Answer using only the information in the context below. Do not use outside knowledge.
- When you state a fact, cite it inline using its reference number, like [1] or [2].
- If the answer is not contained in the context, respond exactly with: "I couldn't find this information in your uploaded sources."
- Do not guess or make up information that isn't in the context.

{history_block}Context:
{context_block}

Question: {question}

Answer (cite sources inline using [1], [2], etc.):"""

    return prompt, used_chunks


def _build_context_block(chunks: list[dict]) -> tuple[str, list[dict]]:
    """
    Formats chunks into a numbered context block, stopping once
    MAX_CONTEXT_CHARS is reached so the prompt stays a reasonable
    size for CPU-bound generation. Returns the block text plus the
    list of chunks actually included (with their reference number
    attached), so citations.py can map [1]/[2] back to real sources.
    """
    lines = []
    used_chunks = []
    running_len = 0

    for i, chunk in enumerate(chunks, start=1):
        entry = f"[{i}] (Section: {chunk.get('section') or 'N/A'}, Page {chunk['page_start']})\n{chunk['text']}\n"

        if running_len + len(entry) > MAX_CONTEXT_CHARS and used_chunks:
            break

        lines.append(entry)
        running_len += len(entry)

        chunk_with_ref = dict(chunk)
        chunk_with_ref["ref_number"] = i
        used_chunks.append(chunk_with_ref)

    return "\n".join(lines), used_chunks