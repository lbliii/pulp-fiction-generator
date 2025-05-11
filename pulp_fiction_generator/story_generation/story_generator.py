"""
StoryGenerator module responsible for generating stories.
"""

import os
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..models.ollama_adapter import OllamaAdapter
from ..agents.agent_factory import AgentFactory
from ..crews.crew_coordinator import CrewCoordinator
from ..crews.config.crew_coordinator_config import CrewCoordinatorConfig
from ..crews.crew_executor import CrewExecutor
from ..plots import plot_registry
from ..utils.story_persistence import StoryPersistence
from ..story_model.state import StoryStateManager
from .generation_config import GenerationConfig

@dataclass
class GenerationResult:
    """Result of a story generation operation"""
    success: bool
    story_text: str = ""
    error: str = ""
    stats: Dict[str, Any] = None

class StoryGenerator:
    """Handles the story generation process"""
    
    def __init__(
        self,
        config: GenerationConfig,
        story_state: Any,
        story_state_manager: StoryStateManager,
        story_persistence: StoryPersistence,
        plugin_genre: Optional[Any] = None,
    ):
        """Initialize the story generator"""
        self.config = config
        self.story_state = story_state
        self.story_state_manager = story_state_manager
        self.story_persistence = story_persistence
        self.plugin_genre = plugin_genre
        
        # Initialize tracking variables
        self.token_count = 0
        self.start_time = 0
        self.task_times = []
        
        # Initialize model and coordinator
        self.ollama_adapter = self._initialize_model()
        self.crew_executor = CrewExecutor(debug_mode=config.verbose)
        self.agent_factory = AgentFactory(self.ollama_adapter)
        self.crew_coordinator = self._initialize_crew_coordinator()
        
        # Progress display
        self.progress_display = None
        self.execution_task = None
        
    def _initialize_model(self) -> OllamaAdapter:
        """Initialize the Ollama model adapter"""
        return OllamaAdapter.from_env(
            model=self.config.model,
            num_ctx=self.config.ollama_ctx_size,
            num_gpu=self.config.ollama_gpu_layers,
            num_thread=self.config.ollama_threads,
            batch_size=self.config.ollama_batch_size,
        )
    
    def _initialize_crew_coordinator(self) -> CrewCoordinator:
        """Initialize the crew coordinator"""
        crew_coordinator_config = CrewCoordinatorConfig(
            debug_mode=self.config.verbose,
            verbose=self.config.verbose,
            process="sequential",
        )
        
        coordinator = CrewCoordinator(
            agent_factory=self.agent_factory,
            model_service=self.ollama_adapter,
            config=crew_coordinator_config
        )
        
        # Apply plugin enhancements if available
        if self.plugin_genre:
            try:
                # Instantiate the plugin
                genre_plugin_instance = self.plugin_genre()
                
                # Get prompt enhancers for each agent type
                prompt_enhancers = genre_plugin_instance.get_prompt_enhancers()
                
                # Apply prompt enhancers to crew coordinator or agent factory
                if hasattr(coordinator, 'set_prompt_enhancers'):
                    coordinator.set_prompt_enhancers(prompt_enhancers)
            except Exception as e:
                print(f"Warning: Error applying plugin enhancements: {e}")
        
        return coordinator
    
    def generate(self) -> GenerationResult:
        """Generate a story based on the configuration"""
        try:
            # Register event listeners
            self._setup_event_listeners()
            
            # Start progress tracking
            with Progress() as self.progress_display:
                self.execution_task = self.progress_display.add_task(
                    f"Generating story...", total=100
                )
                
                # Start tracking time
                self.start_time = time.time()
                
                # Choose generation method based on config
                if self.config.chunked:
                    return self._generate_chunked()
                else:
                    return self._generate_standard()
                    
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    def _setup_event_listeners(self):
        """Set up event listeners for progress and token tracking"""
        # Progress callback for CrewAI events
        def progress_callback(completed_tasks, total_tasks, progress, remaining):
            if self.progress_display and self.execution_task:
                # Update progress bar
                if progress is not None:
                    self.progress_display.update(self.execution_task, completed=int(progress))
                    
                    # Calculate time metrics for better estimates
                    elapsed = time.time() - self.start_time
                    if completed_tasks > 0:
                        # Track task completion times for better estimates
                        task_time = elapsed / completed_tasks
                        self.task_times.append(task_time)
                        
                        # Use the average of the last 5 tasks for more accurate estimates
                        recent_tasks = self.task_times[-5:] if len(self.task_times) > 5 else self.task_times
                        avg_task_time = sum(recent_tasks) / len(recent_tasks)
                        
                        # Calculate remaining time based on tasks left
                        tasks_left = total_tasks - completed_tasks
                        est_remaining_time = avg_task_time * tasks_left
                        
                        # Format time string with hours if needed
                        if est_remaining_time > 3600:
                            hours = int(est_remaining_time / 3600)
                            minutes = int((est_remaining_time % 3600) / 60)
                            time_str = f"{hours}h {minutes}m"
                        else:
                            minutes = int(est_remaining_time / 60)
                            seconds = int(est_remaining_time % 60)
                            time_str = f"{minutes}m {seconds}s"
                        
                        # Format progress description with detailed metrics
                        self.progress_display.update(
                            self.execution_task, 
                            description=f"Generating story... Task {completed_tasks}/{total_tasks} ({progress:.1f}%), ~{time_str} remaining",
                            completed=int(progress)
                        )
                    else:
                        self.progress_display.update(
                            self.execution_task, 
                            description=f"Generating story... Task {completed_tasks}/{total_tasks} ({progress:.1f}%)",
                            completed=int(progress)
                        )
        
        # Token tracking callback for CrewAI events
        def token_callback(source, event):
            if hasattr(event, 'tokens_used'):
                self.token_count += event.tokens_used
                
                # Calculate token rate
                elapsed = time.time() - self.start_time
                tokens_per_second = self.token_count / elapsed if elapsed > 0 else 0
                tokens_per_minute = tokens_per_second * 60
                
                if self.progress_display and self.execution_task:
                    # Only update description if significant change in tokens to avoid flickering
                    if self.token_count % 50 == 0:
                        self.progress_display.update(
                            self.execution_task,
                            description=f"Generating story... {self.token_count:,} tokens ({tokens_per_minute:.1f} tokens/min)"
                        )
        
        # Register event listeners
        progress_listener = self.crew_executor.create_custom_event_listener(callback=progress_callback)
        token_listener = self.crew_executor.add_token_tracking_listener(callback=token_callback)
    
    def _generate_chunked(self) -> GenerationResult:
        """Generate a story using the chunked method"""
        print(f"Generating {self.config.genre} story using chunked method...")
        
        # Define a callback for chunked progress updates
        def chunk_callback(stage, result):
            # Update the progress display with the current stage
            if self.progress_display and self.execution_task:
                self.progress_display.update(
                    self.execution_task, 
                    description=f"Generating {stage}..."
                )
            if self.config.verbose and result:
                print(f"Completed {stage}")
        
        try:
            custom_inputs = self._prepare_custom_inputs()
            
            results = self.crew_coordinator.generate_story_chunked(
                self.config.genre,
                custom_inputs=custom_inputs,
                chunk_callback=chunk_callback,
                story_state=self.story_state_manager,
                timeout_seconds=self.config.timeout
            )
            
            # Process results
            if isinstance(results, dict):
                content = results.get("final_story", "")
            elif hasattr(results, 'final_story'):
                content = results.final_story
            else:
                content = str(results)
                
            # Update progress to complete
            if self.progress_display and self.execution_task:
                self.progress_display.update(self.execution_task, completed=100)
            
            # Finalize the story
            chapter_title = self.config.title or f"Chapter {self.story_state_manager.get_chapter_count() + 1}"
            final_result = self._finalize_story(content, chapter_title)
            
            return GenerationResult(
                success=True,
                story_text=content,
                stats={
                    "token_count": self.token_count,
                    "generation_time": time.time() - self.start_time
                }
            )
        except Exception as e:
            print(f"Error during chunked generation: {str(e)}")
            if self.config.verbose:
                import traceback
                traceback.print_exc()
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    def _generate_standard(self) -> GenerationResult:
        """Generate a story using the standard method"""
        # Add title suffix for display
        title_suffix = f" ({self.config.title})" if self.config.title else ""
        print(f"Generating {self.config.genre} story{title_suffix}...")
        
        try:
            # Add a fake task for token counting in regular generation
            if self.progress_display:
                token_task = self.progress_display.add_task(
                    f"LLM token usage: 0", 
                    total=None,
                    visible=self.config.verbose
                )
            
            # Prepare custom inputs
            custom_inputs = self._prepare_custom_inputs()
            
            # Generate the story
            if self.config.use_flow:
                content = "Flow-based generation is not implemented yet"
            elif self.config.use_yaml_crew:
                content = self.crew_coordinator.generate_story(
                    self.config.genre, 
                    custom_inputs=custom_inputs,
                    debug_mode=self.config.verbose,
                    timeout_seconds=self.config.timeout,
                    use_yaml_crew=True
                )
            else:
                content = self.crew_coordinator.generate_story(
                    self.config.genre, 
                    custom_inputs=custom_inputs,
                    debug_mode=self.config.verbose,
                    timeout_seconds=self.config.timeout,
                    use_yaml_crew=False
                )
                
            generation_time = time.time() - self.start_time
            
            # Update progress to complete
            if self.progress_display and self.execution_task:
                self.progress_display.update(self.execution_task, completed=100)
            
            if not content:
                return GenerationResult(
                    success=False,
                    error="Failed to generate content"
                )
                
            # Finalize the story
            chapter_title = self.config.title or f"Chapter {self.story_state_manager.get_chapter_count() + 1}"
            file_path, word_count, char_count = self._finalize_story(content, chapter_title)
            
            # Calculate stats
            tokens_per_second = self.token_count / generation_time if self.token_count > 0 and generation_time > 0 else 0
            words_per_second = word_count / generation_time
            
            # Print stats
            print(f"Generated {word_count} words ({char_count} characters)")
            print(f"Generation time: {generation_time:.2f} seconds")
            print(f"Speed: {words_per_second:.2f} words/sec")
            if self.token_count > 0:
                print(f"Token usage: {self.token_count:,} tokens ({tokens_per_second:.2f} tokens/sec)")
            
            return GenerationResult(
                success=True,
                story_text=content,
                stats={
                    "word_count": word_count,
                    "char_count": char_count,
                    "token_count": self.token_count,
                    "generation_time": generation_time,
                    "tokens_per_second": tokens_per_second,
                    "words_per_second": words_per_second
                }
            )
        except Exception as e:
            print(f"Error generating story: {str(e)}")
            if self.config.verbose:
                import traceback
                traceback.print_exc()
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    def _prepare_custom_inputs(self) -> Dict[str, Any]:
        """Prepare custom inputs for story generation"""
        custom_inputs = {}
        
        # Add plot template inputs if specified
        if self.config.plot_template:
            plot_data = plot_registry.get_template(self.config.plot_template)
            if plot_data:
                custom_inputs = plot_data.get("inputs", {})
                if self.config.verbose:
                    print(f"Using plot template: {self.config.plot_template}")
        
        # Add state if we're continuing a story
        if self.story_state_manager and (self.config.resume or self.config.continue_from):
            custom_inputs["previous_content"] = "\n\n".join(self.story_state_manager.get_chapters())
            
        return custom_inputs
    
    def _finalize_story(self, content, chapter_title):
        """Finalize the story and save it if needed"""
        # Make sure we have some content, even if just a fallback message
        if not content or not content.strip():
            content = f"Your {self.config.genre} story titled '{chapter_title}' could not be generated due to technical issues."
            
        # Calculate word and character counts
        word_count = len(content.split())
        char_count = len(content)
        
        # Save to state manager
        if self.story_state_manager:
            # Determine chapter number
            chapter_num = self.story_state_manager.get_chapter_count() + 1
            
            # Add chapter to state
            self.story_state_manager.add_chapter(chapter_num, content)
            
            # Save state if requested
            if self.config.save_state:
                # Update story state
                self.story_state.add_chapter(
                    chapter_num=chapter_num,
                    content=content,
                    title=chapter_title
                )
                
                # Save the story state
                story_id = self.story_persistence.save_story(self.story_state)
                print(f"Story state saved with ID: {story_id}")
                
                # Also save in the story state manager's project directory
                self.story_state_manager.save_chapter(content, chapter_title)
        
        # Construct output file path
        output_file = f"{chapter_title.lower().replace(' ', '_')}_{self.story_state_manager.get_chapter_count()}.txt"
        
        return output_file, word_count, char_count 