from database.client import supabase_admin

try:
    response = (
        supabase_admin.table("collections")
        .select("id")
        .limit(1)
        .execute()
    )

    collection_ids = [item["id"] for item in (response.data or [])] # type: ignore

    if not collection_ids:
        raise ValueError("No collections were returned.")

except Exception as error:
    print(f"Keepalive failed: {error}")
    raise

else:
    print(f"Found collection ID: {collection_ids[0]}")