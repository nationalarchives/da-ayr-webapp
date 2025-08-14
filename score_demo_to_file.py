#!/usr/bin/env python3
"""
Demo script showing OpenSearch scores with different fuzziness settings
Outputs results to a text file instead of printing to console
"""

import json
from datetime import datetime

from app import create_app
from configs.env_config import EnvConfig

app = create_app(EnvConfig)


def write_scores(term, config_name, field_config, file_handle):
    """Write search results with scores to file"""
    with app.app_context():
        from app.main.util.search_utils import compare_fuzzy_configurations

        configs = {config_name: field_config}
        results = compare_fuzzy_configurations(
            term, ["file_name^3", "description^2", "content^1"], configs
        )

        if config_name in results and "error" not in results[config_name]:
            result = results[config_name]
            file_handle.write(f"\n Search: '{term}' | Config: {config_name}\n")
            file_handle.write("=" * 70 + "\n")
            file_handle.write(f"Total Hits: {result['total_hits']}\n")
            file_handle.write(
                f"Query: {json.dumps(result['query'], indent=2)}\n"
            )
            file_handle.write("\nRESULTS WITH SCORES:\n")
            file_handle.write("-" * 50 + "\n")
            file_handle.write(f"{'#':>2} | {'Score':>8} | {'File Name'}\n")
            file_handle.write("-" * 50 + "\n")

            for i, (score, filename) in enumerate(
                zip(result["top_scores"], result["top_files"]), 1
            ):
                file_handle.write(f"{i:2d} | {score:8.3f} | {filename}\n")

            if not result["top_scores"]:
                file_handle.write("   No results found\n")
        else:
            file_handle.write(
                f" Error in search: {results.get(config_name, {}).get('error', 'Unknown error')}\n"
            )


