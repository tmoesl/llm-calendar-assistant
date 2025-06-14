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

# Usage: Local variable pattern
config = get_calendar_config()
user_tz = config.user_timezone
```

### Service Objects: New Instances
**Mutable state and side effects that need isolation**

```python
# Pattern: Create new instances
self.client = GoogleAuthClient()          # New auth client per executor
calendar_service = GoogleCalendarService(service)  # New service per operation
```

## Available Configurations

| Config | Function | Usage |
|--------|----------|-------|
| Calendar | `get_calendar_config()` | Calendar API settings, timezone, paths |
| Database | `get_db_config()` | Database connection, pool settings |
| Worker | `get_worker_config()` | Celery/Redis configuration |
| Logger | `get_log_config()` | Logging levels, output settings |

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