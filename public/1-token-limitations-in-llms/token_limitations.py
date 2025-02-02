import streamlit as st
import textwrap
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

def main():
    st.title("🔄 Smart Document Processing with Token Management")
    st.write("""
    ### Handling Large Documents with Token Limitations
    This solution demonstrates how to process large documents by:
    - Breaking them into manageable chunks
    - Using vector storage for efficient retrieval
    - Implementing RAG (Retrieval Augmented Generation)
    """)

    # File upload section
    uploaded_file = st.file_uploader("📄 Upload your document (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"])

    if uploaded_file is not None:
        # Read and display document preview
        text = uploaded_file.read().decode("utf-8")
        st.write("### 📝 Document Preview:")
        st.text(textwrap.shorten(text, width=500, placeholder="..."))

        # Chunking with progress
        with st.spinner('Splitting document into chunks...'):
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=512,
                chunk_overlap=50,
                length_function=len
            )
            chunks = text_splitter.split_text(text)
            st.success(f"✅ Document split into {len(chunks)} manageable chunks")

        # Vector storage setup
        with st.spinner('Creating vector embeddings...'):
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_texts(chunks, embeddings)
            st.success("✅ Vector database created")

        # RAG Implementation
        st.write("### 🔍 Ask Questions About Your Document")
        query = st.text_input("Enter your question:")
        
        if query:
            # Create retrieval chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=OpenAI(),
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
            )
            
            with st.spinner('Searching and generating response...'):
                # Get relevant chunks
                docs = vectorstore.similarity_search(query, k=3)
                st.write("#### 📚 Retrieved Relevant Chunks:")
                for i, doc in enumerate(docs, 1):
                    with st.expander(f"Chunk {i}"):
                        st.write(doc.page_content)
                
                # Generate response
                response = qa_chain.run(query)
                st.write("#### 🤖 AI Response:")
                st.write(response)

if __name__ == "__main__":
    main() 