if __name__ == "__main__":
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"opensearch_scores_{timestamp}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("OPENSEARCH SCORE DEMONSTRATION\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        f.write("\nSEARCH TYPES TESTED:\n")
        f.write(
            "File extensions: .msg .pdf .txt .doc .xlsx | Extension searches: msg pdf txt doc xlsx\n"
        )
        f.write(
            "False match targets: MIG Ms FOI REF TDR | Common terms: file document report email january ministry\n"
        )
        f.write(
            "Typo variations: fil flie ministy januray | Short terms: A B C IT HR Fi\n"
        )
        f.write(
            "Date references: Monday Jan Mon 2023-01-01 | Year tests: 2024 2023 2022 2021 2020\n"
        )
        f.write("\nFUZZINESS SETTINGS USED:\n")
        f.write(
            "LOOSE (Problem): fuzziness 'AUTO', max_expansions 100 (all fields)\n"
        )
        f.write(
            "VERY LOOSE (Worse): fuzziness '2', max_expansions 200 (all fields)\n"
        )
        f.write("EXACT: fuzziness '0' (all fields)\n")
        f.write(
            "SMART SOLUTION: filename fuzziness '0', content fuzziness 'AUTO', max_expansions 50\n"
        )
        f.write(
            "CONSERVATIVE: filename fuzziness '1' + prefix_length 1, content fuzziness 'AUTO'\n"
        )
        f.write(
            "PREFIX PROTECTED: fuzziness 'AUTO' + prefix_length 2 (filename), prefix_length 1 (description)\n"
        )
        f.write("=" * 60 + "\n")

        # Comprehensive test terms covering all problem scenarios
        test_terms = [
            # File extension problems
            ".msg",
            ".pdf",
            ".txt",
            ".doc",
            ".xlsx",
            # Extension searches without dots
            "msg",
            "pdf",
            "txt",
            "doc",
            "xlsx",
            # False match targets
            "MIG",
            "Ms",
            "FOI",
            "REF",
            "TDR",
            # Common searches
            "file",
            "document",
            "report",
            "email",
            "january",
            "ministry",
            # Typo variations
            "fil",
            "flie",
            "ministy",
            "januray",
            # Short terms that over-match
            "A",
            "B",
            "C",
            "IT",
            "HR",
            "Fi",
            # Date references
            "Monday",
            "Jan",
            "Mon",
            "2023-01-01",
            # Year fuzzy matching tests
            "2024",
            "2023",
            "2022",
            "2021",
            "2020",
        ]

        # BEFORE: Current problematic configurations
        before_configs = {
            "Current Loose (Problem)": {
                "file_name": {"fuzziness": "AUTO", "max_expansions": 100},
                "description": {"fuzziness": "AUTO", "max_expansions": 100},
                "content": {"fuzziness": "AUTO", "max_expansions": 100},
            },
            "Very Fuzzy (Worse)": {
                "file_name": {"fuzziness": "2", "max_expansions": 200},
                "description": {"fuzziness": "2", "max_expansions": 200},
                "content": {"fuzziness": "2", "max_expansions": 200},
            },
        }

        # AFTER: Improved configurations
        after_configs = {
            "Smart Solution": {
                "file_name": {
                    "fuzziness": "0"
                },  # Exact for filenames/extensions
                "description": {"fuzziness": "AUTO", "max_expansions": 50},
                "content": {"fuzziness": "AUTO", "max_expansions": 50},
            },
            "Conservative Fuzzy": {
                "file_name": {
                    "fuzziness": "1",
                    "prefix_length": 1,
                    "max_expansions": 10,
                },
                "description": {"fuzziness": "1", "max_expansions": 20},
                "content": {"fuzziness": "AUTO", "max_expansions": 50},
            },
            "Prefix Protected": {
                "file_name": {
                    "fuzziness": "AUTO",
                    "prefix_length": 2,
                    "max_expansions": 20,
                },
                "description": {
                    "fuzziness": "AUTO",
                    "prefix_length": 1,
                    "max_expansions": 50,
                },
                "content": {"fuzziness": "AUTO", "max_expansions": 50},
            },
            "Exact Match Only": {
                "file_name": {"fuzziness": "0"},
                "description": {"fuzziness": "0"},
                "content": {"fuzziness": "0"},
            },
        }

        # Combine all configurations
        configs = {**before_configs, **after_configs}

        # Write BEFORE section
        f.write(f"\n{'='*80}\n")
        f.write("BEFORE: CURRENT PROBLEMATIC FUZZY SETTINGS\n")
        f.write("=" * 80 + "\n")
        f.write(
            "Shows the false matching problems with loose fuzzy configurations\n\n"
        )

        for term in test_terms:
            f.write(f"\nTesting: '{term}'\n")
            f.write("-" * 40 + "\n")

            for config_name, config in before_configs.items():
                write_scores(term, config_name, config, f)

        # Write AFTER section
        f.write(f"\n{'='*80}\n")
        f.write("AFTER: IMPROVED FUZZY CONFIGURATIONS\n")
        f.write("=" * 80 + "\n")
        f.write("Shows how different configurations prevent false matches\n\n")

        for term in test_terms:
            f.write(f"\nTesting: '{term}'\n")
            f.write("-" * 40 + "\n")

            for config_name, config in after_configs.items():
                write_scores(term, config_name, config, f)

        f.write(f"\n{'='*80}\n")
        f.write("💡 KEY INSIGHTS FROM SCORES:\n")
        f.write("=" * 80 + "\n")
        f.write("• Higher scores = More relevant matches\n")
        f.write("• Exact matches typically score highest (~1.351)\n")
        f.write("• Fuzzy matching may lower scores but find more results\n")
        f.write("• Field boosts (file_name^3) multiply the base scores\n")
        f.write("• Watch for zero results vs low-scoring results\n")
        f.write("• prefix_length prevents distant false matches\n")
        f.write("• max_expansions controls performance vs thoroughness\n")
        f.write("\n")
        f.write("SCORE INTERPRETATION:\n")
        f.write("• Score > 1.0:   Excellent match (high confidence)\n")
        f.write("• Score 0.5-1.0: Good match (reasonable fuzzy match)\n")
        f.write("• Score 0.1-0.5: Weak match (review needed)\n")
        f.write("• Score < 0.1:   Poor match (likely false positive)\n")
        f.write("\n")
        f.write("CONFIGURATION ANALYSIS:\n")
        f.write("• Exact Match: No false positives, may miss typos\n")
        f.write("• Fuzzy 1: Good balance, handles simple typos\n")
        f.write("• Fuzzy 1 + Prefix: Prevents distant matches (jan≠can)\n")
        f.write("• Fuzzy AUTO: Adaptive based on term length\n")
        f.write("• Fuzzy 2: More permissive, risk of over-matching\n")
        f.write("• Conservative: Very precise, good for critical searches\n")

    print(f"Results written to: {output_file}")
    print(f"File contains BEFORE/AFTER analysis of fuzzy search configurations")
    print(
        f"BEFORE: {len(test_terms)} search terms × 2 problematic configurations"
    )
    print(f"AFTER: {len(test_terms)} search terms × 4 improved configurations")
    print(
        f"Shows how to fix .msg -> Ms/MIG false matching and other search problems"
    )
