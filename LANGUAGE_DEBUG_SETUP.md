# Language Debug Logging Setup Guide

This guide explains how to use the comprehensive language preference debugging system for the Emergency Bot.

## Files Created

1. **`language_debug_logging.py`** - Core logging framework
2. **`debug_language_preferences.py`** - Debug utility script
3. **Enhanced logging in:**
   - `emergency_bot/telegram_bot/language_bridge.py`
   - `emergency_bot/utils/translations.py`

## Quick Start

### 1. Test the Language System

```bash
# Run a comprehensive system check
python debug_language_preferences.py --generate-report

# Test language changes for a specific user
python debug_language_preferences.py --test-user 123456 --language am

# Check database health
python debug_language_preferences.py --health-check

# View recent log activity
python debug_language_preferences.py --log-summary
```

### 2. Log File Locations

After running the system, logs will be created in the `logs/` directory:

- **`logs/language_operations.log`** - All language operations (INFO+)
- **`logs/language_errors.log`** - Only errors and critical issues (ERROR+)
- **`logs/language_debug.log`** - Detailed debug information (DEBUG+)

### 3. Real-time Monitoring

To monitor language issues in real-time while users interact with the bot:

```bash
# Monitor all operations
tail -f logs/language_operations.log

# Monitor only errors
tail -f logs/language_errors.log

# Monitor debug details
tail -f logs/language_debug.log
```

## Troubleshooting Common Issues

### Issue: "Error updating language preference. Please try again."

**What to check:**

1. **View the error logs:**
   ```bash
   tail -20 logs/language_errors.log
   ```

2. **Run a specific user test:**
   ```bash
   python debug_language_preferences.py --test-user [USER_ID] --language am
   ```

3. **Check database connectivity:**
   ```bash
   python debug_language_preferences.py --health-check
   ```

### Issue: Language changes not persisting

**Debugging steps:**

1. **Test database operations:**
   ```bash
   python debug_language_preferences.py --simulate [USER_ID]
   ```

2. **Check for database permission issues:**
   ```bash
   grep -i "permission\|denied\|readonly" logs/language_errors.log
   ```

3. **Verify user profile exists:**
   ```bash
   python manage.py shell
   >>> from emergency_bot.accounts.models import UserProfile
   >>> user = UserProfile.objects.get(telegram_id="[USER_ID]")
   >>> print(f"Current language: {user.language}")
   ```

### Issue: Bot not responding to language changes

**Check these logs:**

1. **Telegram callback handling:**
   ```bash
   grep "language_button_callback" logs/language_debug.log
   ```

2. **Language extraction from callback data:**
   ```bash
   grep "setlang_" logs/language_debug.log
   ```

3. **Async/sync communication:**
   ```bash
   grep "sync_to_async\|update_user_language_async" logs/language_debug.log
   ```

## Log Analysis Examples

### Finding Failed Language Changes

```bash
# Find all failed language change attempts
grep "LANGUAGE_CHANGE_FAILED" logs/language_operations.log

# Find database update failures
grep "DB_UPDATE_FAILED" logs/language_operations.log

# Find specific user's language operations
grep "User 123456" logs/language_operations.log
```

### Analyzing Performance Issues

```bash
# Find slow operations (look for long delays between related log entries)
grep -A 5 -B 5 "update_user_language_async called" logs/language_debug.log

# Find database connection issues
grep -i "connection\|timeout\|database" logs/language_errors.log
```

## Integration with Bot Monitoring

### Adding to Bot Startup

Add this to your bot startup script to initialize logging:

```python
from language_debug_logging import setup_language_logging
setup_language_logging()
```

### Monitoring in Production

Set up log rotation and monitoring:

```bash
# Add to crontab for log rotation
0 0 * * * find /path/to/logs -name "*.log" -size +50M -exec gzip {} \;

# Monitor for critical errors
*/5 * * * * grep "CRITICAL\|ERROR" /path/to/logs/language_errors.log | tail -10
```

## Debugging Workflow

When a user reports language issues:

1. **Get the user's Telegram ID**
2. **Run user-specific test:**
   ```bash
   python debug_language_preferences.py --test-user [TELEGRAM_ID] --language am --detailed
   ```
3. **Check recent logs for that user:**
   ```bash
   grep "[TELEGRAM_ID]" logs/language_operations.log | tail -20
   ```
4. **If issues persist, run simulation:**
   ```bash
   python debug_language_preferences.py --simulate [TELEGRAM_ID] --detailed
   ```
5. **Generate comprehensive report:**
   ```bash
   python debug_language_preferences.py --generate-report --detailed
   ```

## Understanding Log Entries

### Successful Language Change
```
[2024-01-15 10:30:15.123] [INFO    ] [language_ops.emergency_bot.telegram_bot.language_bridge] LANGUAGE_CHANGE_SUCCESS: User 123456 changed from 'en' to 'am'
[2024-01-15 10:30:15.125] [DEBUG   ] [language_ops.emergency_bot.utils.translations] DB_UPDATE_SUCCESS: UserProfile for user 123456 fields=['language']
```

### Failed Language Change
```
[2024-01-15 10:30:15.123] [ERROR   ] [language_ops.emergency_bot.telegram_bot.language_bridge] LANGUAGE_CHANGE_FAILED: User 123456 failed to change from 'en' to 'am' - Database connection failed
[2024-01-15 10:30:15.125] [ERROR   ] [language_ops.emergency_bot.utils.translations] DB_UPDATE_FAILED: UserProfile for user 123456 fields=['language'] - Connection timeout
```

## Tips for Effective Debugging

1. **Always check the timestamp** - Issues might be intermittent
2. **Look for patterns** - Multiple users having the same issue indicates system problems
3. **Check the full flow** - From button click to database update
4. **Monitor resource usage** - Database connection limits, memory usage
5. **Test edge cases** - New users, users without profiles, invalid language codes

## Contact Information

If you need help interpreting logs or have questions about the debugging system, contact the development team with:
- Log excerpts showing the issue
- User ID(s) affected
- Timestamp of when the issue occurred
- Output from the debug utility script