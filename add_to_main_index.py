#!/usr/bin/env python3
"""
Add test files to the main 'documents' index used by the webapp
"""

import json
from datetime import datetime

import requests


def add_test_files_to_main_index():
    """Add test documents to the main documents index"""

    # OpenSearch connection details
    opensearch_url = "http://localhost:9200"
    main_index = "documents"  # Your webapp's main index

    # Load the test documents we created
    with open(
        "test_files_for_indexing/opensearch_documents.json",
        "r",
        encoding="utf-8",
    ) as f:
        test_documents = json.load(f)

    print(
        f"Adding {len(test_documents)} test documents to main index '{main_index}'..."
    )

    # Check if main index exists
    response = requests.get(f"{opensearch_url}/{main_index}")
    if response.status_code != 200:
        print(f"Error: Main index '{main_index}' not found")
        print("Available indices:")
        indices_response = requests.get(
            f"{opensearch_url}/_cat/indices?format=json"
        )
        if indices_response.status_code == 200:
            for index in indices_response.json():
                print(f"  - {index['index']}")
        return False

    print(f"Main index '{main_index}' found")

    # Add each test document to the main index
    added_count = 0
    failed_count = 0

    for doc in test_documents:
        # Create a unique document ID to avoid conflicts
        doc_id = f"test_{doc['document_id']}"

        try:
            response = requests.put(
                f"{opensearch_url}/{main_index}/_doc/{doc_id}",
                json=doc,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code in [200, 201]:
                added_count += 1
                print(f"Added: {doc['file_name']}")
            else:
                failed_count += 1
                print(f"Failed to add {doc['file_name']}: {response.text}")

        except Exception as e:
            failed_count += 1
            print(f"Error adding {doc['file_name']}: {e}")

    print(f"\nResults:")
    print(f"Successfully added: {added_count} documents")
    print(f"Failed: {failed_count} documents")

    if added_count > 0:
        # Refresh the index to make documents searchable
        refresh_response = requests.post(
            f"{opensearch_url}/{main_index}/_refresh"
        )
        if refresh_response.status_code == 200:
            print("Index refreshed - documents are now searchable")

        # Show some example documents
        print(f"\nVerifying - searching for 'msg' in main index:")
        search_response = requests.get(
            f"{opensearch_url}/{main_index}/_search?q=msg&size=5"
        )
        if search_response.status_code == 200:
            results = search_response.json()
            hits = results.get("hits", {}).get("hits", [])
            print(f"Found {len(hits)} results:")
            for hit in hits:
                filename = hit["_source"].get("file_name", "Unknown")
                score = hit["_score"]
                print(f"  - {filename} (score: {score:.3f})")

        return True

    return False


def check_main_index_content():
    """Check what's currently in the main index"""
    opensearch_url = "http://localhost:9200"
    main_index = "documents"

    print(f"Checking content of main index '{main_index}'...")

    # Get total document count
    count_response = requests.get(f"{opensearch_url}/{main_index}/_count")
    if count_response.status_code == 200:
        total_docs = count_response.json()["count"]
        print(f"Total documents in index: {total_docs}")

    # Sample some documents
    search_response = requests.get(
        f"{opensearch_url}/{main_index}/_search?size=10"
    )
    if search_response.status_code == 200:
        results = search_response.json()
        hits = results.get("hits", {}).get("hits", [])
        print(f"\nSample documents:")
        for hit in hits[:5]:
            filename = hit["_source"].get("file_name", "Unknown")
            print(f"  - {filename}")

    # Check for existing .msg files
    msg_response = requests.get(
        f"{opensearch_url}/{main_index}/_search?q=file_name:*.msg&size=5"
    )
    if msg_response.status_code == 200:
        msg_results = msg_response.json()
        msg_hits = msg_results.get("hits", {}).get("hits", [])
        print(f"\nExisting .msg files: {len(msg_hits)}")
        for hit in msg_hits:
            filename = hit["_source"].get("file_name", "Unknown")
            print(f"  - {filename}")


if __name__ == "__main__":
    print("Checking main index before adding test files...")
    check_main_index_content()

    print(f"\n{'='*60}")

    # Add test files to main index
    success = add_test_files_to_main_index()

    if success:
        print(f"\n{'='*60}")
        print("Test files added successfully!")
        print("\nNow you can test .msg searches in your webapp and see:")
        print("- Real .msg files (report.msg, presentation.msg, email.msg)")
        print(
            "- False match candidates (Ms Johnson Letter.txt, MIG Aircraft Manual.txt)"
        )
        print("- The actual .msg -> Ms/MIG problem in action")
        print("\nRun your score analysis again:")
        print("  poetry run python score_demo_to_file.py")
    else:
        print("Failed to add test files to main index")
