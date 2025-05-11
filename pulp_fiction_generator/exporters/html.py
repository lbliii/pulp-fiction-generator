"""
HTML exporter for Pulp Fiction Generator.
"""

from .base import BaseExporter
from .exceptions import ExporterFileError, ExporterDependencyError
from ...utils.errors import logger


class HtmlExporter(BaseExporter):
    """Exporter for HTML format."""
    
    @staticmethod
    def check_dependencies() -> bool:
        """
        Check if markdown package is installed.
        
        Returns:
            bool: True if dependencies are available, False otherwise
        """
        try:
            import markdown
            return True
        except ImportError:
            return False
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export content as HTML.
        
        Args:
            content: The story content to export
            output_path: Path where the exported file should be saved
            
        Returns:
            The path to the exported file
            
        Raises:
            ExporterDependencyError: If markdown package is not installed
            ExporterFileError: If unable to write to the output file
        """
        try:
            import markdown
        except ImportError:
            raise ExporterDependencyError(
                "markdown package is required for HTML export. "
                "Install with: pip install markdown"
            )
            
        try:
            # Create responsive HTML with light/dark mode support
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Story</title>
    <style>
        :root {{
            --text-color: #333;
            --bg-color: #f8f5f0;
            --accent-color: #7c3636;
            --highlight-color: #e6dacf;
            --spacing: 1.6rem;
        }}
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {{
            :root {{
                --text-color: #e4e4e4;
                --bg-color: #1a1a1a;
                --accent-color: #bf6060;
                --highlight-color: #2c2826;
            }}
        }}
        
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.6;
            margin: 0 auto;
            max-width: 800px;
            padding: var(--spacing);
            color: var(--text-color);
            background-color: var(--bg-color);
            transition: background-color 0.3s ease;
        }}
        
        .container {{
            background-color: var(--bg-color);
            border-radius: 5px;
            padding: var(--spacing);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Bookman Old Style', 'Palatino Linotype', serif;
            margin-top: calc(var(--spacing) * 1.5);
            color: var(--accent-color);
        }}
        
        h1 {{
            text-align: center;
            margin-bottom: calc(var(--spacing) * 1.5);
            font-size: 2.5rem;
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 0.5rem;
            letter-spacing: 1px;
        }}
        
        h2 {{
            font-size: 1.8rem;
            border-bottom: 1px solid var(--accent-color);
            padding-bottom: 0.3rem;
        }}
        
        p {{
            margin-bottom: calc(var(--spacing) * 0.75);
            text-align: justify;
            text-indent: 1.5em;
            font-size: 1.1rem;
        }}
        
        /* Remove text indent for first paragraph after headings */
        h1 + p, h2 + p, h3 + p, h4 + p, h5 + p, h6 + p {{
            text-indent: 0;
        }}
        
        blockquote {{
            font-style: italic;
            border-left: 4px solid var(--accent-color);
            padding-left: 1rem;
            margin-left: 0;
            background-color: var(--highlight-color);
            padding: 1rem;
            border-radius: 0 5px 5px 0;
        }}
        
        /* Theme toggle button */
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: var(--accent-color);
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }}
        
        /* Progress indicator */
        .progress-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: transparent;
            z-index: 100;
        }}
        
        .progress-bar {{
            height: 5px;
            background: var(--accent-color);
            width: 0%;
        }}
        
        /* Font size controls */
        .controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .control-btn {{
            background-color: var(--accent-color);
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }}
        
        @media (max-width: 600px) {{
            body {{
                padding: calc(var(--spacing) / 2);
                font-size: 0.95rem;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .theme-toggle, .controls {{
                position: static;
                margin: 10px 0;
            }}
            
            .controls {{
                flex-direction: row;
                justify-content: center;
            }}
            
            .container {{
                padding: calc(var(--spacing) / 2);
            }}
        }}
    </style>
</head>
<body>
    <div class="progress-container">
        <div class="progress-bar" id="progressBar"></div>
    </div>
    
    <button class="theme-toggle" id="themeToggle">☀️</button>
    
    <div class="container">
        {markdown.markdown(content)}
    </div>
    
    <div class="controls">
        <button class="control-btn" id="fontIncrease">A+</button>
        <button class="control-btn" id="fontDecrease">A-</button>
    </div>
    
    <script>
        // Theme Toggle
        const themeToggle = document.getElementById('themeToggle');
        let darkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Set initial icon
        themeToggle.textContent = darkMode ? '☀️' : '🌙';
        
        themeToggle.addEventListener('click', () => {{
            darkMode = !darkMode;
            document.documentElement.style.setProperty('--text-color', darkMode ? '#e4e4e4' : '#333');
            document.documentElement.style.setProperty('--bg-color', darkMode ? '#1a1a1a' : '#f8f5f0');
            document.documentElement.style.setProperty('--accent-color', darkMode ? '#bf6060' : '#7c3636');
            document.documentElement.style.setProperty('--highlight-color', darkMode ? '#2c2826' : '#e6dacf');
            themeToggle.textContent = darkMode ? '☀️' : '🌙';
        }});
        
        // Reading Progress
        window.onscroll = function() {{
            let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            let scrolled = (winScroll / height) * 100;
            document.getElementById("progressBar").style.width = scrolled + "%";
        }};
        
        // Font Size Controls
        const fontIncrease = document.getElementById('fontIncrease');
        const fontDecrease = document.getElementById('fontDecrease');
        
        // Get current font size
        let currentFontSize = parseFloat(getComputedStyle(document.body).fontSize);
        
        fontIncrease.addEventListener('click', () => {{
            if (currentFontSize < 24) {{
                currentFontSize += 1;
                document.body.style.fontSize = currentFontSize + 'px';
            }}
        }});
        
        fontDecrease.addEventListener('click', () => {{
            if (currentFontSize > 12) {{
                currentFontSize -= 1;
                document.body.style.fontSize = currentFontSize + 'px';
            }}
        }});
    </script>
</body>
</html>
            """
            
            # Write HTML to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            return output_path
        except Exception as e:
            logger.error(f"Error exporting to HTML: {e}")
            raise ExporterFileError(f"Error exporting to HTML: {e}") from e 