"""Command-line interface for project report generator."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from analyzer import RepoAnalyzer
from generator import ReportGenerator
from utils import is_valid_github_url

console = Console()


@click.command()
@click.argument('repo_url')
@click.option(
    '-t',
    '--template',
    type=click.Path(exists=True),
    required=True,
    help='Project report format template in DOCX format (required)',
)
@click.option(
    '-f',
    '--format',
    type=click.Choice(['docx', 'pdf'], case_sensitive=False),
    default='docx',
    help='Output format (default: docx)',
)
@click.option(
    '-o',
    '--output',
    type=click.Path(),
    required=True,
    help='Output file path (required)',
)
def main(repo_url: str, template: str, format: str, output: str):
    """Generate a project report from GitHub repo strictly according to a given DOCX format template."""

    if not is_valid_github_url(repo_url):
        console.print(f"[red]Error:[/red] Invalid GitHub URL: {repo_url}")
        console.print(
            'Please provide a valid GitHub repository URL (e.g., https://github.com/owner/repo)'
        )
        sys.exit(1)

    if not template.endswith('.docx'):
        console.print('[red]Error:[/red] Template must be in DOCX format')
        sys.exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn('[progress.description]{task.description}'),
            console=console,
        ) as progress:
            task = progress.add_task('Cloning and analyzing repository...', total=None)
            analyzer = RepoAnalyzer(repo_url)
            analysis = analyzer.analyze()
            progress.update(task, description='Generating report from template...')
            generator = ReportGenerator(analysis, template_path=template)
            report_bytes = generator.generate(format.lower())
            progress.update(task, description='Done!')

        output_path = Path(output)
        fmt = format.lower()
        if fmt == 'docx' and not str(output_path).endswith('.docx'):
            output_path = output_path.with_suffix('.docx')
        elif fmt == 'pdf' and not str(output_path).endswith('.pdf'):
            output_path = output_path.with_suffix('.pdf')

        output_path.write_bytes(report_bytes)
        console.print(f"[green]✓[/green] Report saved to: {output_path}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
