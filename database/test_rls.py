import os
from getpass import getpass
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


supabase: Client = create_client(url, anon_key)

response = supabase.table("collections").select("id").execute()
response_data = response.data or []

collection_ids = [
    item["id"]
    for item in response_data
]

print("Before sign-in:", collection_ids)

email = input("Test user email: ")
password = getpass("Test user password: ")

supabase.auth.sign_in_with_password(
    {
        "email": email,
        "password": password,
    }
)

print("After sign-in:", [item["id"] for item in (supabase.table("collections").select("id").execute().data or [])])

supabase.auth.sign_out()

print("After sign-out:", [item["id"] for item in (supabase.table("collections").select("id").execute().data or [])])
