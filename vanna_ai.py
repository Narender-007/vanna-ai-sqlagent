from io import StringIO
import pandas as pd
import psycopg2
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from sqlalchemy import create_engine

class VannaAgent(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Initialize the Vanna agent with API key and model configuration
vanna_agent = VannaAgent(config={
    'api_key': 'apikey',
    'model': 'gpt-3.5-turbo-16k'
})

# Database connection details
db_connection_details = {
    'dbname': "dbname", 
    'user': "username", 
    'password': "1234", 
    'host': "localhost", 
    'port': 1234
}

# Create a connection string for SQLAlchemy
connection_string = (
    f"postgresql+psycopg2://{db_connection_details['user']}:"
    f"{db_connection_details['password']}@{db_connection_details['host']}:"
    f"{db_connection_details['port']}/{db_connection_details['dbname']}"
)

# Create a SQLAlchemy engine
sqlalchemy_engine = create_engine(connection_string)

# Create a connection using psycopg2
psycopg2_connection = psycopg2.connect(**db_connection_details)

# Function to run SQL query using SQLAlchemy
def run_sql_query(sql: str) -> pd.DataFrame:
    df = pd.read_sql_query(sql, sqlalchemy_engine)
    return df

# Setting up the Vanna agent with the SQL execution function
vanna_agent.run_sql = run_sql_query
vanna_agent.run_sql_is_set = True
vanna_agent.allow_llm_to_see_data = False

# Function to get response data and generate human-readable response
def get_response_data(question: str):
    generated_sql = vanna_agent.generate_sql(question)
    print("Generated SQL:", generated_sql, type(generated_sql))
    
    df = pd.read_sql_query(generated_sql, sqlalchemy_engine)
    print("DataFrame:", df,len(df))
    
    # Generate a summary of the DataFrame
    if len(df) ==1:
        human_readable_response = vanna_agent.generate_summary(question, df)
        print("Generated Summary:", human_readable_response)
    else:
        human_readable_response = df.to_html(index=False)
        
    return human_readable_response, generated_sql

# Function to get AI agent response
def ai_agent_response(question: str):
    if question:
        response_message, sql_generated_query = get_response_data(question)
        response = {
            'question': question,
            'sql_query': sql_generated_query,
            'answer': response_message
        }
        return response_message
    else:
        return {'error': 'No question provided'}
