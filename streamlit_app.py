import csv
import os
from datetime import datetime
from io import StringIO
from typing import Any

import requests
import streamlit as st

API_BASE_DEFAULT = os.getenv("TV_API_BASE", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT = 5


def inject_imdb_theme() -> None:
    """Apply an IMDB-inspired dark theme with gold accents."""
    st.markdown(
        """
        <style>
        :root {
            --imdb-gold: #f5c518;
            --imdb-dark: #0f0f0f;
            --imdb-panel: #1a1a1a;
            --imdb-muted: #b8b8b8;
        }
        body, .stApp { background-color: var(--imdb-dark); color: #f7f7f7; }
        h1, h2, h3, h4 { color: var(--imdb-gold); letter-spacing: 0.2px; font-weight: 800; }
        .stMarkdown p { color: #f7f7f7; }
        .stDataFrame { border: 1px solid #2a2a2a; border-radius: 12px; overflow: hidden; }
        .stButton>button {
            background-color: var(--imdb-gold);
            color: #0f0f0f;
            border-radius: 6px;
            border: 0;
            padding: 0.5rem 1rem;
            font-weight: 700;
        }
        .stButton>button:hover { filter: brightness(0.92); }
        .panel {
            background: var(--imdb-panel);
            padding: 1rem 1.25rem;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
        }
        .metric-card {
            background: var(--imdb-panel);
            padding: 0.75rem 1rem;
            border: 1px solid #2a2a2a;
            border-radius: 10px;
        }
        input, textarea {
            background: #111 !important;
            color: #f0f0f0 !important;
            border-radius: 6px !important;
            border: 1px solid #2a2a2a !important;
        }
        .stSelectbox>div>div {
            background: #111;
            border: 1px solid #2a2a2a;
            color: #f7f7f7;
            border-radius: 6px;
            box-shadow: none;
        }
        .stDownloadButton>button {
            background: var(--imdb-gold);
            color: #0f0f0f;
            border: 0;
            border-radius: 6px;
            font-weight: 800;
        }
        .header-row {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 0.25rem;
        }
        .logo-box {
            background: var(--imdb-gold);
            color: #0f0f0f;
            font-weight: 900;
            padding: 0.55rem 0.75rem;
            border-radius: 6px;
            letter-spacing: 0.8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.35);
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _clean_base_url(raw_url: str) -> str:
    """Normalize the API base URL input."""
    if not raw_url:
        return API_BASE_DEFAULT
    return raw_url.strip().rstrip("/") or API_BASE_DEFAULT


def fetch_series(api_base: str) -> list[dict[str, Any]]:
    """Fetch the list of series from the API."""
    try:
        response = requests.get(f"{api_base}/series", timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return []

    if response.status_code != 200:
        st.error(f"API returned {response.status_code}: {response.text}")
        return []

    payload = response.json()
    return payload if isinstance(payload, list) else []


def create_series(api_base: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Create a new series via the API."""
    try:
        response = requests.post(f"{api_base}/series", json=payload, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return None

    if response.status_code not in (200, 201):
        st.error(f"Create failed ({response.status_code}): {response.text}")
        return None

    return response.json()


def delete_series(api_base: str, series_id: int) -> bool:
    """Delete a series entry via the API."""
    try:
        response = requests.delete(f"{api_base}/series/{series_id}", timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return False

    if response.status_code != 204:
        st.error(f"Delete failed ({response.status_code}): {response.text}")
        return False

    return True


def update_series(api_base: str, series_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Replace a series entry via the API."""
    try:
        response = requests.put(
            f"{api_base}/series/{series_id}",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return None

    if response.status_code != 200:
        st.error(f"Update failed ({response.status_code}): {response.text}")
        return None

    return response.json()


def patch_series(api_base: str, series_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Partially update a series entry via the API."""
    try:
        response = requests.patch(
            f"{api_base}/series/{series_id}",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return None

    if response.status_code != 200:
        st.error(f"Patch failed ({response.status_code}): {response.text}")
        return None

    return response.json()


def render_metrics(series: list[dict[str, Any]]) -> None:
    """Render summary metrics for the dataset."""
    ratings = [row["rating"] for row in series if row.get("rating") is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    top_rated = max(series, key=lambda row: row.get("rating") or 0, default=None)

    col_total, col_avg, col_top = st.columns(3)
    col_total.metric("Total series", len(series))
    col_avg.metric("Avg rating", f"{avg_rating:.1f}" if avg_rating is not None else "—")
    if top_rated and top_rated.get("rating") is not None:
        col_top.metric("Top rated", f"{top_rated['title']} ({top_rated['rating']})")
    else:
        col_top.metric("Top rated", "—")


def render_table(series: list[dict[str, Any]]) -> None:
    """Render the main data table and export controls."""
    if not series:
        st.info("No series yet. Add your first entry to get started.")
        return

    st.dataframe(
        series,
        width="stretch",
        hide_index=True,
        column_order=["id", "title", "creator", "year", "rating"],
    )

    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=["id", "title", "creator", "year", "rating"])
    writer.writeheader()
    writer.writerows(series)
    st.download_button(
        "Download CSV snapshot",
        data=csv_buffer.getvalue(),
        file_name="series.csv",
        mime="text/csv",
    )


def render_create_form(api_base: str) -> None:
    """Render the form for creating new series entries."""
    st.subheader("Add a new series")
    with st.form("create-series", clear_on_submit=True):
        title = st.text_input("Title", placeholder="e.g., The Bear", max_chars=120)
        creator = st.text_input("Creator", placeholder="e.g., Christopher Storer", max_chars=120)
        year = st.number_input(
            "Year",
            min_value=1900,
            max_value=2100,
            value=datetime.now().year,
            step=1,
        )
        rating_raw = st.text_input("Rating (0-10, optional)", placeholder="8.6")

        submitted = st.form_submit_button("Save series")
        if not submitted:
            return

        rating: float | None = None
        if rating_raw:
            try:
                rating = float(rating_raw)
            except ValueError:
                st.error("Rating must be a number between 0 and 10.")
                return
            if not 0 <= rating <= 10:
                st.error("Rating must be between 0 and 10.")
                return

        if not title or not creator:
            st.error("Title and creator are required.")
            return

        payload = {"title": title, "creator": creator, "year": int(year), "rating": rating}
        created = create_series(api_base, payload)
        if created:
            st.success(f"Saved: {created['title']} ({created['year']})")
            st.rerun()


def render_delete_form(api_base: str, series: list[dict[str, Any]]) -> None:
    """Render a delete control for existing entries."""
    st.subheader("Delete an entry")
    if not series:
        st.caption("No entries to delete yet.")
        return

    options = {row["id"]: row for row in series}
    selected_id = st.selectbox(
        "Pick a series to delete",
        sorted(options.keys()),
        format_func=lambda series_id: (
            f"#{series_id} · {options[series_id]['title']} ({options[series_id]['year']})"
        ),
        key="delete-series",
    )
    if st.button("Delete selected", type="primary"):
        if delete_series(api_base, selected_id):
            st.success(f"Deleted: #{selected_id}")
            st.rerun()


def render_update_forms(api_base: str, series: list[dict[str, Any]]) -> None:
    """Render controls for updating existing entries."""
    st.subheader("Update an entry")
    if not series:
        st.caption("No entries to update yet.")
        return

    options = {row["id"]: row for row in series}
    selected_id = st.selectbox(
        "Pick a series to edit",
        sorted(options.keys()),
        format_func=lambda series_id: (
            f"#{series_id} · {options[series_id]['title']} ({options[series_id]['year']})"
        ),
        key="edit-series",
    )
    selected = options[selected_id]
    st.caption(f"Editing ID #{selected['id']}")

    with st.form("replace-series"):
        st.markdown("Replace (PUT)")
        title = st.text_input("Title", value=selected["title"], max_chars=120, key="put-title")
        creator = st.text_input(
            "Creator",
            value=selected["creator"],
            max_chars=120,
            key="put-creator",
        )
        year = st.number_input(
            "Year",
            min_value=1900,
            max_value=2100,
            value=int(selected["year"]),
            step=1,
            key="put-year",
        )
        rating_raw = st.text_input(
            "Rating (0-10, optional)",
            value="" if selected.get("rating") is None else str(selected["rating"]),
            key="put-rating",
        )
        submitted = st.form_submit_button("Replace series")
        if submitted:
            rating: float | None = None
            if rating_raw:
                try:
                    rating = float(rating_raw)
                except ValueError:
                    st.error("Rating must be a number between 0 and 10.")
                    return
                if not 0 <= rating <= 10:
                    st.error("Rating must be between 0 and 10.")
                    return

            if not title or not creator:
                st.error("Title and creator are required.")
                return

            payload = {"title": title, "creator": creator, "year": int(year), "rating": rating}
            updated = update_series(api_base, selected["id"], payload)
            if updated:
                st.success(f"Updated: {updated['title']} ({updated['year']})")
                st.rerun()

    with st.form("patch-series"):
        st.markdown("Patch (PATCH)")
        new_rating = st.text_input(
            "Rating only (leave empty to skip)",
            value="",
            key="patch-rating",
        )
        submitted = st.form_submit_button("Patch series")
        if submitted:
            payload: dict[str, Any] = {}
            if new_rating:
                try:
                    payload["rating"] = float(new_rating)
                except ValueError:
                    st.error("Rating must be a number between 0 and 10.")
                    return
                if not 0 <= payload["rating"] <= 10:
                    st.error("Rating must be between 0 and 10.")
                    return

            if not payload:
                st.error("Provide at least one field to patch.")
                return

            updated = patch_series(api_base, selected["id"], payload)
            if updated:
                st.success(f"Patched: {updated['title']} ({updated.get('rating', '—')})")
                st.rerun()


def main() -> None:
    """Run the Streamlit UI."""
    st.set_page_config(page_title="TV Series Catalogue", page_icon="📺", layout="wide")
    inject_imdb_theme()
    st.markdown(
        """
        <div class="header-row">
            <div class="logo-box">TV-DB</div>
            <div style="display:flex; flex-direction:column;">
                <div style="color:#f7f7f7; font-size: 28px; font-weight: 900; letter-spacing:0.5px;">TV Series Catalogue</div>
                <div style="color: var(--imdb-muted); font-size: 14px;">Fast API-powered tracker with an IMDb-inspired coat of paint.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    api_base = _clean_base_url(API_BASE_DEFAULT)

    st.markdown(
        "",
        unsafe_allow_html=True,
    )
    series = fetch_series(api_base)

    top_area = st.container()
    with top_area:
        st.subheader("Your series")
        render_metrics(series)
        render_table(series)

    render_create_form(api_base)
    render_update_forms(api_base, series)
    render_delete_form(api_base, series)


if __name__ == "__main__":
    main()
