import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET

import tomli  
import tomli_w as tomli_writer  


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
            self.config = {"temperature": 0.2, "top_p": 0.95}


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
        ) as f:  
            return tomli.load(f)

    def _load_poml_template(self, template_path: Path) -> Dict[str, Any]:
        """
        Load and parse a POML template file

        Args:
            template_path (Path): Path to the POML file

        Returns:
            Dict[str, Any]: Parsed POML data including template and config

        Raises:
            FileNotFoundError: If the template file doesn't exist
        """
        if not template_path.exists():
            raise FileNotFoundError(f"POML template file not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            poml_content = f.read()

        # Parse the POML XML structure
        try:
            root = ET.fromstring(poml_content)
        except ET.ParseError as e:
            raise ValueError(f"Invalid POML syntax in {template_path.name}: {e}")

        # Extract components
        role = self._get_poml_text(root, 'role', '')
        task = self._get_poml_text(root, 'task', '')
        output_format = self._get_poml_text(root, 'output-format', '')
        
        # Extract examples
        examples = []
        for example in root.findall('example'):
            examples.append(example.text.strip() if example.text else '')

        # Extract stylesheet configuration
        config = {}
        stylesheet = root.find('stylesheet')
        if stylesheet is not None:
            if stylesheet.text:
                # Parse stylesheet properties
                for line in stylesheet.text.strip().split('\n'):
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Convert to appropriate type
                        if value.replace('.', '').isdigit():
                            config[key] = float(value) if '.' in value else int(value)
                        else:
                            config[key] = value

        # Build the complete prompt template
        template_parts = []
        
        if role:
            template_parts.append(f"Role: {role}")
        
        if task:
            template_parts.append(f"\nTask: {task}")
        
        if examples:
            template_parts.append("\n\nExamples:")
            for i, example in enumerate(examples, 1):
                template_parts.append(f"\nExample {i}:\n{example}")
        
        if output_format:
            template_parts.append(f"\n\nOutput Format:\n{output_format}")

        template = '\n'.join(template_parts)

        # Extract metadata
        name = template_path.stem.replace('_', ' ').title()
        description = f"POML-based {name} template"

        return {
            'name': name,
            'description': description,
            'template': template,
            'config': config,
            'version': '2.0',  # POML version
            'author': 'Excavator Analysis System (POML)'
        }

    def _get_poml_text(self, root: ET.Element, tag: str, default: str = '') -> str:
        """
        Extract text content from a POML tag

        Args:
            root: Root element
            tag: Tag name to find
            default: Default value if tag not found

        Returns:
            str: Text content of the tag
        """
        element = root.find(tag)
        if element is not None:
            # Get all text including nested elements
            text_parts = []
            if element.text:
                text_parts.append(element.text.strip())
            for child in element:
                if child.text:
                    text_parts.append(child.text.strip())
                if child.tail:
                    text_parts.append(child.tail.strip())
            return '\n'.join(text_parts) if text_parts else default
        return default

    def _initialize_default_prompts(self):
        """Initialize default prompt templates from both TOML and POML files"""
        # Find all .toml and .poml files in the templates directory
        toml_files = list(self.templates_dir.glob("*.toml"))
        poml_files = list(self.templates_dir.glob("*.poml"))

        # Load TOML templates (legacy format)
        for template_file in toml_files:
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
                print(f"Warning: Failed to load TOML template {template_file.name}: {e}")

        # Load POML templates (new format)
        for template_file in poml_files:
            try:
                template_name = template_file.stem
                poml_data = self._load_poml_template(template_file)

                self.prompts[template_name] = PromptTemplate(
                    name=poml_data["name"],
                    description=poml_data["description"],
                    template=poml_data["template"],
                    version=poml_data.get("version", "1.0"),
                    author=poml_data.get("author", "Excavator Analysis System"),
                    config=poml_data.get("config", {}),
                )
            except Exception as e:
                print(f"Warning: Failed to load POML template {template_file.name}: {e}")

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


        self.save_prompt_to_file(prompt_type, prompt)

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
        ) as f:  
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


