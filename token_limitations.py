import streamlit as st
import textwrap
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import io

# Load environment variables
load_dotenv()

# Configure OpenAI API key
if 'OPENAI_API_KEY' not in os.environ:
    st.error('⚠️ OPENAI_API_KEY not found in environment variables. Please add it to .env file.')
    st.stop()

def read_pdf(file):
    """Read text from PDF file"""
    try:
        pdf_reader = PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
        file.seek(0)  # Reset file pointer
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def read_docx(file):
    """Read text from DOCX file"""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file.read()))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        file.seek(0)  # Reset file pointer
        return text.strip()
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return None

def read_file_with_fallback_encoding(file):
    """Try different encodings to read the file"""
    if not file:
        return None
        
    # Check file type
    file_type = file.name.split('.')[-1].lower()
    
    # Handle different file types
    if file_type == 'pdf':
        return read_pdf(file)
    elif file_type == 'docx':
        return read_docx(file)
    elif file_type == 'txt':
        # Handle text files
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                content = file.read()
                if isinstance(content, bytes):
                    text = content.decode(encoding)
                else:
                    text = content
                file.seek(0)  # Reset file pointer
                return text.strip()
            except UnicodeDecodeError:
                file.seek(0)  # Reset file pointer
                continue
        
        raise ValueError("Could not read the file with any of the attempted encodings")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def process_text(text):
    """Process and split text into chunks"""
    if not text or not text.strip():
        return None
        
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=512,
        chunk_overlap=50,
        length_function=len
    )
    
    chunks = text_splitter.split_text(text)
    if not chunks:
        return None
    return chunks

def main():
    st.title("Handling Large Documents with Token Limitations")
   

    # File upload section
    uploaded_file = st.file_uploader("📄 Upload (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"])

    if uploaded_file is not None:
        try:
            # Read document
            text = read_file_with_fallback_encoding(uploaded_file)
            if not text:
                st.error("Could not extract text from the document. Please check if the file is valid and not empty.")
                return

            # Display document preview
            st.write("### 📝 Document Preview:")
            preview_text = textwrap.shorten(text, width=500, placeholder="...")
            st.text_area("Document Content Preview:", preview_text, height=150)

            # Process chunks
            with st.spinner('Splitting document into chunks...'):
                chunks = process_text(text)
                if not chunks:
                    st.error("Could not create chunks from the document. The text might be empty or invalid.")
                    return
                    
                st.success(f"Document split into {len(chunks)} manageable chunks")

            # Vector storage setup
            with st.spinner('Creating vector embeddings...'):
                embeddings = OpenAIEmbeddings()
                vectorstore = FAISS.from_texts(chunks, embeddings)
                st.success("Vector database created")

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
                    if docs:
                        st.write("#### Retrieved Relevant Chunks:")
                        for i, doc in enumerate(docs, 1):
                            with st.expander(f"Chunk {i}"):
                                st.write(doc.page_content)
                        
                        # Generate response
                        response = qa_chain.run(query)
                        st.write("#### AI Response:")
                        st.write(response)
                    else:
                        st.warning("No relevant content found for your question.")
                        
        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")

if __name__ == "__main__":
    main() 