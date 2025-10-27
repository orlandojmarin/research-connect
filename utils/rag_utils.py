# utils/rag_utils.py
from typing import List, Dict, Any
import os

# Read from Streamlit secrets, with env fallback (so it also works on Cloud Run)
try:
    import streamlit as st
    _secrets = st.secrets
except Exception:
    _secrets = {}

def _get(key: str, default: str | None = None) -> str | None:
    if _secrets and key in _secrets:
        return _secrets[key]
    return os.getenv(key, default)

PROJECT_ID = _get("GCP_PROJECT_ID")
LOCATION   = _get("VERTEX_SEARCH_LOCATION", "global")
ENGINE_ID  = _get("VERTEX_SEARCH_APP_ID")  # your Search App (Engine) ID

from google.cloud import discoveryengine_v1 as de  # Vertex AI Search / Discovery Engine

class RAGSearchError(Exception):
    """Raised for config/call issues with Vertex AI Search."""
    pass

def _serving_config_path() -> str:
    """
    For Site search with AI mode:
    projects/{project}/locations/{location}/collections/default_collection/engines/{engine}/servingConfigs/default_config
    """
    if not PROJECT_ID or not LOCATION or not ENGINE_ID:
        raise RAGSearchError(
            "Missing config: GCP_PROJECT_ID / VERTEX_SEARCH_LOCATION / VERTEX_SEARCH_APP_ID."
        )
    return (
        f"projects/{PROJECT_ID}/locations/{LOCATION}"
        f"/collections/default_collection/engines/{ENGINE_ID}"
        f"/servingConfigs/default_config"
    )

def query_vertex_search(user_query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Query Vertex AI Search and return a list of hits:
    [{title, uri, snippet, score}]
    """
    try:
        client = de.SearchServiceClient()
        req = de.SearchRequest(
            serving_config=_serving_config_path(),
            query=user_query,
            page_size=top_k,
        )
        resp = client.search(request=req)

        results: List[Dict[str, Any]] = []
        for r in resp:
            doc = r.document
            # Try common fields safely
            derived = doc.derived_struct_data or {}
            title = (
                getattr(doc, "title", None)
                or derived.get("title")
                or derived.get("pageTitle")
                or doc.uri
                or "Result"
            )
            uri = getattr(doc, "uri", None) or derived.get("uri") or derived.get("link")
            snippet = (
                derived.get("snippet")
                or derived.get("extract")
                or derived.get("content")
                or ""
            )
            results.append({
                "title": title,
                "uri": uri,
                "snippet": snippet.strip(),
                "score": getattr(r, "score", None),
            })
        return results
    except Exception as e:
        raise RAGSearchError(f"Vertex AI Search error: {e}") from e

def format_context(results: List[Dict[str, Any]], max_chars: int = 2400) -> str:
    """
    Convert search hits into a compact context block for the LLM.
    """
    if not results:
        return ""
    buf, used = [], 0
    for r in results:
        piece = (
            f"- Source: {r.get('title')}\n"
            f"  Excerpt: {r.get('snippet','')}\n"
            f"  Link: {r.get('uri','')}\n"
        )
        if used + len(piece) > max_chars:
            break
        buf.append(piece)
        used += len(piece)
    return "Relevant SCSU context:\n" + "\n".join(buf)
