import os
import sys
from dotenv import load_dotenv
from client import supabase, supabase_admin


row_data = {
        "run_id": "phase1-write-test-001",
        "query": "This is a temporary permission test.",
        "llm_label": False,
        "llm_model": "test-only"
    }




try:
    response = (
        supabase.table("grading_log")
        .insert(row_data)
        .execute()
    )
except Exception as e:
    print(f"Anon insert failed. Check that the error says permission was denied: {e}")

else:
    print("Anon insert succeeded unexpectedly; check the table permissions and remove the test row.")



try:
    admin_response = (
        supabase_admin.table("grading_log")
        .insert(row_data)
        .execute()
    )
except Exception as e:
    print(f"Admin insert failed unexpectedly: {e}")

else:
    if not admin_response.data:
        raise RuntimeError("Admin insert returned no row ID; check grading_log for the test row.")
    inserted_row_id = admin_response.data[0]["id"]
    print(f"Admin insert succeeded. Test row ID: {inserted_row_id}")

    delete_response = (
    supabase_admin.table("grading_log")
    .delete()
    .eq("id", inserted_row_id)
    .execute()
    )

    lookup_response = (
    supabase_admin.table("grading_log")
    .select("*")
    .eq("id", inserted_row_id)
    .execute()
    )
    
    if lookup_response.data:
        raise RuntimeError("Test row was not deleted; check grading_log for the test row.")
    else:
        print("Deleted successfully:", delete_response.data)
