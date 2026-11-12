from sentence_transformers import SentenceTransformer, util

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

questions = [
    "What is artificial intelligence?",
    "Explain AI.",
    "What is the weather today?"
]

# Generate embeddings
embeddings = model.encode(
    questions,
    convert_to_tensor=True
)

# Compare the questions
similarity_1 = util.cos_sim(
    embeddings[0],
    embeddings[1]
)

similarity_2 = util.cos_sim(
    embeddings[0],
    embeddings[2]
)

print("Question 1:", questions[0])
print("Question 2:", questions[1])
print("Similarity:", similarity_1.item())

print("\nQuestion 1:", questions[0])
print("Question 3:", questions[2])
print("Similarity:", similarity_2.item())