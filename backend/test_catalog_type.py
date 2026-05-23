import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(r"D:\PrismAI\backend\.env")
from ingestion.storage import get_supabase

sb = get_supabase()
result = sb.table("features").select("name").limit(3).execute()
print(type(result.data))
print(result.data)
