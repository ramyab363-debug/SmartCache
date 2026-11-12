
import streamlit as st
from cache import SemanticCache

st.set_page_config(
    page_title="SmartCache",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ SmartCache")
st.subheader("Intelligent Semantic Caching for LLM Applications")

st.write(
    "Reduce unnecessary AI API calls "
    "using semantic similarity and vector search."
)

st.divider()

# Create cache once per user session
if "semantic_cache" not in st.session_state:
    st.session_state.semantic_cache = SemanticCache()

cache = st.session_state.semantic_cache

# Question input
question = st.text_input("Ask your question:")

if st.button("Submit Question"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            result = cache.get_answer(question)

            if result["status"] == "HIT":
                st.success("⚡ Cache HIT! Reusing saved answer.")

                st.metric(
                    "Similarity Score",
                    f'{result["similarity"]:.3f}'
                )

                st.write("**Matched cached question:**")
                st.info(result["matched_question"])

            else:
                st.info("Cache MISS! Generating a new demo answer.")

            st.write("### Answer")
            st.write(result["answer"])

            st.caption(
                f'Processing time: {result["latency"] * 1000:.2f} ms'
            )

        except ValueError as error:
            st.warning(str(error))

st.divider()

# Performance monitoring
st.header("📊 Performance Monitoring")

total_requests = cache.hit_count + cache.miss_count

hit_rate = (
    cache.hit_count / total_requests * 100
    if total_requests > 0 else 0
)

average_latency = (
    cache.total_latency / total_requests * 1000
    if total_requests > 0 else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Cache Hits", cache.hit_count)
col2.metric("Cache Misses", cache.miss_count)
col3.metric("Cache Hit Rate", f"{hit_rate:.2f}%")

st.metric(
    "Average Processing Time",
    f"{average_latency:.2f} ms"
)

st.caption(
    "Metrics cover the current application session only. "
    "Processing time measures SmartCache operations, "
    "not a real LLM API response."
)

st.divider()

st.header("💾 Cache Storage")
st.metric("Saved Questions", len(cache.cache))
