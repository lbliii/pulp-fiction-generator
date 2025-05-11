"""
Configuration class for story generation.
"""

from typing import Optional

class GenerationConfig:
    """Configuration class for story generation parameters"""
    
    def __init__(
        self,
        genre: str,
        chapters: int = 1,
        output_file: Optional[str] = None,
        model: str = "llama3.2",
        title: Optional[str] = None,
        save_state: bool = True,
        continue_from: Optional[str] = None,
        resume: Optional[str] = None,
        plot_template: Optional[str] = None,
        verbose: bool = False,
        chunked: bool = False,
        timeout: int = 120,
        use_yaml_crew: bool = False,
        ollama_threads: Optional[int] = None,
        ollama_gpu_layers: Optional[int] = None,
        ollama_ctx_size: Optional[int] = None,
        ollama_batch_size: Optional[int] = None,
        use_flow: bool = False,
        plot_flow: bool = False,
        output_format: str = "plain",
    ):
        """Initialize generation configuration"""
        self.genre = genre
        self.chapters = chapters
        self.output_file = output_file
        self.model = model
        self.title = title
        self.save_state = save_state
        self.continue_from = continue_from
        self.resume = resume
        self.plot_template = plot_template
        self.verbose = verbose
        self.chunked = chunked
        self.timeout = timeout
        self.use_yaml_crew = use_yaml_crew
        self.ollama_threads = ollama_threads
        self.ollama_gpu_layers = ollama_gpu_layers
        self.ollama_ctx_size = ollama_ctx_size
        self.ollama_batch_size = ollama_batch_size
        self.use_flow = use_flow
        self.plot_flow = plot_flow
        self.output_format = output_format 