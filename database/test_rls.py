from getpass import getpass
from client import supabase
response = supabase.table("collections").select("id").execute()
response_data = response.data or []

collection_ids = [
    item["id"]
    for item in response_data
]

print("Before sign-in:", collection_ids)
if collection_ids:
    raise AssertionError("Unsigned client unexpectedly read collections.")

email = input("Test user email: ")
password = getpass("Test user password: ")

supabase.auth.sign_in_with_password(
    {
        "email": email,
        "password": password,
    }
)

signed_in_ids = [item["id"] for item in (supabase.table("collections").select("id").execute().data or [])]
print("After sign-in:", signed_in_ids)
expected_ids = {"technical_docs", "sec_filings", "research_papers", "policy_reports"}
if len(signed_in_ids) != len(expected_ids) or set(signed_in_ids) != expected_ids:
    raise AssertionError("Signed-in client did not read exactly the four expected collections.")

supabase.auth.sign_out()

signed_out_ids = [item["id"] for item in (supabase.table("collections").select("id").execute().data or [])]
print("After sign-out:", signed_out_ids)
if signed_out_ids:
    raise AssertionError("Signed-out client unexpectedly read collections.")
