from parsing.loader import load_pdf
from parsing.chunker import chunk_document
from embeddings.encoder import embed_chunks, embed_query
from embeddings.vector_store import add_chunks, query
from generation.prompt_builder import build_prompt
from generation.response_generator import generate_answer
from generation.citations import extract_citations, format_sources_block

question = "What does the literature review section discuss?"
q_vec = embed_query(question)
results = query(q_vec, top_k=3)

prompt, used_chunks = build_prompt(question, results)
answer = generate_answer(prompt)
sources = extract_citations(answer, used_chunks)

print(answer)
print(format_sources_block(sources))