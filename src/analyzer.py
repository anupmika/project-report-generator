"""Repository analysis logic."""

import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

# pyrefly: ignore[missing-import]
from git import Repo


class RepoAnalyzer:
    """Analyze a GitHub repository and extract metadata."""

    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.temp_dir = None
        self.repo = None

    def clone_repo(self) -> Path:
        """Clone repository to temporary directory."""
        self.temp_dir = tempfile.mkdtemp(prefix='project_report_')
        self.repo = Repo.clone_from(self.repo_url, self.temp_dir)
        return Path(self.temp_dir)

    def analyze(self) -> dict[str, Any]:
        """Perform comprehensive repository analysis."""
        if not self.repo:
            self.clone_repo()

        repo_path = Path(self.temp_dir)

        analysis = {
            'url': self.repo_url,
            'path': str(repo_path),
            'metadata': self._get_metadata(),
            'structure': self._get_structure(),
            'languages': self._get_languages(),
            'dependencies': self._get_dependencies(),
            'stats': self._get_stats(),
            'files': self._get_file_list(),
        }
        return analysis

    def _get_metadata(self) -> dict[str, Any]:
        """Get repository metadata."""
        try:
            head = self.repo.head.commit
            branches = [str(b) for b in self.repo.branches]
            remotes = {r.name: next(iter(r.urls)) for r in self.repo.remotes}

            return {
                'commit_count': sum(1 for _ in self.repo.iter_commits()),
                'latest_commit': {
                    'sha': head.hexsha[:7],
                    'message': head.message.strip(),
                    'author': str(head.author),
                    'date': head.committed_datetime.isoformat(),
                },
                'branches': branches,
                'remotes': remotes,
                'active_branch': self.repo.active_branch.name,
            }
        except Exception as e:
            return {'error': str(e)}

    def _get_structure(self) -> dict[str, Any]:
        """Get repository directory structure."""
        repo_path = Path(self.temp_dir)
        structure = {
            'directories': [],
            'root_files': [],
        }

        try:
            for item in repo_path.iterdir():
                if item.name.startswith('.git'):
                    continue
                if item.is_dir():
                    structure['directories'].append(item.name)
                else:
                    structure['root_files'].append(item.name)
        except Exception as e:
            structure['error'] = str(e)

        return structure

    def _get_languages(self) -> dict[str, int]:
        """Detect programming languages used."""
        repo_path = Path(self.temp_dir)
        extensions = defaultdict(int)
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.cs': 'C#',
        }

        try:
            for root, dirs, files in os.walk(repo_path):
                if '.git' in root:
                    continue
                for file in files:
                    ext = Path(file).suffix.lower()
                    if ext in lang_map:
                        full_path = Path(root) / file
                        try:
                            extensions[lang_map[ext]] += full_path.stat().st_size
                        except:
                            extensions[lang_map[ext]] += 1
        except Exception as e:
            return {'error': str(e)}

        return dict(extensions)

    def _get_dependencies(self) -> dict[str, list[str]]:
        """Extract dependency information from common files."""
        repo_path = Path(self.temp_dir)
        deps = {}

        dep_files = {
            'requirements.txt': 'pip',
            'pyproject.toml': 'poetry/uv',
            'package.json': 'npm',
            'Pipfile': 'pipenv',
            'Cargo.toml': 'cargo',
            'go.mod': 'go',
        }

        for filename, manager in dep_files.items():
            filepath = repo_path / filename
            if filepath.exists():
                try:
                    content = filepath.read_text(errors='ignore')
                    deps[manager] = {'file': filename, 'content': content[:1000]}
                except Exception as e:
                    deps[manager] = {'file': filename, 'error': str(e)}

        return deps

    def _get_stats(self) -> dict[str, Any]:
        """Get repository statistics."""
        repo_path = Path(self.temp_dir)
        total_files = 0
        total_size = 0

        try:
            for root, dirs, files in os.walk(repo_path):
                if '.git' in root:
                    continue
                for file in files:
                    total_files += 1
                    full_path = Path(root) / file
                    try:
                        total_size += full_path.stat().st_size
                    except:
                        pass
        except Exception as e:
            return {'error': str(e)}

        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
        }

    def _get_file_list(self) -> list[str]:
        """Get list of files (limited)."""
        repo_path = Path(self.temp_dir)
        files = []

        try:
            for root, dirs, filenames in os.walk(repo_path):
                if '.git' in root:
                    continue
                for fname in filenames[:100]:  # Limit to avoid huge lists
                    rel_path = Path(root).relative_to(repo_path) / fname
                    if str(rel_path) != '.':
                        files.append(str(rel_path))
            return sorted(files)[:200]  # Return top 200
        except Exception:
            return []

    def cleanup(self):
        """Clean up temporary directory."""
        # Could implement cleanup if needed
