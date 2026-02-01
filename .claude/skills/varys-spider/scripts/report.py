#!/usr/bin/env python3
"""report.py - Backwards-compatible wrapper.

`varys-spider report` delegates to generate.py which reads
~/.openclaw/varys-spider/config.json.

"""

from __future__ import annotations

from generate import main


if __name__ == "__main__":
    main()
