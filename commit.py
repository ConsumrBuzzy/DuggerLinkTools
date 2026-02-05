#!/usr/bin/env python3
"""Universal commit script for DuggerLinkTools ecosystem.

This script provides a convenient way to run the commit CLI
from any directory in the C:\GitHub ecosystem.
"""

import sys
from pathlib import Path

# Add DuggerLinkTools to Python path
dlt_path = Path(__file__).parent
sys.path.insert(0, str(dlt_path))

from duggerlink.cli.commit import main

if __name__ == "__main__":
    main()