# Development Patterns

Code patterns and architectural guidelines for contributors working with the LLM Calendar Assistant codebase. This guide explains the key patterns used to ensure performance, maintainability, and consistency across all modules.

## Configuration Pattern

### Singleton Configs vs New Service Instances
Different object types require different lifecycle patterns to ensure performance and thread safety.

**Configuration objects**: Immutable, shared via `@lru_cache` singleton
**Service objects**: Mutable state, create new instances

```python
# Configs: Singleton pattern
@lru_cache
def get_calendar_config() -> CalendarConfig:
    return CalendarConfig()

# Usage
config = get_calendar_config()
user_tz = config.user_timezone

# Services: New instances  
calendar_service = GoogleCalendarService(service)
llm_factory = LLMFactory("openai")
```

## Domain Architecture

Self-contained functional areas with consistent structure:

```
app/
├── calendar/     # Google Calendar API
├── database/     # PostgreSQL/sessions
├── worker/       # Celery/Redis
├── llm/          # OpenAI/Anthropic
└── logging/      # Structured logging
```

Each domain contains:
- `config.py` - Configuration classes with `@lru_cache`
- `factory.py` - Service creation and runtime behavior
- `__init__.py` - Package structure

## Available Configurations

| Config | Function | Usage |
|--------|----------|-------|
| **Calendar** | `get_calendar_config()` | API settings, timezone, paths |
| **Database** | `get_db_config()` | Connection, pool settings |
| **Worker** | `get_worker_config()` | Celery/Redis configuration |
| **LLM** | `get_llm_config()` | Model settings, API keys |
| **Logging** | `get_log_config()` | Levels, output, service tags |

## Implementation Examples

```python
# 1. Config pattern
@lru_cache
def get_*_config() -> *Config:
    return *Config()

# 2. Usage pattern
config = get_*_config()
value = config.property_name

# 3. Service pattern
service = ServiceClass()  # New instances
```

## Benefits

✅ **Performance**: Single config instances, cached via @lru_cache  
✅ **Consistency**: Same configuration across entire application  
✅ **Isolation**: Service objects remain independent  
✅ **Maintainability**: Clear separation of concerns  
✅ **Testability**: Easy to mock config functions 

---