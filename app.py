import os

import streamlit as st
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(page_title="Knowledge Desk", page_icon="K", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink: #edf4f0; --muted: #9aaca5; --mint: #17352f; --paper: #101917; --panel: #17231f; --line: #2b3d37; --accent: #f08a5b; }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background: #0c1412; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding: 2rem 1.35rem; }
    h1, h2, h3, [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; }
    .brand { display: flex; align-items: center; gap: .7rem; margin-bottom: 2.5rem; }
    .brand-mark { display: grid; place-items: center; width: 2.25rem; height: 2.25rem; border-radius: 9px; background: var(--accent); color: white; font: 700 1rem 'Space Grotesk'; }
    .brand-name { font: 700 1.1rem 'Space Grotesk'; letter-spacing: .01em; }
    .eyebrow { color: var(--accent); font: 700 .72rem 'Space Grotesk'; letter-spacing: .13em; text-transform: uppercase; }
    .hero { padding: 1.2rem 0 1.8rem; border-bottom: 1px solid var(--line); margin-bottom: 1.8rem; }
    .hero h1 { font-size: clamp(2.1rem, 4vw, 3.65rem); line-height: 1.02; margin: .35rem 0 .8rem; max-width: 740px; }
    .hero p { max-width: 620px; color: var(--muted); font-size: 1.02rem; line-height: 1.6; }
    .empty { padding: 3.5rem 1rem 4rem; text-align: center; border: 1px dashed #40574e; border-radius: 10px; background: var(--panel); }
    .empty h2 { font-size: 1.45rem; margin: .4rem 0; }
    .empty p { color: var(--muted); margin: 0 auto; max-width: 500px; line-height: 1.55; }
    .source-card { padding: .9rem 1rem; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); margin-top: .6rem; }
    .source-title { font: 600 .95rem 'Space Grotesk'; }
    .source-meta { color: var(--muted); font-size: .78rem; margin-top: .25rem; }
    .status { padding: .75rem .85rem; border-radius: 8px; background: var(--panel); border: 1px solid var(--line); color: var(--muted); font-size: .84rem; }
    [data-testid="stChatInput"] textarea { background: var(--panel); color: var(--ink); border-color: var(--line); }
    [data-testid="stExpander"] { background: var(--panel); border-color: var(--line); }
    [data-testid="stMarkdownContainer"] a { color: var(--accent); }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    div[data-testid="stChatMessage"] { padding: .75rem 0; }
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { line-height: 1.65; }
    .stButton > button { border-radius: 7px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def backend_status() -> tuple[bool, str]:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    key_names = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
    key_name = key_names.get(provider)
    if key_name and os.getenv(key_name):
        return True, f"{provider.title()} ready"
    return False, f"{provider.title()} needs an API key"


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"Sources used ({len(sources)})", expanded=False):
        for index, source in enumerate(sources, 1):
            metadata = source.get("metadata", {})
            title = metadata.get("title", "Untitled document")
            label = metadata.get("source", "Unknown source")
            score = source.get("score")
            score_text = f"  |  score {float(score):.3f}" if isinstance(score, (int, float)) else ""
            url = metadata.get("url")
            link = f"  |  [{url}]({url})" if url else ""
            st.markdown(
                f"**{index}. {title}**  \n"
                f"<span class='source-meta'>{label}{score_text}{link}</span>",
                unsafe_allow_html=True,
            )
            with st.expander("View excerpt", expanded=False):
                st.caption(source.get("content", ""))


if "messages" not in st.session_state:
    st.session_state.messages = []

ready, status_text = backend_status()

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">K</div><div class="brand-name">Knowledge Desk</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Retrieval controls</div>', unsafe_allow_html=True)
    top_k = st.slider("Sources to retrieve", min_value=3, max_value=10, value=5)
    st.checkbox("Hybrid reranking", value=True, disabled=True)
    st.caption("Dense + BM25 fusion is managed by the retrieval pipeline.")
    st.divider()
    st.markdown("**System status**")
    st.markdown(f'<div class="status">{'Ready' if ready else 'Setup required'}<br>{status_text}</div>', unsafe_allow_html=True)
    st.caption("Add your provider key to `.env`, then restart Streamlit.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown('<div class="hero"><div class="eyebrow">Evidence-first assistant</div><h1>Ask your knowledge base.</h1><p>Search across the team corpus and get answers grounded in retrieved documents, with every source kept close to the response.</p></div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown('<div class="empty"><div class="eyebrow">Start a conversation</div><h2>What would you like to verify?</h2><p>Ask about a policy, a news article, or any detail in the indexed corpus. Retrieved passages and scores will appear below each answer.</p></div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources", []))

query = st.chat_input("Ask a question about your documents...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base..."):
            try:
                from src.task10_generation import generate_with_citation

                result = generate_with_citation(query, top_k=top_k)
                answer = result["answer"]
                sources = result.get("sources", [])
            except Exception as error:
                answer = (
                    "The RAG pipeline is not ready yet. Complete indexing and configure "
                    f"the language model provider before asking this question.\n\n`{error}`"
                )
                sources = []
        st.markdown(answer)
        render_sources(sources)
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
