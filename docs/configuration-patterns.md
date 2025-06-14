# Configuration Patterns

## Overview

This codebase follows a consistent pattern for handling configuration objects vs service objects to ensure optimal performance and architectural clarity.

## Core Principles

### Configuration Objects: Singleton Pattern
**Immutable data that should be shared across the application**

```python
# Pattern: @lru_cache singleton
@lru_cache
def get_calendar_config() -> CalendarConfig:
    return CalendarConfig()

@lru_cache  
def get_llm_config() -> LLMConfig:
    return LLMConfig()

@lru_cache
def get_log_config() -> LogConfig:
    return LogConfig()

# Usage: Local variable pattern
config = get_calendar_config()
user_tz = config.user_timezone

llm_config = get_llm_config()
openai_settings = llm_config.openai

log_config = get_log_config()
log_level = log_config.level
```

### Service Objects: New Instances
**Mutable state and side effects that need isolation**

```python
# Pattern: Create new instances
self.client = GoogleAuthClient()          # New auth client per executor
calendar_service = GoogleCalendarService(service)  # New service per operation
llm_factory = LLMFactory("openai")        # New factory per pipeline node
db_session = get_db_session()             # New session per request
```

## Domain-Based Architecture

This codebase follows a **pure domain separation** approach where each functional area is self-contained:

```
app/
├── calendar/     # Calendar domain (Google Calendar API)
├── database/     # Database domain (PostgreSQL/sessions) 
├── worker/       # Worker domain (Celery/Redis)
├── llm/          # LLM domain (OpenAI/Anthropic)
└── logging/      # Logging domain (structured logging)
```

Each domain contains:
- `config.py` - Configuration classes with `@lru_cache` singleton
- `factory.py` or service files - Runtime behavior and object creation
- `__init__.py` - Package structure

## Available Configurations

| Config | Function | Domain Location | Usage |
|--------|----------|-----------------|-------|
| Calendar | `get_calendar_config()` | `app/calendar/` | Calendar API settings, timezone, paths |
| Database | `get_db_config()` | `app/database/` | Database connection, pool settings |
| Worker | `get_worker_config()` | `app/worker/` | Celery/Redis configuration |
| LLM | `get_llm_config()` | `app/llm/` | OpenAI/Anthropic API settings, model configs |
| Logging | `get_log_config()` | `app/logging/` | Logging levels, output settings, service tags |

## Implementation Structure

```python
# 1. Config Module Pattern
@lru_cache
def get_*_config() -> *Config:
    """Get configuration. Uses lru_cache to avoid repeated loading"""
    return *Config()

# 2. Usage Pattern  
config = get_*_config()
value = config.property_name

# 3. Service Pattern
service_instance = ServiceClass()  # Always new instances
```

## Benefits

✅ **Performance**: Single config instances, cached via @lru_cache  
✅ **Consistency**: Same configuration across entire application  
✅ **Isolation**: Service objects remain independent  
✅ **Maintainability**: Clear separation of concerns  
✅ **Testability**: Easy to mock config functions 