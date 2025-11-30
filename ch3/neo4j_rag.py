from neo4j import GraphDatabase
from transformers import BartTokenizer, BartForConditionalGeneration

# Define the connection credentials for the Neo4j database
uri = "bolt://localhost:7687"  # Replace with your Neo4j URI
username = "neo4j"             # Replace with your Neo4j username
password = "12341234"          # Replace with your Neo4j password

# Create a driver instance to connect to the Neo4j database
driver = GraphDatabase.driver(uri, auth=(username, password))

# Initialize the BART tokenizer and model (RAG uses BART internally)
# Using BART directly since we're retrieving from Neo4j, not using RAG's retriever
tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")

# Function to retrieve relevant data from the Neo4j knowledge graph
def get_relevant_data(prompt):
    """
    Fetch relevant data (plots) for movies that match the user's prompt.
    """
    # Use parameterized query to prevent injection
    query = """
    MATCH (m:Movie)-[:HAS_PLOT]->(p:Plot)
    WHERE m.title CONTAINS $prompt
    RETURN DISTINCT m.title AS title, m.year AS year, p.description AS plot
    """
    with driver.session() as session:
        result = session.run(query, prompt=prompt)
        # Use a set to track unique plots to avoid duplicates
        seen_plots = set()
        records = []
        for record in result:
            if record["plot"] is not None:
                plot_key = (record["title"], record["plot"])
                if plot_key not in seen_plots:
                    seen_plots.add(plot_key)
                    records.append({
                        "title": record["title"],
                        "year": record["year"],
                        "plot": record["plot"],
                    })
        print(f"Retrieved Records: {records}")  # Debugging line
        return records

# Function to generate a response using the BART model
def generate_response(prompt):
    """
    Combine the user's prompt with relevant data from the graph
    and generate a focused, non-repetitive response using the BART model.
    """
    relevant_data = get_relevant_data(prompt)

    if not relevant_data:
        return "No relevant data found for the given prompt."

    # Combine dictionaries in relevant_data into a single string
    # Create a better prompt for the model
    movie_info = "\n".join(
        [f"Movie: {data['title']} ({data['year']})\nPlot: {data['plot']}" for data in relevant_data]
    )
    combined_input = f"Question: Tell me about {prompt}.\n\nContext:\n{movie_info}\n\nAnswer:"

    print(f"Combined Input: {combined_input}")

    if not combined_input.strip():
        return "No relevant data to process for this prompt."

    # Tokenize the combined input with truncation
    max_input_length = 512 - 50  # Leave space for output
    tokenized_input = tokenizer(combined_input, truncation=True, max_length=max_input_length, return_tensors="pt")

    # Generate response with tuned parameters
    outputs = model.generate(
        **tokenized_input,
        max_length=150,
        min_length=20,
        temperature=0.7,
        top_k=50,
        top_p=0.9,
        num_beams=5,
        no_repeat_ngram_size=3,
        early_stopping=True
    )

    # Decode the response with improved formatting
    response = tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return response


# Example prompt provided within the script
prompt = "The Matrix"  # Replace with the movie title you want to query
response = generate_response(prompt)

# Print the AI-generated response
print(f"Prompt: {prompt}\nResponse: {response}")

# Close the database driver
driver.close()
