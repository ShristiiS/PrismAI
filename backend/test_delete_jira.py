import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(r"D:\PrismAI\backend\.env")
from ingestion.pipeline import delete_file

result = delete_file("test_sprint1_jira")
print(result)
