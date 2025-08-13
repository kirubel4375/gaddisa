# Database Population Guide

This guide explains how to populate the Gaddisa emergency reporting system database with sample data for testing and development.

## 📋 What Gets Created

The population script creates realistic sample data for all models:

### User Profiles (7 users)
- Users with different languages: English, Amharic, Afaan Oromo  
- Mix of users with/without location permissions
- Varied consent preferences
- Sample Telegram IDs for testing

### Agencies (20 agencies)
- **5 Police Stations**: Bole, Arada, Kirkos, Yeka, Lideta
- **5 Hospitals**: Black Lion, St. Paul, Zewditu, ALERT, Yekatit 12
- **5 NGO/Support Organizations**: Women lawyers, support centers
- **3 Government Offices**: Women/Children Affairs, Legal Aid
- **2 Shelters**: Safe Haven, Bethany House

Each agency includes:
- Complete contact information
- Realistic GPS coordinates in Addis Ababa
- Operating hours and services
- Verification status

### Incident Reports (15 reports)
- Various incident types: assault, harassment, domestic violence, etc.
- Different statuses: submitted, processing, resolved, closed
- Realistic descriptions and locations
- Associated with sample users

### Notifications (25 notifications)
- Report status updates
- Nearby agency alerts  
- System notifications
- Safety tips
- Read/unread status simulation

### Notification Channels
- Telegram channels for all users
- WebSocket channels for most users
- Email channels for some users

## 🚀 How to Run

### Method 1: Automated Script (Recommended)

**Windows:**
```bash
run_populate.bat
```

**Linux/Mac:**
```bash
chmod +x run_populate.sh
./run_populate.sh
```

### Method 2: Django Management Command

```bash
python manage.py populate_db --clear
```

### Method 3: Standalone Script

```bash
python populate_database.py --clear
```

## 📝 Options

- `--clear`: Removes existing data before populating (recommended for clean setup)
- Without `--clear`: Adds data to existing database

## 🧪 Sample Data Details

### Test Users
| Telegram ID | Language | Location Permission | Data Consent |
|-------------|----------|-------------------|--------------|
| 123456789   | English  | ✅ Granted         | ✅ Yes        |
| 234567890   | Amharic  | ✅ Granted         | ✅ Yes        |
| 345678901   | Oromo    | ❌ Denied          | ✅ Yes        |
| 456789012   | English  | ✅ Granted         | ❌ No         |
| 567890123   | Amharic  | ✅ Granted         | ✅ Yes        |
| 678901234   | Oromo    | ❌ Denied          | ✅ Yes        |
| 789012345   | English  | ✅ Granted         | ✅ Yes        |

### Key Agencies for Testing

**Emergency Services:**
- Bole Police Station: `+251114670001`
- Black Lion Hospital: `+251115517011`
- St. Paul Hospital: `+251115533666`

**Support Organizations:**
- Ethiopian Women Lawyers Association: `+251115505050`
- Safe Haven Women Shelter: `+251115606060`

**Government Services:**
- Women and Children Affairs Bureau: `+251115252525`

## 🔧 Prerequisites

1. **Virtual Environment**: Ensure your Python virtual environment is activated
2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. **Database**: Ensure database migrations are up to date:
   ```bash
   python manage.py migrate
   ```

## ⚠️ Important Notes

- **Development Only**: This sample data is for development/testing purposes only
- **Data Privacy**: Never use this script with real user data
- **Database Backup**: Always backup your database before running with `--clear`
- **Encryption**: Reports may have encrypted descriptions if encryption is configured

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError"**
- Solution: Activate virtual environment and install dependencies

**"No such table" errors**
- Solution: Run database migrations first: `python manage.py migrate`

**"ENCRYPTION_KEY" warnings**
- Solution: Set ENCRYPTION_KEY in settings (optional for testing)

**Permission errors**
- Solution: Ensure proper file permissions and directory access

### Verification

After running the script, verify data was created:

```bash
python manage.py shell
```

```python
from emergency_bot.accounts.models import UserProfile
from emergency_bot.agencies.models import Agency
from emergency_bot.reports.models import IncidentReport

print(f"Users: {UserProfile.objects.count()}")
print(f"Agencies: {Agency.objects.count()}")  
print(f"Reports: {IncidentReport.objects.count()}")
```

## 📊 Testing Scenarios

The populated data enables testing:

- **Multi-language Support**: Users with different language preferences
- **Location Services**: Users with/without location permissions
- **Incident Reporting**: Various report types and statuses
- **Notification System**: Different notification types and channels
- **Agency Discovery**: Location-based agency search
- **User Consent**: GDPR compliance testing

## 🎯 Next Steps

After populating the database:

1. **Test the Telegram Bot**: Use sample Telegram IDs to test bot functionality
2. **Test Mini App**: Navigate to different pages and test features
3. **Test API Endpoints**: Use sample data for API testing
4. **Test Notifications**: Check notification delivery and channels
5. **Test Location Features**: Verify location-based services work

---

**Need Help?** Check the main project documentation or create an issue in the repository.