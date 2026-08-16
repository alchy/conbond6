"""`python -m cb6 …` → CLI."""

import sys

from cb6.cli import main

sys.exit(main(sys.argv[1:]))
