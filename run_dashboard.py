#!/usr/bin/env python3
"""Quick-start: python run_dashboard.py"""

import uvicorn

from dashboard.config import HOST, PORT

if __name__ == "__main__":
    print(f"\n  EquityScope starting at  http://localhost:{PORT}\n")
    uvicorn.run("dashboard.app:app", host=HOST, port=PORT, reload=True)
