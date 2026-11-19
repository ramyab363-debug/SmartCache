
import csv
import io
import streamlit as st

from cache import SemanticCache


# Page configuration
st.set_page_config(
    page_title="SmartCache",
    page_icon="⚡",
    layout="wide"
)

# Application heading
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

                st.info("Cache MISS! Generating a response using Gemma via Ollama.")

                if result["matched_question"] is not None:

                    st.write("**Closest cached question:**")
                    st.info(result["matched_question"])

                    st.metric(
                        "Best Similarity Score",
                        f'{result["similarity"]:.3f}'
                    )

                else:
                    st.caption(
                        "No previous cached questions to compare."
                    )

            st.write("### Answer")
            st.write(result["answer"])

            st.caption(
                f'Processing time: {result["latency"] * 1000:.2f} ms'
            )

        except ValueError as error:
            st.warning(str(error))


st.divider()


# Performance Monitoring
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


# Cache Storage
st.header("💾 Cache Storage")

st.metric("Saved Questions", len(cache.cache))


st.divider()


# Cache Explorer Dashboard
st.header("🔍 Cache Explorer")

st.write(
    "Explore and manage questions and answers "
    "currently stored in your semantic cache."
)


# Search cached questions
search_query = st.text_input(
    "Search cached questions:",
    placeholder="Enter a keyword..."
)


# Filter cache entries
filtered_cache = [
    item for item in cache.cache
    if search_query.lower() in item["question"].lower()
]


# Display cache statistics
col1, col2 = st.columns(2)

col1.metric("Total Cache Entries", len(cache.cache))
col2.metric("Filtered Entries", len(filtered_cache))


st.divider()


# Export cache entries to CSV
if filtered_cache:

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(["Question", "Answer"])

    for item in filtered_cache:

        writer.writerow([
            item["question"],
            item["answer"]
        ])

    st.download_button(
        label="📥 Download Cache as CSV",
        data=output.getvalue(),
        file_name="smartcache_export.csv",
        mime="text/csv"
    )


st.divider()


# Display saved entries
if filtered_cache:

    for index, item in enumerate(filtered_cache, start=1):

        with st.expander(
            f"Cache Entry {index}: {item['question']}"
        ):

            st.write("**Question:**")
            st.write(item["question"])

            st.write("**Stored Answer:**")
            st.write(item["answer"])

            st.caption("Embedding Dimension: 384")

            st.caption(f"Created at (IST): {item['created_at']}"
        )

            # Delete cache entry
            if st.button(
                "🗑️ Delete Entry",
                key=f"delete_{index}_{item['question']}"
            ):

                deleted = cache.delete_entry(
                    item["question"]
                )

                if deleted:
                    st.success(
                        "Cache entry deleted successfully!"
                    )
                    st.rerun()

                else:
                    st.warning(
                        "Entry could not be deleted."
                    )

else:
    st.info("No matching cache entries found.")
