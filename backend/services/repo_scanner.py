"""Repository analysis, language detection, and secret scanning service."""
from __future__ import annotations
import re
import time
import uuid
from pathlib import Path
from typing import List, Tuple
from models.schemas import RepoSummary, RepoFileMeta
from core.logging import logger

class RepoScannerService:
    def __init__(self, max_context_chars: int) -> None:
        self.max_context_chars = max_context_chars
        self._lang_map = {".py":"Python",".js":"JavaScript",".ts":"TypeScript",".rs":"Rust",".go":"Go",
                          ".java":"Java",".cpp":"C++",".h":"C",".yaml":"YAML",".yml":"YAML",".json":"JSON",".toml":"TOML"}
        self._secret_re = [r"api[_-]?key\s*[:=]\s*['\"][\w-]{20,}['\"]", r"(?:password|secret|token)\s*[:=]\s*['\"][^\s]{8,}['\"]"]
        self._entry_files = {"main.py","index.js","app.ts","main.rs","main.go","pom.xml","package.json","Cargo.toml","go.mod"}

    def scan(self, files: List[Tuple[str, str]]) -> RepoSummary:
        tid = str(uuid.uuid4())[:8]
        start = time.perf_counter()
        logger.info("Starting repository scan", trace=tid, file_count=len(files))
        metas: List[RepoFileMeta] = []
        secrets = 0
        for path, content in files:
            ext = Path(path).suffix.lower()
            lang = self._lang_map.get(ext, "Other")
            is_cfg = ext in {".yaml",".yml",".json",".toml",".env",".cfg",".ini"}
            is_entry = Path(path).name in self._entry_files
            has_sec = any(re.search(p, content, re.IGNORECASE) for p in self._secret_re)
            if has_sec: secrets += 1
            metas.append(RepoFileMeta(path=path, size_bytes=len(content.encode()), language=lang,
                                      is_config=is_cfg, is_entrypoint=is_entry, contains_secrets=has_sec))
        lang_dist: dict[str, int] = {}
        for m in metas: lang_dist[m.language] = lang_dist.get(m.language, 0) + 1
        largest = sorted(metas, key=lambda x: x.size_bytes, reverse=True)[:5]
        entries = [m.path for m in metas if m.is_entrypoint]
        dur = (time.perf_counter() - start) * 1000
        logger.info("Repo scan complete", trace=tid, files=len(metas), secrets=secrets, duration_ms=round(dur, 2))
        return RepoSummary(
            total_files=len(metas), languages=lang_dist,
            largest_files=[m.path for m in largest], entry_points=entries,
            secrets_detected=secrets, notes="Scan complete. Review secrets before AI processing."
        )

    def build_context_prompt(self, files: List[Tuple[str, str]]) -> str:
        parts = []
        total_len = 0
        for path, content in files:
            chunk = f"\n--- File: {path} ---\n{content[:1500]}\n"
            if total_len + len(chunk) > self.max_context_chars:
                break
            parts.append(chunk)
            total_len += len(chunk)
        return "".join(parts)
