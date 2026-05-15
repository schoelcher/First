"""Allow: python -m dashboard"""

import uvicorn

from dashboard.config import HOST, PORT


def main():
    print(f"\n  EquityScope starting at  http://localhost:{PORT}\n")
    uvicorn.run("dashboard.app:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    main()
