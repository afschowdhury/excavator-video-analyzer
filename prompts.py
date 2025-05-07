import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import tomli  # for reading TOML files
import tomli_w as tomli_writer  # for writing TOML files


@dataclass
class PromptTemplate:
    """Base class for prompt templates"""

    name: str
    description: str
    template: str
    version: str = "1.0"
    author: str = "Excavator Analysis System"
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {"temperature": 0.2, "top_p": 0.95, "max_tokens": 2000}


class PromptManager:
    """Manages different prompt templates for video analysis"""

    def __init__(self, templates_dir="prompt_templates"):
        """
        Initialize the PromptManager with templates directory

        Args:
            templates_dir (str): Directory containing prompt template files
        """
        self.templates_dir = Path(templates_dir)
        self.prompts: Dict[str, PromptTemplate] = {}
        self._initialize_default_prompts()

    def _load_template_from_file(self, template_name: str) -> Dict[str, Any]:
        """
        Load a template from a TOML file

        Args:
            template_name (str): Name of the template file (without extension)

        Returns:
            Dict[str, Any]: The template data including metadata and content

        Raises:
            FileNotFoundError: If the template file doesn't exist
        """
        template_path = self.templates_dir / f"{template_name}.toml"
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(
            template_path, "rb"
        ) as f:  # TOML files should be opened in binary mode
            return tomli.load(f)

    def _initialize_default_prompts(self):
        """Initialize default prompt templates from TOML files"""
        # Find all .toml files in the templates directory
        template_files = list(self.templates_dir.glob("*.toml"))

        for template_file in template_files:
            try:
                template_name = template_file.stem
                template_data = self._load_template_from_file(template_name)

                self.prompts[template_name] = PromptTemplate(
                    name=template_data["metadata"]["name"],
                    description=template_data["metadata"]["description"],
                    template=template_data["template"]["content"],
                    version=template_data["metadata"].get("version", "1.0"),
                    author=template_data["metadata"].get(
                        "author", "Excavator Analysis System"
                    ),
                    config=template_data.get("config", {}),
                )
            except Exception as e:
                print(f"Warning: Failed to load template {template_file.name}: {e}")

    def get_prompt(self, prompt_type: str) -> str:
        """
        Get a prompt template by type

        Args:
            prompt_type (str): Type of prompt to retrieve

        Returns:
            str: The prompt template

        Raises:
            KeyError: If the prompt type doesn't exist
        """
        if prompt_type not in self.prompts:
            raise KeyError(
                f"Prompt type '{prompt_type}' not found. Available types: {list(self.prompts.keys())}"
            )
        return self.prompts[prompt_type].template

    def get_prompt_config(self, prompt_type: str) -> Dict[str, Any]:
        """
        Get the configuration for a prompt type

        Args:
            prompt_type (str): Type of prompt to retrieve

        Returns:
            Dict[str, Any]: The prompt configuration

        Raises:
            KeyError: If the prompt type doesn't exist
        """
        if prompt_type not in self.prompts:
            raise KeyError(
                f"Prompt type '{prompt_type}' not found. Available types: {list(self.prompts.keys())}"
            )
        return self.prompts[prompt_type].config

    def add_prompt(
        self,
        prompt_type: str,
        template: str,
        description: str,
        version: str = "1.0",
        author: str = "Excavator Analysis System",
        config: Dict[str, Any] = None,
    ):
        """
        Add a new prompt template and save it to a TOML file

        Args:
            prompt_type (str): Unique identifier for the prompt
            template (str): The prompt template text
            description (str): Description of what the prompt does
            version (str): Version of the prompt template
            author (str): Author of the prompt template
            config (Dict[str, Any]): Configuration for the prompt
        """
        # Create the prompt template
        prompt = PromptTemplate(
            name=prompt_type.capitalize(),
            description=description,
            template=template,
            version=version,
            author=author,
            config=config,
        )

        # Save to TOML file
        self.save_prompt_to_file(prompt_type, prompt)

        # Add to prompts dictionary
        self.prompts[prompt_type] = prompt

    def save_prompt_to_file(self, prompt_type: str, prompt: PromptTemplate) -> Path:
        """
        Save a prompt template to a TOML file

        Args:
            prompt_type (str): Type of prompt to save
            prompt (PromptTemplate): The prompt template to save

        Returns:
            Path: Path to the saved template file
        """
        template_data = {
            "metadata": {
                "name": prompt.name,
                "description": prompt.description,
                "version": prompt.version,
                "author": prompt.author,
            },
            "template": {"content": prompt.template},
            "config": prompt.config,
        }

        template_path = self.templates_dir / f"{prompt_type}.toml"
        with open(
            template_path, "wb"
        ) as f:  # TOML files should be written in binary mode
            tomli_writer.dump(template_data, f)

        return template_path

    def list_prompts(self) -> Dict[str, str]:
        """
        List all available prompts with their descriptions

        Returns:
            Dict[str, str]: Dictionary of prompt types and their descriptions
        """
        return {name: prompt.description for name, prompt in self.prompts.items()}

    def get_prompt_info(self, prompt_type: str) -> Optional[PromptTemplate]:
        """
        Get detailed information about a specific prompt

        Args:
            prompt_type (str): Type of prompt to retrieve

        Returns:
            Optional[PromptTemplate]: Prompt template information or None if not found
        """
        return self.prompts.get(prompt_type)
