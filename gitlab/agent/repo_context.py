"""Project Onboarding Context & Repository Index Cache.

Provides pre-indexed repository metadata, allowed directory boundaries,
and key framework paths so agents do not need to scan the entire tree on every run.
"""
import os
import json
from typing import Dict, Any, List, Optional


ONBOARDING_CACHE_FILE = ".agent-state/repo-context.json"


class RepoContext:
    def __init__(self, repo_dir: str, cache_path: Optional[str] = None):
        self.repo_dir = repo_dir
        self.cache_path = cache_path or os.path.join(repo_dir, ONBOARDING_CACHE_FILE)

    def load_or_build_context(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Loads repository onboarding context from cache or builds it if missing."""
        if not force_rebuild and os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        context = self.build_context()
        self.save_context(context)
        return context

    def build_context(self) -> Dict[str, Any]:
        """Scans repository structure once to produce an onboarding context cache."""
        has_package_json = os.path.exists(os.path.join(self.repo_dir, "package.json"))
        has_astro = os.path.exists(os.path.join(self.repo_dir, "astro.config.mjs")) or os.path.exists(
            os.path.join(self.repo_dir, "astro.config.ts")
        )

        content_collections = []
        content_dir = os.path.join(self.repo_dir, "src/content")
        if os.path.isdir(content_dir):
            content_collections = [
                d for d in os.listdir(content_dir) if os.path.isdir(os.path.join(content_dir, d))
            ]

        return {
            "framework": "Astro" if has_astro else ("Node.js" if has_package_json else "Generic"),
            "has_package_json": has_package_json,
            "content_collections": sorted(content_collections),
            "type_scopes": {
                "content": [
                    "src/content/",
                    "src/data/",
                    "public/project-images/",
                    "public/assets/img/",
                    "public/decks/",
                ],
                "fix": ["src/", "public/", "scripts/"],
                "refresh": ["src/", "public/", "scripts/"],
            },
            "build_pipeline": {
                "fast_checks": ["git diff --check"],
                "heavy_checks": [
                    "npm ci",
                    "npm run build",
                    "node scripts/validate-build.mjs",
                    "node scripts/validate-links.mjs",
                ],
            },
        }

    def save_context(self, context: Dict[str, Any]) -> None:
        """Persists the onboarding context to disk."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2)
