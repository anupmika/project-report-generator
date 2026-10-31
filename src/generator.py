"""Report generation logic."""
from __future__ import annotations

from datetime import datetime
from formatter import ReportFormatParser
from pathlib import Path
from typing import Any

from utils import format_file_size, parse_github_url


class ReportGenerator:
    """Generate reports strictly according to a given project report format template."""

    def __init__(self, analysis: dict[str, Any], template_path: str | None = None):
        self.analysis = analysis
        self.template_path = template_path
        self.format_parser = None
        if template_path:
            self.format_parser = ReportFormatParser(template_path)

    def generate(self, format: str = 'docx') -> bytes:
        """Generate report in specified format according to template."""
        if format == 'docx':
            return self._generate_docx_from_template()
        elif format == 'pdf':
            return self._generate_pdf_from_template()
        else:
            raise ValueError(f"Unsupported format: {format}. Only 'docx' and 'pdf' are supported.")

    def _get_repo_info(self):
        """Extract repo info."""
        try:
            owner, repo = parse_github_url(self.analysis['url'])
            repo_name = f"{owner}/{repo}"
        except:
            repo_name = self.analysis['url'].rstrip('/').split('/')[-1]
        return repo_name

    def _read_repo_files(self):
        """Read important files from cloned repo."""
        repo_path = Path(self.analysis.get('path', ''))
        content = {}

        if not repo_path.exists():
            return content

        # Try to read README
        for readme_name in ['README.md', 'README.txt', 'readme.md', 'Readme.md']:
            readme_path = repo_path / readme_name
            if readme_path.exists():
                try:
                    content['readme'] = readme_path.read_text(errors='ignore')
                    break
                except:
                    pass

        # Try to read other important files
        for fname in ['package.json', 'pyproject.toml', 'requirements.txt', 'setup.py', 'Cargo.toml']:
            fpath = repo_path / fname
            if fpath.exists():
                try:
                    content[fname] = fpath.read_text(errors='ignore')[:2000]
                except:
                    pass

        return content

    def _generate_mermaid_diagrams(self):
        """Generate Mermaid diagrams for flowcharts and architecture."""
        repo_name = self._get_repo_info()
        structure = self.analysis.get('structure', {})
        files = self.analysis.get('files', [])
        languages = self.analysis.get('languages', {})
        diagrams = []
        if structure.get('directories') or structure.get('root_files'):
            flowchart = '```mermaid\ngraph TD\n'
            flowchart += f"    A[{repo_name}] --> B[Root]\n"
            for idx, d in enumerate(structure.get('directories', [])[:5]):
                flowchart += f"    B --> D{idx}[{d}/]\n"
            for idx, f in enumerate(structure.get('root_files', [])[:5]):
                flowchart += f"    B --> F{idx}[{f}]\n"
            flowchart += '```'
            diagrams.append(('Project Structure Flowchart', flowchart))
        if languages:
            tech_flow = '```mermaid\nflowchart LR\n'
            tech_flow += f"    A[{repo_name}] --> B[Tech Stack]\n"
            for idx, lang in enumerate(sorted(languages.keys())[:6]):
                tech_flow += f"    B --> T{idx}[{lang}]\n"
            tech_flow += '```'
            diagrams.append(('Technology Stack', tech_flow))
        if len(files) > 0:
            file_flow = '```mermaid\ngraph LR\n'
            file_flow += f"    A[Repository] --> B[Source Files]\n"
            file_flow += f"    B --> C[Total: {len(files)} files]\n"
            file_flow += f"    C --> D[Analyzed]\n"
            file_flow += '```'
            diagrams.append(('File Organization', file_flow))
        return diagrams

    def _fill_template_content(self, doc):
        """Fill the document template with actual data from analysis."""

        repo_name = self._get_repo_info()
        metadata = self.analysis.get('metadata', {})
        stats = self.analysis.get('stats', {})
        languages = self.analysis.get('languages', {})
        structure = self.analysis.get('structure', {})
        self.analysis.get('dependencies', {})
        files = self.analysis.get('files', [])
        repo_files_content = self._read_repo_files()
        mermaid_diagrams = self._generate_mermaid_diagrams()

        latest_commit = metadata.get('latest_commit', {})

        replacements = {
            '{{REPO_NAME}}': repo_name,
            '{{PROJECT_NAME}}': repo_name.split('/')[-1] if '/' in repo_name else repo_name,
            '{{REPO_URL}}': self.analysis['url'],
            '{{GITHUB_URL}}': self.analysis['url'],
            '{{GENERATED_DATE}}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '{{DATE}}': datetime.now().strftime('%Y-%m-%d'),
            '{{COMMIT_SHA}}': latest_commit.get('sha', 'N/A'),
            '{{LATEST_COMMIT_SHA}}': latest_commit.get('sha', 'N/A'),
            '{{COMMIT_MESSAGE}}': str(latest_commit.get('message', 'N/A')).replace('\n', ' ').strip(),
            '{{LATEST_COMMIT_MESSAGE}}': str(latest_commit.get('message', 'N/A')).replace('\n', ' ').strip(),
            '{{AUTHOR}}': str(latest_commit.get('author', 'N/A')),
            '{{COMMIT_AUTHOR}}': str(latest_commit.get('author', 'N/A')),
            '{{COMMIT_DATE}}': str(latest_commit.get('date', 'N/A')),
            '{{BRANCH}}': metadata.get('active_branch', 'N/A'),
            '{{ACTIVE_BRANCH}}': metadata.get('active_branch', 'N/A'),
            '{{COMMIT_COUNT}}': str(metadata.get('commit_count', 0)),
            '{{TOTAL_COMMITS}}': str(metadata.get('commit_count', 0)),
            '{{TOTAL_FILES}}': str(stats.get('total_files', 0)),
            '{{FILE_COUNT}}': str(stats.get('total_files', 0)),
            '{{TOTAL_SIZE}}': format_file_size(stats.get('total_size_bytes', 0)),
            '{{SIZE}}': format_file_size(stats.get('total_size_bytes', 0)),
        }

        # Add languages/tech stack
        if languages:
            lang_str = ', '.join(sorted(languages.keys()))
            replacements['{{LANGUAGES}}'] = lang_str
            replacements['{{TECH_STACK}}'] = lang_str
            replacements['{{TECHNOLOGIES}}'] = lang_str

        # Add branches
        if metadata.get('branches'):
            replacements['{{BRANCHES}}'] = ', '.join(metadata.get('branches', []))

        # Add README content (truncated)
        if repo_files_content.get('readme'):
            readme = repo_files_content['readme']
            # Clean up markdown for plain text
            replacements['{{README}}'] = readme[:3000]
            replacements['{{DESCRIPTION}}'] = readme[:500].replace('#', '').strip()
            replacements['{{PROJECT_DESCRIPTION}}'] = readme[:500].replace('#', '').strip()
            replacements['{{ABOUT}}'] = readme[:500].replace('#', '').strip()

        # Add file structure
        if structure.get('directories'):
            replacements['{{DIRECTORIES}}'] = ', '.join(structure['directories'])
        if files:
            replacements['{{FILES}}'] = '\n'.join(files[:50])
            replacements['{{FILE_LIST}}'] = '\n'.join(files[:50])

        # Replace in all paragraphs
        for para in doc.paragraphs:
            text = para.text
            changed = False
            for placeholder, value in replacements.items():
                if placeholder in text:
                    text = text.replace(placeholder, str(value))
                    changed = True
            if changed:
                para.text = text

        # Replace in all tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        text = para.text
                        changed = False
                        for placeholder, value in replacements.items():
                            if placeholder in text:
                                text = text.replace(placeholder, str(value))
                                changed = True
                        if changed:
                            para.text = text

        # If no placeholders found, intelligently fill based on headings
        if not any('{{' in p.text for p in doc.paragraphs):
            self._fill_by_headings(doc, repo_name, repo_files_content, mermaid_diagrams)
        else:
            # Add mermaid diagrams if placeholders exist
            self._add_mermaid_to_doc(doc, mermaid_diagrams)

        return doc

        return doc

    def _add_mermaid_to_doc(self, doc, mermaid_diagrams):
        """Add Mermaid diagrams to document."""
        if not mermaid_diagrams:
            return
        doc.add_paragraph()
        doc.add_heading('Diagrams and Flowcharts', level=1)
        for title, diagram in mermaid_diagrams:
            doc.add_heading(title, level=2)
            p = doc.add_paragraph()
            p.add_run(diagram)

    def _fill_by_headings(self, doc, repo_name, repo_files_content, mermaid_diagrams=None):
        """Fill template by matching headings to repo content."""
        if mermaid_diagrams is None:
            mermaid_diagrams = []
        metadata = self.analysis.get('metadata', {})
        stats = self.analysis.get('stats', {})
        languages = self.analysis.get('languages', {})
        structure = self.analysis.get('structure', {})
        self.analysis.get('dependencies', {})
        files = self.analysis.get('files', [])
        latest_commit = metadata.get('latest_commit', {})
        readme = repo_files_content.get('readme', '')

        i = 0
        paragraphs = list(doc.paragraphs)
        while i < len(paragraphs):
            para = paragraphs[i]
            text = para.text.lower().strip()
            style = para.style.name.lower()

            if style.startswith('heading'):
                # Look ahead for content paragraphs
                j = i + 1
                # Clear following empty paragraphs and replace with content
                if any(k in text for k in ['introduction', 'overview', 'abstract', 'about', 'description']):
                    # Insert description from README or generate
                    desc = readme[:800] if readme else f"This project {repo_name} is a GitHub repository containing {stats.get('total_files', 0)} files."
                    # Add content after heading
                    if j < len(doc.paragraphs):
                        doc.paragraphs[j].text = desc.strip()
                    else:
                        doc.add_paragraph(desc.strip())

                elif any(k in text for k in ['objective', 'aim', 'purpose']):
                    if j < len(doc.paragraphs):
                        doc.paragraphs[j].text = f"To analyze and document the {repo_name} project repository."

                elif any(k in text for k in ['technology', 'tech', 'tools', 'stack']):
                    if languages:
                        tech_text = 'Technologies used: ' + ', '.join(sorted(languages.keys()))
                        if j < len(doc.paragraphs):
                            doc.paragraphs[j].text = tech_text
                    elif structure.get('root_files'):
                        if j < len(doc.paragraphs):
                            doc.paragraphs[j].text = f"Project files include: {', '.join(structure['root_files'][:10])}"

                elif any(k in text for k in ['feature']):
                    if readme:
                        # Extract features from README
                        features = []
                        for line in readme.split('\n'):
                            if line.strip().startswith('-') or line.strip().startswith('*'):
                                features.append(line.strip()[1:].strip())
                        if features and j < len(doc.paragraphs):
                            doc.paragraphs[j].text = '\n'.join(features[:10])

                elif any(k in text for k in ['diagram', 'flowchart', 'architecture']):
                    # Add mermaid diagrams
                    if mermaid_diagrams:
                        for title, diagram in mermaid_diagrams:
                            doc.add_paragraph()
                            doc.add_paragraph(diagram)
                    if j < len(doc.paragraphs):
                        doc.paragraphs[j].text = f"This report documents the {repo_name} repository as analyzed on {datetime.now().strftime('%Y-%m-%d')}."

                elif any(k in text for k in ['reference', 'bibliography']):
                    if j < len(doc.paragraphs):
                        doc.paragraphs[j].text = f"GitHub Repository: {self.analysis['url']}"

            i += 1

        # Also add a summary section if document is mostly empty
        if len([p for p in doc.paragraphs if p.text.strip()]) < 5:
            doc.add_paragraph()
            doc.add_heading('Project Report', level=1)
            doc.add_paragraph(f'Project Name: {repo_name}')
            doc.add_paragraph(f'Repository URL: {self.analysis["url"]}')
            doc.add_paragraph(f'Generated On: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            doc.add_heading('Project Description', level=2)
            if readme:
                doc.add_paragraph(readme[:1000])
            else:
                doc.add_paragraph(f'This is the {repo_name} project repository.')
            doc.add_heading('Repository Statistics', level=2)
            doc.add_paragraph(f'Total Files: {stats.get("total_files", 0)}')
            doc.add_paragraph(f'Total Size: {format_file_size(stats.get("total_size_bytes", 0))}')
            doc.add_paragraph(f'Latest Commit: {latest_commit.get("sha", "N/A")} by {latest_commit.get("author", "N/A")}')
            if languages:
                doc.add_heading('Technologies Used', level=2)
                for lang in sorted(languages.keys()):
                    doc.add_paragraph(f'• {lang}')
            doc.add_heading('Project Structure', level=2)
            for d in structure.get('directories', [])[:10]:
                doc.add_paragraph(f'• {d}/')
            for f in structure.get('root_files', [])[:15]:
                doc.add_paragraph(f'• {f}')
            if files:
                doc.add_heading('Files', level=2)
                for f in files[:30]:
                    doc.add_paragraph(f'• {f}')

    def _generate_docx_from_template(self) -> bytes:
        """Generate DOCX strictly according to template format."""
        import io

        from docx import Document

        if not self.template_path or not Path(self.template_path).exists():
            raise ValueError('Project report format template (DOCX) is required')

        # Load the template
        doc = Document(self.template_path)
        # Fill in the template with actual data
        doc = self._fill_template_content(doc)

        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()

    def _generate_pdf_from_template(self) -> bytes:
        """Generate PDF strictly according to template format."""
        from docx import Document
        from weasyprint import HTML

        if not self.template_path or not Path(self.template_path).exists():
            raise ValueError('Project report format template (DOCX) is required')

        # Load template, fill it
        doc = Document(self.template_path)
        doc = self._fill_template_content(doc)

        # Convert filled docx to HTML then PDF
        html_parts = ['<!DOCTYPE html><html><head><meta charset="utf-8"><style>']
        html_parts.append('body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }')
        html_parts.append('h1 { color: #333; border-bottom: 2px solid #333; font-size: 24pt; }')
        html_parts.append('h2 { color: #444; border-bottom: 1px solid #ccc; margin-top: 30px; font-size: 18pt; }')
        html_parts.append('h3 { color: #555; font-size: 14pt; }')
        html_parts.append('h4 { color: #666; font-size: 12pt; }')
        html_parts.append('p { margin: 10px 0; }')
        html_parts.append('table { border-collapse: collapse; width: 100%; margin: 15px 0; }')
        html_parts.append('td, th { border: 1px solid #ddd; padding: 8px; text-align: left; }')
        html_parts.append('th { background-color: #f2f2f2; }')
        html_parts.append('li { margin: 5px 0; }')
        html_parts.append('ul { padding-left: 20px; }')
        html_parts.append('</style></head><body>')

        for para in doc.paragraphs:
            text = para.text
            if not text.strip():
                html_parts.append('<br>')
                continue
            style = para.style.name.lower()
            if 'heading 1' in style:
                html_parts.append(f'<h1>{text}</h1>')
            elif 'heading 2' in style:
                html_parts.append(f'<h2>{text}</h2>')
            elif 'heading 3' in style:
                html_parts.append(f'<h3>{text}</h3>')
            elif 'heading 4' in style:
                html_parts.append(f'<h4>{text}</h4>')
            elif 'list' in style:
                html_parts.append(f'<li>{text}</li>')
            else:
                html_parts.append(f'<p>{text}</p>')

        # Add tables
        for table in doc.tables:
            html_parts.append('<table>')
            for i, row in enumerate(table.rows):
                html_parts.append('<tr>')
                for cell in row.cells:
                    cell_text = ' '.join([p.text for p in cell.paragraphs])
                    if i == 0:
                        html_parts.append(f'<th>{cell_text}</th>')
                    else:
                        html_parts.append(f'<td>{cell_text}</td>')
                html_parts.append('</tr>')
            html_parts.append('</table>')

        html_parts.append('</body></html>')
        html_content = ''.join(html_parts)

        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
