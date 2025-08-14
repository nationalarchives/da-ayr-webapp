#!/usr/bin/env python3
"""
Add additional date-related test files to showcase fuzzy matching with years
"""

import json
import os
from datetime import datetime

import requests


def create_date_test_files():
    """Create additional test files with various date formats and years"""

    date_files = [
        # Different years that could cause fuzzy matching
        ("2024 Annual Report.pdf", "Annual report for the year 2024"),
        ("2023 Budget Analysis.xlsx", "Budget analysis for fiscal year 2023"),
        (
            "2022 Performance Review.doc",
            "Performance review document from 2022",
        ),
        ("2021 Strategic Plan.txt", "Strategic planning document for 2021"),
        ("2020 COVID Response.pdf", "Emergency response plan from 2020"),
        # Similar years that might cross-match
        ("2024-01-15 Meeting.txt", "Meeting minutes from January 15, 2024"),
        ("2023-12-31 Summary.pdf", "Year-end summary dated December 31, 2023"),
        ("2022-06-30 Audit.xlsx", "Mid-year audit report from June 30, 2022"),
        # Month/year combinations
        ("Jan 2024 Newsletter.pdf", "Monthly newsletter for January 2024"),
        ("Feb 2023 Status.doc", "February 2023 status update"),
        ("Mar 2022 Forecast.xlsx", "March 2022 financial forecast"),
        ("Dec 2021 Closure.txt", "December 2021 project closure notes"),
        # Date formats that could confuse fuzzy matching
        ("01-01-2024 New Year.pdf", "New Year document for January 1, 2024"),
        (
            "31-12-2023 End Year.doc",
            "End of year document for December 31, 2023",
        ),
        ("15-06-2022 Mid Year.xlsx", "Mid-year review for June 15, 2022"),
        # Quarter references
        ("Q1 2024 Results.pdf", "First quarter 2024 financial results"),
        ("Q4 2023 Summary.doc", "Fourth quarter 2023 performance summary"),
        ("Q2 2022 Analysis.xlsx", "Second quarter 2022 market analysis"),
        # Potential fuzzy confusion cases
        (
            "2024 vs 2023 Comparison.pdf",
            "Comparative analysis between 2024 and 2023",
        ),
        (
            "2023-2024 Transition Plan.doc",
            "Transition planning document spanning 2023-2024",
        ),
        (
            "Historical 2020-2024 Trends.xlsx",
            "Four-year trend analysis from 2020 to 2024",
        ),
    ]

    # Create test files directory if it doesn't exist
    test_dir = "test_files_for_indexing"
    os.makedirs(test_dir, exist_ok=True)

    created_files = []
    for filename, content in date_files:
        filepath = os.path.join(test_dir, filename)

        # Add detailed content
        full_content = f"""
{content}

Document Details:
- Filename: {filename}
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Purpose: Date-based fuzzy search testing
- Category: Date reference test document

Content Summary:
This document is designed to test how OpenSearch handles date-related searches
with different fuzziness configurations. It contains various date formats and
year references to evaluate potential cross-matching between similar years.

Key dates and references mentioned in this document:
- Primary date reference: {filename.split()[0] if any(char.isdigit() for char in filename.split()[0]) else "Various"}
- Document type: {filename.split('.')[-1].upper() if '.' in filename else 'Text'}
- Year focus: {[word for word in filename.split() if word.isdigit() and len(word) == 4]}

Additional searchable content includes quarterly reports, annual summaries,
date-specific analysis, and temporal reference points for comprehensive
fuzzy matching evaluation across different time periods and formats.
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        created_files.append(filepath)

    return created_files


def create_date_documents(test_files):
    """Create OpenSearch document format for the date test files"""

    documents = []
    base_id = 100  # Start with higher IDs to avoid conflicts

    for i, filepath in enumerate(test_files, base_id):
        filename = os.path.basename(filepath)

        # Read file content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract file extension
        if "." in filename:
            name_part, ext_part = filename.rsplit(".", 1)
            file_extension = f".{ext_part}"
        else:
            name_part = filename
            file_extension = ""

        # Extract years from filename for keyword analysis
        import re

        years = re.findall(r"\b(20\d{2})\b", filename)

        doc = {
            "file_name": filename,
            "file_extension": file_extension,
            "description": (
                content.split("\n")[1]
                if len(content.split("\n")) > 1
                else filename
            ),
            "content": content,
            "file_path": filepath,
            "file_size": os.path.getsize(filepath),
            "created_date": datetime.now().isoformat(),
            "document_id": f"date-test-{i:03d}",
            "category": "date_test_document",
            "keywords": filename.replace(".", " ")
            .replace("-", " ")
            .replace("_", " ")
            .split(),
            "years_referenced": years,
        }

        documents.append(doc)

    return documents


def index_date_documents(documents):
    """Index the date test documents into the main OpenSearch index"""

    opensearch_url = "http://localhost:9200"
    main_index = "documents"

    print(f"Adding {len(documents)} date test documents to main index...")

    added_count = 0
    for doc in documents:
        doc_id = doc["document_id"]

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
                print(f"Failed to add {doc['file_name']}: {response.text}")

        except Exception as e:
            print(f"Error adding {doc['file_name']}: {e}")

    if added_count > 0:
        # Refresh the index
        refresh_response = requests.post(
            f"{opensearch_url}/{main_index}/_refresh"
        )
        if refresh_response.status_code == 200:
            print("Index refreshed")

        # Test search for years
        print(f"\nTesting year searches:")
        for year in ["2024", "2023", "2022"]:
            search_response = requests.get(
                f"{opensearch_url}/{main_index}/_search?q={year}&size=3"
            )
            if search_response.status_code == 200:
                results = search_response.json()
                hits = results.get("hits", {}).get("hits", [])
                print(f"  '{year}': {len(hits)} results")
                for hit in hits:
                    filename = hit["_source"].get("file_name", "Unknown")
                    score = hit["_score"]
                    print(f"    - {filename} (score: {score:.3f})")

    return added_count


if __name__ == "__main__":
    print("Creating additional date test files...")

    # Create date test files
    test_files = create_date_test_files()
    print(f"Created {len(test_files)} date test files")

    # Create OpenSearch documents
    documents = create_date_documents(test_files)
    print(f"Prepared {len(documents)} documents for indexing")

    # Index into main OpenSearch index
    added_count = index_date_documents(documents)

    print(f"\nSUMMARY:")
    print(f"Successfully added {added_count} date test documents")
    print(f"Now you can test fuzzy matching with year searches:")
    print(f"- Search '2024' to see if it matches '2023', '2022', etc.")
    print(f"- Search '2023' to check cross-year matching")
    print(f"- Test different fuzziness settings to see year confusion")
    print(f"\nRun updated score analysis:")
    print(f"poetry run python score_demo_to_file.py")
