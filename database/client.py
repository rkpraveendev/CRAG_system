import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()


def load_the_env(name: str) -> str:
    try:
        value = os.getenv(name)
    except Exception as e:
        raise ValueError(f"Error fetching {name}: {e}")
    if not value:
        raise ValueError(f"{name} is missing.")
    return value


url = load_the_env("SUPABASE_URL")
anon_key = load_the_env("SUPABASE_ANON_KEY")
service_role_key = load_the_env("SUPABASE_SERVICE_ROLE_KEY")


# 3. Initialize clients
supabase: Client = create_client(url, anon_key)
supabase_admin: Client = create_client(url, service_role_key)

