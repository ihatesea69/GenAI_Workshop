import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI
import json
import sqlparse

class TextToSQLProcessor:
    def __init__(self):
        self.client = OpenAI()
        self.conn = None
        self.schema = None
    
    def connect_to_database(self, db_path):
        """Connect to SQLite database and extract schema"""
        try:
            self.conn = sqlite3.connect(db_path)
            cursor = self.conn.cursor()
            
            # Get table schema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                schema[table_name] = [col[1] for col in columns]
            
            self.schema = schema
            return True
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            return False

    def generate_sql(self, query):
        """Generate SQL from natural language using GPT-4"""
        schema_str = json.dumps(self.schema, indent=2)
        prompt = f"""
        Given the following database schema:
        {schema_str}
        
        Convert this natural language query to SQL:
        "{query}"
        
        Rules:
        1. Use only tables and columns from the schema
        2. Return only the SQL query, no explanations
        3. Ensure the query is optimized and follows best practices
        4. Add appropriate JOIN conditions if multiple tables are needed
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert SQL developer. Generate only SQL queries, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating SQL: {str(e)}"

    def execute_sql(self, sql):
        """Execute SQL query and return results"""
        try:
            # Format SQL for display
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            
            # Execute query
            df = pd.read_sql_query(sql, self.conn)
            return formatted_sql, df
        except Exception as e:
            return formatted_sql, f"Error executing SQL: {str(e)}"

def main():
    st.title("🔍 Natural Language to SQL Assistant")
    st.write("""
    ### Text-to-SQL for Business Applications
    Upload your SQLite database and ask questions in natural language!
    The system will:
    1. Analyze your database schema
    2. Convert your question to SQL
    3. Execute the query and show results
    """)

    # Initialize processor
    processor = TextToSQLProcessor()
    
    # Database upload
    uploaded_file = st.file_uploader("📁 Upload SQLite Database", type=["db", "sqlite", "sqlite3"])
    
    if uploaded_file:
        # Save uploaded file temporarily
        with open("temp.db", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Connect to database
        if processor.connect_to_database("temp.db"):
            st.success("✅ Database connected successfully")
            
            # Display schema
            st.write("### 📋 Database Schema")
            st.json(processor.schema)
            
            # Query input
            query = st.text_input("💭 Ask your question in natural language:", 
                                placeholder="e.g., What were the total sales in the last quarter?")
            
            if query:
                with st.spinner("Converting to SQL..."):
                    sql = processor.generate_sql(query)
                    
                    st.write("### 🔍 Generated SQL")
                    formatted_sql, results = processor.execute_sql(sql)
                    st.code(formatted_sql, language="sql")
                    
                    st.write("### 📊 Query Results")
                    if isinstance(results, pd.DataFrame):
                        st.dataframe(results)
                        
                        # Export options
                        if st.button("Export Results"):
                            csv = results.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name="query_results.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error(results)

if __name__ == "__main__":
    main() 