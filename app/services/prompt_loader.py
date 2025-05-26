from pathlib import Path

import frontmatter
from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateError,
    TemplateNotFound,
    meta,
)

"""
Prompt Management Module

This module provides functionality for loading and rendering prompt templates with frontmatter.
It uses Jinja2 for template rendering and python-frontmatter for metadata handling,
implementing a singleton pattern for template environment management.
"""


class PromptManager:
    """Manager class for handling prompt templates and their metadata.

    This class provides functionality to load prompt templates from files,
    render them with variables, and extract template metadata and requirements.
    It implements a singleton pattern for the Jinja2 environment to ensure
    consistent template loading across the application.

    Attributes:
        _env: Class-level singleton instance of Jinja2 Environment

    Example:
        # Render a prompt template with variables
        prompt = PromptManager.get_prompt("greeting", name="Alice")

        # Get template metadata and required variables
        info = PromptManager.get_template_info("greeting")
    """

    _env = None

    @classmethod
    def _get_env(cls, templates_dir="prompts") -> Environment:
        """Gets or creates the Jinja2 environment singleton.

        Args:
            templates_dir: Directory name containing prompt templates, relative to app/

        Returns:
            Configured Jinja2 Environment instance

        Note:
            Uses StrictUndefined to raise errors for undefined variables,
            helping catch template issues early.
        """
        # Corrected path to point to app/prompts from app/service/prompt_loader.py
        base_path = Path(__file__).parent.parent
        templates_full_path = base_path / templates_dir
        if cls._env is None:
            cls._env = Environment(
                loader=FileSystemLoader(templates_full_path),
                undefined=StrictUndefined,
            )
        return cls._env

    @staticmethod
    def _load_template_file(template: str):
        """
        Internal utility to resolve and load a template file with frontmatter.

        Returns:
            A tuple containing the frontmatter.Post object and the Jinja2 Environment.
        Raises:
            FileNotFoundError: If the template file cannot be found or path is None.
        """
        env = PromptManager._get_env()
        assert env.loader is not None, "Jinja2 environment loader must be initialized"
        template_path = f"{template}.j2"

        try:
            actual_template_path = env.loader.get_source(env, template_path)[1]
        except TemplateNotFound as e:
            raise FileNotFoundError(
                f"Template file {template_path} not found at loader paths."
            ) from e

        if actual_template_path is None:
            # This case should ideally not be reached if TemplateNotFound is handled,
            # but linters might complain based on Jinja2\'s get_source type hints.
            raise FileNotFoundError(f"Template file {template_path} loaded but path is None.")

        with open(actual_template_path) as file:
            post = frontmatter.load(file)

        return post, env

    @staticmethod
    def get_prompt(template: str, **kwargs) -> str:
        """Loads and renders a prompt template with provided variables.

        Args:
            template: Name of the template file (without .j2 extension)
            **kwargs: Variables to use in template rendering

        Returns:
            Rendered template string

        Raises:
            ValueError: If template rendering fails
            FileNotFoundError: If template file doesn't exist
        """
        post, env = PromptManager._load_template_file(template)

        # Create a new template object from the content string after frontmatter processing
        template_obj = env.from_string(post.content)
        try:
            return template_obj.render(**kwargs)
        except TemplateError as e:
            raise ValueError(f"Error rendering template: {str(e)}") from e

    @staticmethod
    def get_template_info(template: str) -> dict:
        """Extracts metadata and variable requirements from a template.

        Args:
            template: Name of the template file (without .j2 extension)

        Returns:
            Dictionary containing:
                - name: Template name
                - description: Template description from frontmatter
                - author: Template author from frontmatter
                - variables: List of required template variables
                - frontmatter: Raw frontmatter metadata dictionary

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        post, env = PromptManager._load_template_file(template)

        ast = env.parse(post.content)
        variables = meta.find_undeclared_variables(ast)
        print(post.content)
        print(post.metadata)

        return {
            "name": template,
            "description": post.metadata.get("description", "No description provided"),
            "author": post.metadata.get("author", "Unknown"),
            "variables": list(variables),
            "frontmatter": post.metadata,
        }
