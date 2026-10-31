"""Utility functions for project report generation."""

from urllib.parse import urlparse


def parse_github_url(url: str) -> tuple[str, str]:
    """Parse GitHub URL to extract owner and repo name."""
    # Handle different GitHub URL formats
    if url.startswith("git@github.com:"):
        # SSH format: git@github.com:owner/repo.git
        path = url.split(":")[1]
        path = path.removesuffix(".git")
        owner, repo = path.split("/")
        return owner, repo

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    path = path.removesuffix(".git")
    parts = path.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    raise ValueError(f"Invalid GitHub URL: {url}")


def is_valid_github_url(url: str) -> bool:
    """Check if URL is a valid GitHub URL."""
    try:
        owner, repo = parse_github_url(url)
        return bool(owner and repo)
    except Exception:
        return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
