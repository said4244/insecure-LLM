###############################
##  TOOLS
from langchain.agents import Tool
from langchain.tools import BaseTool
from langchain.tools import StructuredTool
import streamlit as st
from datetime import date
from dotenv import load_dotenv
import json
import re
import os
from transaction_db import TransactionDb

load_dotenv()

def get_current_user(input : str):
    db = TransactionDb()
    user = db.get_user(1)
    db.close()
    return user

get_current_user_tool = Tool(
    name='GetCurrentUser',
    func= get_current_user,
    description="Returns the current user for querying transactions."
)

def get_transactions(userId : str):
    """Returns the transactions associated to the userId provided by running this query: SELECT * FROM Transactions WHERE userId = ?."""
    try:
        db = TransactionDb()
        transactions = db.get_user_transactions(userId)
        db.close()
        return transactions
        
    except Exception as e:
        return f"Error: {e}'"
            

get_recent_transactions_tool = Tool(
    name='GetUserTransactions',
    func= get_transactions,
    description="Returns the transactions associated to the userId provided by running this query: SELECT * FROM Transactions WHERE userId = provided_userId."
)


def export_transactions_to_file(user_id):

    try:
        if not os.path.exists("exports"):
            os.makedirs("exports")
        
        #Here we have the vuln: generating a filename based on user_id
        filename = f"transaction-{user_id}" #<----
        file_path = f"exports/{filename}"
        
        # Get the transactions
        db = TransactionDb()
        transactions = db.get_user_transactions(1)
        db.close()
        
        #and here is where the vuln is finalized and executed basically
        command = f"echo '{transactions}' > {file_path}"
        os.system(command)
        
        # Return a link to the file
        return f"Transactions for user {user_id} exported successfully. Access file at: http://192.168.189.131:8502/{file_path}"
        
    except Exception as e:
        return f"Error exporting transactions: {str(e)}"

export_transactions_tool = Tool(
    name='ExportTransactionsToFile',
    func=export_transactions_to_file,
    description="Exports transactions for a specific user to a text file. Input format: user_id (e.g., '1')"
)
