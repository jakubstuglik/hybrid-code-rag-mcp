"""OpenAI-compatible embedding backend (e.g. llama.cpp ``llama-server --embeddings``).

Posts to ``{base_url}/v1/embeddings`` and reuses the TEI client machinery
(prefixes, concurrent mini-batches, dimension probe) by subclassing
:class:`shared.embedding.TEIEmbedding`.

llama-server rejects inputs longer than its physical batch (``-ub``) instead
of truncating them.  When a request fails, each text is retried alone and,
if it is still rejected, truncated to ``max_tokens`` with the server's own
``/tokenize`` + ``/detokenize`` endpoints, so the cut uses the model tokenizer.

Several servers can share the load (``endpoints``): each request goes to the
eligible endpoint with the fewest in-flight requests per slot.  An endpoint
with a smaller ``max_tokens`` only gets batches whose texts are short enough
(estimated as ``len(text) / 2.5`` tokens); anything it rejects is retried on
the first (primary) endpoint.
"""

import json
import threading
import urllib.error
import urllib.request
from typing import Any, List, Optional

from llama_index.core.bridge.pydantic import PrivateAttr

from shared.embedding import TEIEmbedding
from shared.log import log_warn


class OpenAICompatEmbedding(TEIEmbedding):
    _api_model: str = PrivateAttr(default="")
    _max_tokens: int = PrivateAttr(default=4000)
    _truncated: int = PrivateAttr(default=0)
    _lock: Any = PrivateAttr(default=None)
    _endpoints: Any = PrivateAttr(default=None)
    _served: Any = PrivateAttr(default=None)

    def __init__(
        self,
        base_url: str,
        model_name: str,
        api_model: Optional[str] = None,
        max_tokens: int = 4000,
        timeout: float = 1800.0,
        query_prefix: Optional[str] = None,
        text_prefix: Optional[str] = None,
        endpoints: Optional[List[dict]] = None,
        **kwargs: Any,
    ):
        super().__init__(
            tei_url=base_url,
            model_name=model_name,
            timeout=timeout,
            query_prefix=query_prefix,
            text_prefix=text_prefix,
            **kwargs,
        )
        self._api_model = api_model or model_name
        self._max_tokens = int(max_tokens)
        self._truncated = 0
        self._lock = threading.Lock()
        eps = endpoints or [{"url": base_url, "max_tokens": max_tokens, "slots": 1}]
        self._endpoints = [
            {
                "url": e["url"].rstrip("/"),
                "max_tokens": int(e.get("max_tokens", max_tokens)),
                "slots": max(1, int(e.get("slots", 1))),
                "inflight": 0,
            }
            for e in eps
        ]
        self._tei_url = self._endpoints[0]["url"]
        self._served = {e["url"]: 0 for e in self._endpoints}

    @property
    def served_counts(self) -> dict:
        return dict(self._served)

    def _pick(self, texts: List[str]) -> dict:
        need = max((len(t) for t in texts), default=0) / 2.5
        with self._lock:
            ok = [e for e in self._endpoints if need <= e["max_tokens"] * 0.95]
            ep = min(ok or self._endpoints[:1], key=lambda e: e["inflight"] / e["slots"])
            ep["inflight"] += 1
        return ep

    @property
    def truncated_count(self) -> int:
        return self._truncated

    def _request(self, path: str, body: dict, url: Optional[str] = None) -> Any:
        req = urllib.request.Request(
            f"{url or self._tei_url}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            msg = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise RuntimeError(f"{path} returned HTTP {exc.code}: {msg[:500]}") from exc

    def _embed_at(self, url: str, texts: List[str]) -> List[List[float]]:
        result = self._request(
            "/v1/embeddings", {"input": texts, "model": self._api_model}, url
        )
        data = sorted(result["data"], key=lambda d: d["index"])
        with self._lock:
            self._served[url] += len(texts)
        return [d["embedding"] for d in data]

    def _embed_raw(self, texts: List[str]) -> List[List[float]]:
        ep = self._pick(texts)
        try:
            return self._embed_at(ep["url"], texts)
        except RuntimeError:
            if ep is self._endpoints[0]:
                raise
            # Secondary endpoint rejected it (e.g. too long): use the primary.
            return self._embed_at(self._endpoints[0]["url"], texts)
        finally:
            with self._lock:
                ep["inflight"] -= 1

    def _truncate(self, text: str) -> str:
        toks = self._request("/tokenize", {"content": text, "add_special": False})
        ids = toks["tokens"]
        if len(ids) <= self._max_tokens:
            return text
        cut = self._request("/detokenize", {"tokens": ids[: self._max_tokens]})
        with self._lock:
            self._truncated += 1
        return cut["content"]

    def _post_embed(self, texts: List[str]) -> List[List[float]]:
        try:
            return self._embed_raw(texts)
        except RuntimeError as exc:
            if len(texts) == 1:
                try:
                    return self._embed_raw([self._truncate(texts[0])])
                except RuntimeError:
                    raise exc
            log_warn(f"Embedding batch of {len(texts)} failed ({exc}); retrying one by one")
            out: List[List[float]] = []
            for t in texts:
                out.extend(self._post_embed([t]))
            return out
