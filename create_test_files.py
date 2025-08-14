#!/usr/bin/env python3
"""
Create test files to showcase different search scenarios
Includes problematic cases like .msg -> Ms, MIG false matching
"""

import json
import os
from datetime import datetime


def create_test_files():
    """Create test files that demonstrate various search scenarios"""

    # Create test files directory
    test_dir = "test_files_for_indexing"
    os.makedirs(test_dir, exist_ok=True)

    test_files = [
        # File extension test cases
        ("report.msg", "Monthly status report from January meeting"),
        ("presentation.msg", "Quarterly review presentation for management"),
        ("email.msg", "Important correspondence regarding project status"),
        ("document.pdf", "Annual financial report with charts and graphs"),
        ("manual.pdf", "User manual for software installation procedures"),
        ("spreadsheet.xlsx", "Budget calculations for next fiscal year"),
        ("image.jpg", "Photo documentation of site inspection"),
        ("archive.zip", "Compressed backup files from server migration"),
        # Files that could cause false matches
        (
            "Ms Johnson Letter.txt",
            "Correspondence from Ms Johnson regarding policy",
        ),
        (
            "MIG Aircraft Manual.txt",
            "Technical manual for MIG fighter aircraft",
        ),
        ("Ms Smith Report.doc", "Performance review prepared by Ms Smith"),
        ("MIG Database.sql", "Migration scripts for database upgrade"),
        # Short term test cases
        ("A Team Notes.txt", "Notes from A Team weekly standup meeting"),
        ("B Section Report.pdf", "Status report from B Section operations"),
        ("C Division Plan.docx", "Strategic plan from C Division leadership"),
        ("IT Support Log.txt", "Technical support tickets and resolutions"),
        ("HR Policy Update.pdf", "Human resources policy revision document"),
        ("Fi Analysis.xlsx", "Financial analysis spreadsheet with projections"),
        # Common search terms
        ("file management guide.pdf", "Best practices for file organization"),
        (
            "file transfer protocol.txt",
            "Documentation for secure file transfers",
        ),
        ("ministry briefing.doc", "Briefing document for ministry officials"),
        (
            "ministry guidelines.pdf",
            "Official guidelines from ministry headquarters",
        ),
        ("january schedule.xlsx", "Work schedule for January activities"),
        ("january budget.pdf", "Budget allocation for January operations"),
        # Technical and reference codes
        ("FOI-2023-001.pdf", "Freedom of Information request response"),
        ("FOI-2023-002.txt", "FOI case file with supporting documents"),
        ("REF-ABC-123.doc", "Reference document with classification code"),
        ("TDR-2023-BV6.xml", "Transfer document record metadata file"),
        ("LOG-ERROR-456.txt", "System error log with diagnostic information"),
        # Typo variations for testing
        ("fil transfer guide.txt", "Guide with intentional typo in filename"),
        ("flie management.pdf", "Document with transposed characters"),
        ("ministy briefing.doc", "Briefing with missing letter"),
        ("januray schedule.xlsx", "Schedule with character substitution"),
        # Date and temporal references
        ("Monday Meeting Notes.txt", "Weekly team meeting minutes"),
        ("Tuesday Status Update.pdf", "Project status for Tuesday review"),
        ("2023-01-01 Report.xlsx", "New Year status report"),
        ("01-01-2023 Summary.doc", "Year-end summary document"),
        ("Jan 2023 Budget.pdf", "Monthly budget for January"),
        ("Mon Schedule.txt", "Monday work schedule"),
        # Mixed content for comprehensive testing
        ("Project Alpha .msg Archive.zip", "Email archive for Project Alpha"),
        ("Beta Test .pdf Results.txt", "Test results mixing extensions"),
        ("Gamma Release msg backup.doc", "Release notes with mixed terms"),
    ]

    # Create the files with content
    created_files = []
    for filename, content in test_files:
        filepath = os.path.join(test_dir, filename)

        # Add more detailed content
        full_content = f"""
{content}

Document Details:
- Filename: {filename}
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Purpose: Search testing and analysis
- Category: Test document for OpenSearch fuzzy matching evaluation

Content Summary:
This document is part of a test suite designed to evaluate OpenSearch fuzzy matching
configurations. It helps identify optimal settings for different search scenarios
including file extensions, short terms, reference codes, and natural language queries.

Keywords: {filename.replace('.', ' ').replace('-', ' ').replace('_', ' ')}

Additional searchable content to ensure meaningful results in OpenSearch analysis.
The document contains various terms that should be findable through different
fuzzy matching configurations while avoiding false positive matches.
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        created_files.append(filepath)

    return created_files, test_dir


def create_opensearch_documents(test_files, base_dir):
    """Create OpenSearch document format for indexing"""

    documents = []
    for i, filepath in enumerate(test_files, 1):
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

        # Create document structure similar to your existing index
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
            "document_id": f"test-doc-{i:03d}",
            "category": "test_document",
            "keywords": filename.replace(".", " ")
            .replace("-", " ")
            .replace("_", " ")
            .split(),
        }

        documents.append(doc)

    # Save documents as JSON for easy indexing
    docs_file = os.path.join(base_dir, "opensearch_documents.json")
    with open(docs_file, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    return documents, docs_file


def create_indexing_script(docs_file):
    """Create script to index the test documents in OpenSearch"""

    script_content = f'''#!/usr/bin/env python3
"""
Index test documents into OpenSearch for fuzzy search testing
"""

import json
import requests
from datetime import datetime

def index_test_documents():
    """Index all test documents into OpenSearch"""

    # OpenSearch connection details
    opensearch_url = "http://localhost:9200"
    index_name = "test_documents"

    # Load documents
    with open("{docs_file}", 'r', encoding='utf-8') as f:
        documents = json.load(f)

    print(f"Indexing {{len(documents)}} test documents...")

    # Create index if it doesn't exist
    index_config = {{
        "mappings": {{
            "properties": {{
                "file_name": {{"type": "text", "analyzer": "standard"}},
                "file_extension": {{"type": "keyword"}},
                "description": {{"type": "text", "analyzer": "standard"}},
                "content": {{"type": "text", "analyzer": "standard"}},
                "file_path": {{"type": "keyword"}},
                "file_size": {{"type": "long"}},
                "created_date": {{"type": "date"}},
                "document_id": {{"type": "keyword"}},
                "category": {{"type": "keyword"}},
                "keywords": {{"type": "text"}}
            }}
        }}
    }}

    try:
        # Create index
        response = requests.put(f"{{opensearch_url}}/{{index_name}}",
                              json=index_config,
                              headers={{"Content-Type": "application/json"}})

        if response.status_code in [200, 400]:  # 400 if index exists
            print(f"Index {{index_name}} ready")
        else:
            print(f"Error creating index: {{response.text}}")
            return

        # Index documents
        indexed_count = 0
        for doc in documents:
            doc_id = doc["document_id"]
            response = requests.put(f"{{opensearch_url}}/{{index_name}}/_doc/{{doc_id}}",
                                  json=doc,
                                  headers={{"Content-Type": "application/json"}})

            if response.status_code in [200, 201]:
                indexed_count += 1
                print(f"Indexed: {{doc['file_name']}}")
            else:
                print(f"Error indexing {{doc['file_name']}}: {{response.text}}")

        print(f"\\nSuccessfully indexed {{indexed_count}} documents")
        print(f"Index: {{index_name}}")
        print(f"OpenSearch URL: {{opensearch_url}}")

        # Refresh index
        requests.post(f"{{opensearch_url}}/{{index_name}}/_refresh")
        print("Index refreshed")

    except Exception as e:
        print(f"Error: {{e}}")
        print("Make sure OpenSearch is running on localhost:9200")

if __name__ == "__main__":
    index_test_documents()
'''

    script_file = "index_test_documents.py"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script_content)

    return script_file


if __name__ == "__main__":
    print("Creating test files for fuzzy search analysis...")

    # Create test files
    test_files, test_dir = create_test_files()
    print(f"Created {len(test_files)} test files in {test_dir}/")

    # Create OpenSearch documents
    documents, docs_file = create_opensearch_documents(test_files, test_dir)
    print(f"Created OpenSearch document definitions in {docs_file}")

    # Create indexing script
    script_file = create_indexing_script(docs_file)
    print(f"Created indexing script: {script_file}")

    print("\\nNext steps:")
    print("1. Run the indexing script:")
    print(f"   python {script_file}")
    print("2. Test fuzzy search configurations:")
    print("   python score_demo_to_file.py")
    print("3. Analyze results for .msg -> Ms/MIG false matches")

    print("\\nTest scenarios included:")
    print("- File extensions (.msg, .pdf, .txt, .xlsx, .jpg, .zip)")
    print("- False match targets (Ms Johnson, MIG Aircraft)")
    print("- Short terms (A, B, C, IT, HR, Fi)")
    print("- Reference codes (FOI-2023-001, REF-ABC-123)")
    print("- Typo variations (fil, flie, ministy, januray)")
    print("- Date references (January, Monday, 2023-01-01)")
    print("- Mixed content for comprehensive testing")
