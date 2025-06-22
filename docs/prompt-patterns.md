# Prompt Patterns

Template management and Jinja2 patterns for contributors extending the LLM Calendar Assistant pipeline with new prompt templates. This guide explains the essential patterns for creating, loading, and managing versioned prompt templates using the PromptManager singleton and Jinja2 templating engine.

## Template Architecture

### Frontmatter + Jinja2 Structure
All prompt templates follow a consistent structure with YAML frontmatter and Jinja2 templating:

```jinja2
---
description: A template for extracting event details from natural language
author: Applied AI Team
---

# IDENTITY AND PURPOSE
You're an AI assistant named {{ name | default('Orion') }}.

# CONTEXT  
Current datetime: {{ datetime }}
System timezone: {{ timezone }}

# TASK
Extract the following details:
{% if is_bulk_operation %}
- Process multiple events
{% else %}
- Process single event
{% endif %}
```

## Loading Patterns

### Singleton Environment
The template system uses a singleton Jinja2 environment for performance:

```python
from app.services.prompt_loader import PromptManager

# Load and render template with variables
prompt = PromptManager.get_prompt(
    "create_event_extraction",
    datetime=context.datetime_ref.dateTime,
    timezone=context.datetime_ref.timeZone
)

# Get template metadata and required variables
info = PromptManager.get_template_info("create_event_extraction")
```

### Variable Injection
Templates support dynamic variable injection with defaults:

```python
# Pipeline node usage
prompt = PromptManager.get_prompt(
    "lookup_event_extraction",
    datetime=context.datetime_ref.dateTime,
    timezone=context.datetime_ref.timeZone,
    is_bulk_operation=context.is_bulk_operation
)
```

## Template Patterns

### Required Structure
Every prompt template must include:

```jinja2
---
description: Clear description of template purpose
author: Applied AI Team  
---

# IDENTITY AND PURPOSE
Define the AI assistant role and primary function

# CONTEXT
List all input variables and their sources

# TASK
Specific extraction or validation requirements

# EXAMPLES
Provide input/output examples for clarity
```

### Variable Handling
```jinja2
# Default values for optional variables
{{ name | default('Orion') }}

# Conditional logic for different scenarios  
{% if is_bulk_operation %}
- Bulk operation instructions
{% else %}
- Single operation instructions
{% endif %}

# Required variables (no defaults)
Current datetime: {{ datetime }}
System timezone: {{ timezone }}
```

### Error Prevention
Templates use `StrictUndefined` to catch missing variables early:

```python
# This will raise TemplateError if 'required_var' is missing
prompt = PromptManager.get_prompt("template_name", required_var="value")
```

## Implementation Examples

### Adding New Template
```python
# 1. Create template file: app/prompts/new_template.j2
---
description: Template for new functionality
author: Applied AI Team
---

# IDENTITY AND PURPOSE  
You extract {{ target_data }} from user requests.

# CONTEXT
Current time: {{ datetime }}
User request: Will be provided separately

# TASK
Extract and return structured {{ target_data }}.
```

### Using in Pipeline Node
```python
class NewExtractor(Node):
    def create_completion(self, context):
        prompt = PromptManager.get_prompt(
            "new_template",
            datetime=context.datetime_ref.dateTime,
            target_data="meeting details"
        )
        
        return self.llm_provider.create_completion(
            response_model=NewResponse,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": context.request}
            ]
        )
```

### Template Debugging
```python
# Get template information and required variables
info = PromptManager.get_template_info("template_name")
print(f"Required variables: {info['variables']}")
print(f"Description: {info['description']}")

# Check frontmatter metadata
print(f"Metadata: {info['frontmatter']}")
```

## Available Templates

| Template | Purpose | Key Variables |
|----------|---------|---------------|
| **validate_event_request** | Security and legitimacy validation | None (static) |
| **classify_event_request** | Intent classification | None (static) |
| **create_event_extraction** | Extract event creation details | `datetime`, `timezone` |
| **lookup_event_extraction** | Extract event search criteria | `datetime`, `timezone`, `is_bulk_operation` |

## Benefits

✅ **Consistency**: Standardized template structure across all prompts  
✅ **Maintainability**: Version-controlled prompts with clear metadata  
✅ **Flexibility**: Dynamic variable injection for context-aware prompts  
✅ **Performance**: Singleton environment with template caching  
✅ **Reliability**: Strict variable validation prevents runtime errors

## Prompt Engineering References

For advanced prompt engineering techniques and best practices:

- **[Prompt Engineering Guide](https://www.promptingguide.ai/)** - Comprehensive resource covering all major prompting techniques, research findings, and practical applications
- **[OpenAI GPT-4.1 Prompt Engineering Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)** - Comprehensive prompting strategies and examples
- **[OpenAI Prompt Caching 101](https://cookbook.openai.com/examples/prompt_caching101)** - Optimization techniques for reducing latency and costs with cached prompts
- **[Anthropic Effective Prompt Engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)** - Advanced techniques for Claude and LLM optimization
- **[Anthropic Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)** - Agentic coding patterns and workflow optimization
- **[Google Gemini for Workspace Prompting Guide](https://services.google.com/fh/files/misc/gemini-for-workspace-prompting-guide.pdf)** - Practical prompting for productivity applications (PDF) 