class POMLParser:
    """Parser for POML (Prompt-Oriented Markup Language) structured outputs"""

    @staticmethod
    def parse_cycles(poml_text: str) -> List[Dict[str, Any]]:
        """
        Parse POML cycle markup from AI response

        Args:
            poml_text (str): Text containing POML cycle markup

        Returns:
            List[Dict[str, Any]]: List of parsed cycle dictionaries
        """
        cycles = []
        
        # Extract cycle blocks using regex
        cycle_pattern = r'<cycle\s+id="(\d+)"\s+start="([^"]+)"\s+end="([^"]+)"(?:\s+total_duration="([^"]+)")?>(.*?)</cycle>'
        cycle_matches = re.finditer(cycle_pattern, poml_text, re.DOTALL)
        
        for match in cycle_matches:
            cycle_id = int(match.group(1))
            start = match.group(2)
            end = match.group(3)
            total_duration = match.group(4) or "0s"
            content = match.group(5)
            
            # Parse phases within cycle
            phases = {}
            phase_pattern = r'<(\w+)\s+start="([^"]+)"\s+end="([^"]+)"\s+duration="([^"]+)"(?:\s+description="([^"]+)")?\s*/>'
            phase_matches = re.finditer(phase_pattern, content)
            
            for phase_match in phase_matches:
                phase_name = phase_match.group(1)
                phases[phase_name] = {
                    'start': phase_match.group(2),
                    'end': phase_match.group(3),
                    'duration': phase_match.group(4),
                    'description': phase_match.group(5) or ''
                }
            
            cycles.append({
                'id': cycle_id,
                'start': start,
                'end': end,
                'total_duration': total_duration,
                'phases': phases
            })
        
        return cycles

    @staticmethod
    def parse_summary(poml_text: str) -> Dict[str, Any]:
        """
        Parse POML summary section

        Args:
            poml_text (str): Text containing POML summary markup

        Returns:
            Dict[str, Any]: Parsed summary data
        """
        summary = {}
        
        # Extract summary block
        summary_pattern = r'<summary>(.*?)</summary>'
        summary_match = re.search(summary_pattern, poml_text, re.DOTALL)
        
        if summary_match:
            summary_content = summary_match.group(1)
            
            # Parse individual summary fields
            field_pattern = r'<(\w+)(?:\s+id="([^"]+)")?(?:\s+time="([^"]+)")?>([^<]*)</\1>'
            field_matches = re.finditer(field_pattern, summary_content)
            
            for field_match in field_matches:
                field_name = field_match.group(1)
                field_value = field_match.group(4).strip()
                
                # Handle fields with attributes (like fastest_cycle)
                if field_match.group(2) or field_match.group(3):
                    summary[field_name] = {
                        'value': field_value,
                        'id': field_match.group(2),
                        'time': field_match.group(3)
                    }
                else:
                    summary[field_name] = field_value
        
        return summary

    @staticmethod
    def parse_evaluation(poml_text: str) -> Dict[str, Any]:
        """
        Parse POML evaluation markup

        Args:
            poml_text (str): Text containing POML evaluation markup

        Returns:
            Dict[str, Any]: Parsed evaluation data
        """
        evaluation = {}
        
        # Extract evaluation block
        eval_pattern = r'<evaluation>(.*?)</evaluation>'
        eval_match = re.search(eval_pattern, poml_text, re.DOTALL)
        
        if eval_match:
            eval_content = eval_match.group(1)
            
            # Parse evaluation categories
            category_pattern = r'<(\w+)\s+score="([^"]+)">(.*?)</\1>'
            category_matches = re.finditer(category_pattern, eval_content, re.DOTALL)
            
            for cat_match in category_matches:
                category_name = cat_match.group(1)
                score = cat_match.group(2)
                category_content = cat_match.group(3)
                
                # Parse strengths and improvements
                strengths = []
                improvements = []
                
                strength_pattern = r'<strength timestamp="([^"]+)">([^<]+)</strength>'
                improvement_pattern = r'<improvement timestamp="([^"]+)">([^<]+)</improvement>'
                
                for strength_match in re.finditer(strength_pattern, category_content):
                    strengths.append({
                        'timestamp': strength_match.group(1),
                        'description': strength_match.group(2)
                    })
                
                for improvement_match in re.finditer(improvement_pattern, category_content):
                    improvements.append({
                        'timestamp': improvement_match.group(1),
                        'description': improvement_match.group(2)
                    })
                
                evaluation[category_name] = {
                    'score': score,
                    'strengths': strengths,
                    'improvements': improvements
                }
        
        return evaluation

    @staticmethod
    def extract_plain_text(poml_text: str) -> str:
        """
        Extract plain text content, removing POML markup

        Args:
            poml_text (str): Text with POML markup

        Returns:
            str: Plain text without markup
        """
        # Remove XML-style tags but preserve content
        text = re.sub(r'<[^>]+>', '', poml_text)
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
