import os
import sys

import httpx

from .config import API_BASE_URL


def main() -> None:
    api_base = os.getenv("API_BASE_URL", API_BASE_URL)
    username = os.getenv("DEMO_USERNAME", "admin")
    password = os.getenv("DEMO_PASSWORD", "admin-pass")

    print("Step 1: Start the API + UI (run in another terminal):")
    print("  uv run uvicorn app.main:app --reload")
    print("  uv run streamlit run streamlit_app.py --server.port 8501")
    print("Step 2: Use this script to verify the API and queue a report.")

    print(f"API base: {api_base}")
    with httpx.Client(timeout=5) as client:
        health = client.get(f"{api_base}/health")
        print(f"Health: {health.status_code} {health.json()}")

        login = client.post(
            f"{api_base}/auth/login",
            json={"username": username, "password": password},
        )
        if login.status_code != 200:
            print("Login failed. Create a user with: uv run python -m app.cli create-user")
            sys.exit(1)
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        search = client.get(f"{api_base}/series", params={"query": "bear"})
        print(f"Search for 'bear' returned {len(search.json())} results.")

        queued = client.post(f"{api_base}/reports/queue", headers=headers)
        print(f"Queued report job: {queued.status_code} {queued.json()}")


if __name__ == "__main__":
    main()
