#!/usr/bin/env python3
"""CRAG CLI - Command-line interface for the CRAG system."""

import os
import sys

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from dotenv import load_dotenv
load_dotenv()

from crag.agent import crag_app


def main():
    """Run the CRAG CLI."""
    print("\n" + "=" * 70)
    print("CRAG - Corrective Retrieval-Augmented Generation System")
    print("=" * 70)
    print("Built by Mobolaji Opeyemi Bolatito Obinna")
    print("Local PDFs + Brave Search Fallback")
    print("=" * 70)
    print("\nType 'quit', 'exit', or 'bye' to stop\n")

    while True:
        try:
            question = input("Ask me anything: ").strip()
            
            if question.lower() in {"quit", "exit", "bye", ""}:
                print("\nGoodbye!")
                break
            
            if not question:
                continue
                
            print("\nThinking...\n")

            result = crag_app.invoke({"question": question})
            
            print("\n" + "=" * 70)
            print("ANSWER:")
            print("=" * 70)
            print(result.get("answer", "No answer generated"))
            
            print("\n" + "=" * 70)
            print("SOURCES:")
            print("=" * 70)
            
            citations = result.get("citations", [])
            if citations:
                for c in citations[:10]:
                    source_type = c.get("type", "local")
                    source_name = c.get("source", "Unknown")
                    print(f"  [{source_type.upper()}] {source_name}")
            else:
                print("  No sources found")
            
            used_web = result.get("used_web_search", False)
            if used_web:
                print("\n  (Web search was used for this query)")
            
            print("\n" + "-" * 70)
            print("CRAG System - Corrective Retrieval-Augmented Generation")
            print("-" * 70 + "\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
