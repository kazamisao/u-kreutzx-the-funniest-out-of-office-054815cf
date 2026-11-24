"""The Funniest Out-of-Office (make.fun).

Writes one funny out-of-office line to
$MAKEFUN_OUTPUT_DIR/entry.txt. Deterministic, stdlib only, no network:
the same single line on every run.
"""

import os
from pathlib import Path

OUT_OF_OFFICE = (
    "Out of office: chaperoning a school field trip. The kids made me "
    "snack treasurer, so your urgent email is in a nine-year-old's "
    "audit queue."
)


def main() -> None:
    # The gate refuses anything outside 1-140 characters; fail loudly
    # here rather than shipping an invalid entry.
    if not 1 <= len(OUT_OF_OFFICE) <= 140 or not OUT_OF_OFFICE.strip():
        raise ValueError(
            f"out-of-office is {len(OUT_OF_OFFICE)} characters, must be 1-140"
        )
    out_dir = Path(os.environ["MAKEFUN_OUTPUT_DIR"])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "entry.txt").write_text(OUT_OF_OFFICE, encoding="utf-8")


if __name__ == "__main__":
    main()
