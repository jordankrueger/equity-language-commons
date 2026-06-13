#!/usr/bin/env python3
"""One-off: standardize ELC's own prose to house style.

Rules (2026-06-13, Jordan):
  - United States  ->  "U.S." (AP style)
  - "N percent"    ->  "N%"   (majority form; AP post-2019)
  - "towards"      ->  "toward"

HARD CONSTRAINT: never touch verbatim `quote:` fields (Layer 1 / fair-use
locked). We skip any line whose first non-space token is `quote:`. All quotes
in the corpus are single-line YAML scalars (verified — no block scalars), so a
line-level skip is sufficient.

Applies to ELC prose: body markdown + paraphrase/note/relevance/claim/audience
frontmatter fields. Idempotent.
"""
import re
import sys
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "site" / "src" / "content"
DIRS = ["terms", "chapters", "sources"]

QUOTE_LINE = re.compile(r"^\s*quote:")

# "US." (followed by period) -> "U.S."  then standalone "US" -> "U.S."
RE_US_DOT = re.compile(r"\bUS\.")
RE_US = re.compile(r"\bUS\b(?!\.)")
RE_PERCENT = re.compile(r"(\d)\s*percent\b")
RE_TOWARDS = re.compile(r"\btowards\b")


def transform_line(line: str) -> str:
    if QUOTE_LINE.match(line):
        return line  # verbatim quote — never touch
    line = RE_US_DOT.sub("U.S.", line)
    line = RE_US.sub("U.S.", line)
    line = RE_PERCENT.sub(r"\1%", line)
    line = RE_TOWARDS.sub("toward", line)
    return line


def main() -> int:
    changed_files = 0
    total_lines = 0
    for d in DIRS:
        for path in sorted((CONTENT / d).glob("*.md")):
            orig = path.read_text(encoding="utf-8")
            new_lines = []
            file_changed = False
            for line in orig.splitlines(keepends=True):
                t = transform_line(line)
                if t != line:
                    file_changed = True
                    total_lines += 1
                new_lines.append(t)
            if file_changed:
                path.write_text("".join(new_lines), encoding="utf-8")
                changed_files += 1
                print(f"  {d}/{path.name}")
    print(f"\n{changed_files} files changed, {total_lines} lines touched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
