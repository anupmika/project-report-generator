"""Streamlit UI for Project Report Generator."""

import os
import tempfile

import streamlit as st

from analyzer import RepoAnalyzer
from generator import ReportGenerator
from utils import is_valid_github_url

st.set_page_config(
    page_title='Project Report Generator',
    page_icon='📊',
    layout='wide'
)

st.title('📊 Project Report Generator')
st.markdown('Generate project reports from GitHub repositories strictly according to your custom format')

# Main content
repo_url = st.text_input(
    'GitHub Repository URL',
    placeholder='https://github.com/owner/repo',
    help='Enter the full GitHub repository URL'
)

template_file = st.file_uploader(
    'Upload Project Report Format Template',
    type=['docx'],
    help='Upload your custom report format in DOCX format only'
)

output_format = st.radio(
    'Output Format',
    options=['docx', 'pdf'],
    horizontal=True,
    help='Download final report as DOCX or PDF'
)

# Generate button
if st.button('Generate Report', type='primary', use_container_width=True):
    if not repo_url:
        st.error('Please enter a GitHub repository URL')
    elif not is_valid_github_url(repo_url):
        st.error('Please enter a valid GitHub repository URL')
    elif not template_file:
        st.error('Please upload a project report format template (DOCX)')
    else:
        try:
            with st.spinner('Cloning and analyzing repository...'):
                # Save template to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_template:
                    tmp_template.write(template_file.getvalue())
                    template_path = tmp_template.name

                # Analyze repo
                analyzer = RepoAnalyzer(repo_url)
                analysis = analyzer.analyze()

            with st.spinner('Generating report according to template...'):
                # Generate report
                generator = ReportGenerator(analysis, template_path=template_path)
                report_bytes = generator.generate(output_format)

                # Clean up temp file
                os.unlink(template_path)

            st.success('✓ Report generated successfully!')

            # Download button
            repo_name = repo_url.rstrip('/').split('/')[-1]
            filename = f"{repo_name}_report.{output_format}"

            st.download_button(
                label=f"Download Report ({output_format.upper()})",
                data=report_bytes,
                file_name=filename,
                mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document' if output_format == 'docx' else 'application/pdf',
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)
