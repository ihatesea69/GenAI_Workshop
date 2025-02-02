import streamlit as st
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
from openai import OpenAI
import json

# Load embedding model
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    return tokenizer, model

def compute_embedding(text, tokenizer, model):
    """Compute embeddings for text using the transformer model"""
    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        output = model(**tokens)
    return output.last_hidden_state.mean(dim=1).squeeze().numpy()

def process_table_chunks(df, chunk_size=5):
    """Split table into manageable chunks"""
    return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

def analyze_data_with_ai(client, data, data_type="table"):
    """Analyze data using OpenAI's GPT model"""
    prompt = f"""
    Analyzing {data_type} data:
    {data}
    
    Please provide:
    1. Key patterns and trends
    2. Notable relationships between variables
    3. Potential business insights
    4. Anomalies or interesting findings
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analysis expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def main():
    st.title("🧠 Multi-Agent Knowledge Embedding System")
    st.write("""
    ### Embedding Knowledge for Multi-Agent Systems
    This solution demonstrates:
    - Unified embedding space for different data types
    - Table chunking and processing
    - Inter-agent communication through embeddings
    """)

    # Initialize models
    tokenizer, model = load_model()
    
    # File upload section
    uploaded_file = st.file_uploader("📊 Upload your data (CSV, JSON)", type=["csv", "json"])
    
    if uploaded_file is not None:
        try:
            # Process different file types
            file_type = uploaded_file.name.split('.')[-1]
            if file_type == 'csv':
                data = pd.read_csv(uploaded_file)
                st.write("### 📈 Data Preview:")
                st.dataframe(data.head())
                
                # Process table in chunks
                chunks = process_table_chunks(data)
                st.write(f"Split into {len(chunks)} chunks for processing")
                
                # Compute embeddings for each chunk
                embeddings = []
                for chunk in chunks:
                    chunk_text = chunk.to_string()
                    embedding = compute_embedding(chunk_text, tokenizer, model)
                    embeddings.append(embedding)
                
                st.success("✅ Embeddings computed for all chunks")
                
                # Visualize embeddings distribution
                fig, ax = plt.subplots()
                embedding_norms = [np.linalg.norm(emb) for emb in embeddings]
                ax.hist(embedding_norms, bins=20)
                ax.set_title("Distribution of Embedding Magnitudes")
                st.pyplot(fig)
                
            elif file_type == 'json':
                data = json.load(uploaded_file)
                st.write("### 📋 JSON Data Preview:")
                st.json(data)
                
                # Compute embeddings for JSON structure
                json_text = json.dumps(data, indent=2)
                embedding = compute_embedding(json_text, tokenizer, model)
                st.success("✅ Embeddings computed for JSON data")
            
            # AI Analysis section
            st.write("### 🤖 AI Analysis")
            if st.button("Analyze Data"):
                client = OpenAI()  # Make sure to set your API key in environment variables
                analysis = analyze_data_with_ai(client, data)
                st.write(analysis)
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main() 