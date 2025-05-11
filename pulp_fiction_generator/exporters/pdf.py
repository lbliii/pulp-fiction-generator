"""
PDF exporter for Pulp Fiction Generator.
"""

import os
from .base import BaseExporter
from .exceptions import ExporterFileError, ExporterDependencyError
from ...utils.errors import logger


class PdfExporter(BaseExporter):
    """Exporter for PDF format."""
    
    @staticmethod
    def check_dependencies() -> bool:
        """
        Check if required dependencies are installed.
        Looks for WeasyPrint first, then pdfkit as a fallback.
        
        Returns:
            bool: True if at least one PDF dependency is available
        """
        try:
            # Try primary dependency
            import weasyprint
            return True
        except ImportError:
            try:
                # Try fallback dependency
                import pdfkit
                return True
            except ImportError:
                return False
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export content as PDF.
        
        Args:
            content: The story content to export
            output_path: Path where the exported file should be saved
            
        Returns:
            The path to the exported file
            
        Raises:
            ExporterDependencyError: If no PDF export library is installed
            ExporterFileError: If unable to write to the output file
        """
        try:
            # First convert to HTML with PDF-specific styling
            html_path = output_path.replace(".pdf", "_temp.html")
            
            try:
                import markdown
            except ImportError:
                raise ExporterDependencyError(
                    "markdown package is required for PDF export. "
                    "Install with: pip install markdown"
                )
            
            # Create enhanced HTML with better typography for print
            title = self.extract_title(content) or "Generated Story"
            
            pdf_html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            margin: 2cm;
            size: A4;
            @top-center {{
                content: "{title}";
                font-family: Georgia, serif;
                font-style: italic;
                font-size: 10pt;
            }}
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-family: Georgia, serif;
                font-size: 10pt;
            }}
        }}
        body {{
            font-family: Georgia, serif;
            font-size: 12pt;
            line-height: 1.5;
            text-align: justify;
            hyphens: auto;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            font-family: "Bookman Old Style", Georgia, serif;
            font-size: 24pt;
            text-align: center;
            page-break-after: avoid;
            margin-top: 2cm;
            margin-bottom: 1.5cm;
        }}
        h2 {{
            font-family: "Bookman Old Style", Georgia, serif;
            font-size: 18pt;
            page-break-after: avoid;
            margin-top: 1.5cm;
            margin-bottom: 0.5cm;
        }}
        h3 {{
            font-family: "Bookman Old Style", Georgia, serif;
            font-size: 14pt;
            page-break-after: avoid;
            margin-top: 1cm;
            margin-bottom: 0.3cm;
        }}
        p {{
            margin-bottom: 0.5cm;
            text-indent: 1.5em;
            orphans: 3;
            widows: 3;
        }}
        /* First paragraph after heading has no indent */
        h1 + p, h2 + p, h3 + p, h4 + p, h5 + p, h6 + p {{
            text-indent: 0;
        }}
        blockquote {{
            font-style: italic;
            border-left: 3px solid #888;
            padding-left: 1em;
            margin-left: 1em;
            margin-right: 1em;
        }}
        hr {{
            border: none;
            border-top: 1px solid #888;
            margin: 2em auto;
            width: 50%;
        }}
        /* Add proper spacing for chapter breaks */
        h2 {{
            page-break-before: always;
        }}
        h1 + h2 {{
            page-break-before: avoid;
        }}
        /* Make sure the title page stands alone */
        h1:first-child {{
            page-break-after: always;
        }}
    </style>
</head>
<body>
    {markdown.markdown(content)}
</body>
</html>
            """
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(pdf_html_content)
            
            # Try primary PDF generator (WeasyPrint)
            try:
                from weasyprint import HTML
                HTML(html_path).write_pdf(output_path)
                
                # Remove temporary HTML file
                os.remove(html_path)
                return output_path
            except ImportError:
                logger.info("WeasyPrint not installed. Falling back to alternative PDF export.")
                
                # Try alternative PDF export with pdfkit
                try:
                    import pdfkit
                    
                    # Configure pdfkit options for better output
                    options = {
                        'page-size': 'A4',
                        'margin-top': '2cm',
                        'margin-right': '2cm',
                        'margin-bottom': '2cm',
                        'margin-left': '2cm',
                        'encoding': 'UTF-8',
                        'no-outline': None,
                        'enable-local-file-access': None
                    }
                    
                    pdfkit.from_file(html_path, output_path, options=options)
                    
                    # Remove temporary HTML file
                    os.remove(html_path)
                    return output_path
                except ImportError:
                    # Clean up HTML file before raising error
                    if os.path.exists(html_path):
                        os.remove(html_path)
                    
                    raise ExporterDependencyError(
                        "No PDF export library available. "
                        "Install with: pip install weasyprint or pip install pdfkit"
                    )
                except Exception as e:
                    # Clean up HTML file before raising error
                    if os.path.exists(html_path):
                        os.remove(html_path)
                    
                    logger.error(f"Error with pdfkit export: {e}")
                    raise ExporterFileError(f"Error exporting to PDF: {e}") from e
            except Exception as e:
                # Clean up HTML file before raising error
                if os.path.exists(html_path):
                    os.remove(html_path)
                
                logger.error(f"Error with WeasyPrint export: {e}")
                raise ExporterFileError(f"Error exporting to PDF: {e}") from e
                
        except ExporterDependencyError:
            # Re-raise dependency errors
            raise
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise ExporterFileError(f"Error exporting to PDF: {e}") from e 