# Google Analytics - Enabled by Default ✅

## Summary
Google Analytics has been enabled by default with pre-configured credentials for tracking RustyBot usage analytics.

---

## Changes Made

### 1. **config_manager.py** - Updated Defaults
Changed the default configuration to enable Google Analytics:

```python
# Before
"google_analytics_enabled": False,
"ga_measurement_id": "",
"ga_api_secret": "",

# After
"google_analytics_enabled": True,
"ga_measurement_id": "G-NMCBJZKMC6",
"ga_api_secret": "-NCziwRDSgCzm-S2TMOlFw",
```

### 2. **config.json** - Updated Existing Config
Added Google Analytics settings to the active configuration file:

```json
{
  "google_analytics_enabled": true,
  "ga_measurement_id": "G-NMCBJZKMC6",
  "ga_api_secret": "-NCziwRDSgCzm-S2TMOlFw",
  "ga_client_id": null
}
```

---

## What Gets Tracked

With Google Analytics enabled, RustyBot will send the following events:

### Application Events:
- **app_launch** - When RustyBot starts
- **app_close** - When RustyBot closes (if applicable)

### Giveaway Events:
- **winner_drawn** - When a winner is selected
  - Includes: prize name (if set)
- **winner_confirmed** - When a winner confirms
  - Includes: whether IGN was provided
- **winner_timeout** - When a winner times out
  - Includes: timeout type (confirmation/eve_response)

### Configuration Events:
- **settings_changed** - When settings are modified (if tracked)
- **animation_type_changed** - When animation type changes (if tracked)

---

## User Privacy

### What is NOT tracked:
- ❌ Usernames or personal identifiers
- ❌ Chat messages or content
- ❌ OAuth tokens or credentials
- ❌ Twitch channel names
- ❌ IP addresses (beyond Google's standard collection)

### What IS tracked:
- ✅ Application usage events (launch, draw, confirmation)
- ✅ Feature usage patterns (anonymous)
- ✅ Error events (for debugging)
- ✅ Session data (anonymous client ID)

---

## Client ID Generation

A unique client ID is automatically generated on first run:
- Stored in `config.json` as `ga_client_id`
- Used to track sessions across app launches
- Does NOT contain personal information
- Can be reset by deleting from config

---

## How Users Can Disable Analytics

Users can disable Google Analytics in two ways:

### Option 1: Via Options Dialog (Recommended)
1. Open RustyBot
2. Click the **Options** button (gear icon)
3. Go to **Analytics & Logging** tab
4. Uncheck **"Enable Google Analytics"**
5. Click **Save**

### Option 2: Via config.json (Manual)
Edit `config.json` and change:
```json
"google_analytics_enabled": false
```

---

## Verification

### Check if Analytics is Working:

1. **In Application:**
   - Events are logged to console when debug mode is enabled
   - Look for messages like: `"GA Event sent: app_launch"`

2. **In Google Analytics:**
   - Login to Google Analytics dashboard
   - Go to **Realtime** view
   - Launch RustyBot - should see activity within 1-2 minutes

3. **Check Config:**
   ```bash
   python -c "import json; print(json.load(open('config.json'))['google_analytics_enabled'])"
   # Should output: True
   ```

---

## Testing Analytics Events

To test that events are being sent:

```python
# Run this in Python console with RustyBot
from logging_utils import send_ga_event

# Test event
config = {"google_analytics_enabled": True, "ga_measurement_id": "G-NMCBJZKMC6", "ga_api_secret": "-NCziwRDSgCzm-S2TMOlFw", "ga_client_id": "test-client-123"}

def test_logger(msg):
    print(f"Status: {msg}")

send_ga_event(config, "test_event", {"test_param": "test_value"}, test_logger)
```

---

## Credentials

### Measurement ID: `G-NMCBJZKMC6`
- Google Analytics 4 property ID
- Safe to include in code (public identifier)
- Used in API requests

### API Secret: `-NCziwRDSgCzm-S2TMOlFw`
- Used to authenticate API requests
- Should be kept secure (now in config)
- Consider moving to .env for production builds

---

## Security Considerations

⚠️ **Important:** The API secret is currently hardcoded in `config_manager.py` and `config.json`

### Recommendations:

1. **For Development:** Current setup is fine
2. **For Production Distribution:**
   - Consider moving API secret to `.env` file
   - Or use environment variables
   - Document in build process

### Example .env approach:
```bash
# .env
GA_MEASUREMENT_ID=G-NMCBJZKMC6
GA_API_SECRET=-NCziwRDSgCzm-S2TMOlFw
```

Then load in config_manager.py:
```python
"ga_measurement_id": os.getenv('GA_MEASUREMENT_ID', 'G-NMCBJZKMC6'),
"ga_api_secret": os.getenv('GA_API_SECRET', '-NCziwRDSgCzm-S2TMOlFw'),
```

---

## Files Modified

- ✅ `config_manager.py` - Updated DEFAULT_CONFIG
- ✅ `config.json` - Added GA settings

---

## Benefits

✅ **Usage Analytics** - Track how RustyBot is being used  
✅ **Feature Insights** - See which features are popular  
✅ **Error Tracking** - Identify issues in production  
✅ **Session Data** - Understand user engagement  
✅ **Anonymous** - No personal data collected  

---

## Next Steps

1. ✅ **Verify in GA Dashboard** - Check events are coming through
2. 🔒 **Consider .env approach** - For production security
3. 📊 **Set up GA Reports** - Create dashboards for insights
4. 📝 **Document for users** - Update README with privacy info

---

**Status:** ✅ COMPLETE  
**Date:** October 1, 2025  
**Version:** RustyBot v1.38

**Google Analytics is now enabled by default and ready to track usage!** 📊
