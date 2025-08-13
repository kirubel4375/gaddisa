#!/usr/bin/env python
"""
Standalone script to populate the database with sample data.
Run this from the project root directory:
    python populate_database.py
"""

import os
import sys
import django
from datetime import timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.utils import timezone
from django.db import transaction

from emergency_bot.accounts.models import UserProfile
from emergency_bot.agencies.models import Agency
from emergency_bot.reports.models import IncidentReport
from emergency_bot.notifications.models import Notification, NotificationChannel


def clear_data():
    """Clear existing data from all models"""
    print("Clearing existing data...")
    Notification.objects.all().delete()
    NotificationChannel.objects.all().delete()
    IncidentReport.objects.all().delete()
    Agency.objects.all().delete()
    UserProfile.objects.all().delete()
    print("✓ Data cleared")


def create_users():
    """Create sample user profiles"""
    print("Creating user profiles...")
    
    users_data = [
        {
            'telegram_id': '123456789',
            'language': 'en',
            'latitude': 9.0054,
            'longitude': 38.7636,
            'location_permission_granted': True,
            'data_consent': True,
        },
        {
            'telegram_id': '234567890',
            'language': 'am',
            'latitude': 9.0365,
            'longitude': 38.7578,
            'location_permission_granted': True,
            'data_consent': True,
        },
        {
            'telegram_id': '345678901',
            'language': 'om',
            'latitude': 8.9806,
            'longitude': 38.7578,
            'location_permission_granted': False,
            'data_consent': True,
        },
        {
            'telegram_id': '456789012',
            'language': 'en',
            'latitude': 9.0123,
            'longitude': 38.7456,
            'location_permission_granted': True,
            'data_consent': False,
        },
        {
            'telegram_id': '567890123',
            'language': 'am',
            'latitude': 8.9890,
            'longitude': 38.7890,
            'location_permission_granted': True,
            'data_consent': True,
        },
        {
            'telegram_id': '678901234',
            'language': 'om',
            'latitude': 9.0200,
            'longitude': 38.7600,
            'location_permission_granted': False,
            'data_consent': True,
        },
        {
            'telegram_id': '789012345',
            'language': 'en',
            'latitude': 9.0100,
            'longitude': 38.7700,
            'location_permission_granted': True,
            'data_consent': True,
        },
    ]

    users = []
    for user_data in users_data:
        user = UserProfile.objects.create(**user_data)
        if user.location_permission_granted:
            user.update_location(user_data['latitude'], user_data['longitude'])
        if user.data_consent:
            user.grant_consent()
        users.append(user)

    print(f"✓ Created {len(users)} user profiles")
    return users


def create_agencies():
    """Create sample agencies"""
    print("Creating agencies...")
    
    agencies_data = [
        # Police Stations
        {
            'name': 'Bole Police Station',
            'type': 'police',
            'description': 'Main police station serving the Bole area with 24/7 emergency response.',
            'region': 'Addis Ababa',
            'zone': 'Bole',
            'woreda': '03',
            'kebele': '07',
            'phone': '+251114670001',
            'alt_phone': '+251911123456',
            'email': 'bole.police@addisababa.gov.et',
            'address': 'Bole Road, near Edna Mall, Addis Ababa',
            'latitude': 8.9936,
            'longitude': 38.7870,
            'hours_of_operation': '24/7',
            'services': 'Emergency response, crime reporting, investigation, traffic control',
            'verified': True,
        },
        {
            'name': 'Arada Police Station',
            'type': 'police',
            'description': 'Central police station in Arada sub-city serving Piazza area.',
            'region': 'Addis Ababa',
            'zone': 'Arada',
            'woreda': '02',
            'kebele': '01',
            'phone': '+251114456001',
            'alt_phone': '+251911234567',
            'email': 'arada.police@addisababa.gov.et',
            'address': 'Piazza, Churchill Avenue, Addis Ababa',
            'latitude': 9.0370,
            'longitude': 38.7510,
            'hours_of_operation': '24/7',
            'services': 'Law enforcement, emergency response, crime investigation',
            'verified': True,
        },
        {
            'name': 'Kirkos Police Station',
            'type': 'police',
            'description': 'Police station serving Kirkos sub-city and surrounding areas.',
            'region': 'Addis Ababa',
            'zone': 'Kirkos',
            'woreda': '01',
            'kebele': '05',
            'phone': '+251114789001',
            'alt_phone': '+251911345678',
            'email': 'kirkos.police@addisababa.gov.et',
            'address': 'Mexico Square, Kirkos, Addis Ababa',
            'latitude': 9.0125,
            'longitude': 38.7425,
            'hours_of_operation': '24/7',
            'services': 'Emergency services, patrol, community policing',
            'verified': True,
        },
        {
            'name': 'Yeka Police Station',
            'type': 'police',
            'description': 'Police station serving Yeka sub-city and residential areas.',
            'region': 'Addis Ababa',
            'zone': 'Yeka',
            'woreda': '04',
            'kebele': '03',
            'phone': '+251114567001',
            'alt_phone': '+251911456789',
            'email': 'yeka.police@addisababa.gov.et',
            'address': 'Yeka, near CMC Hospital, Addis Ababa',
            'latitude': 9.0456,
            'longitude': 38.8123,
            'hours_of_operation': '24/7',
            'services': 'Community policing, emergency response, traffic management',
            'verified': True,
        },
        {
            'name': 'Lideta Police Station',
            'type': 'police',
            'description': 'Police station covering Lideta sub-city including university area.',
            'region': 'Addis Ababa',
            'zone': 'Lideta',
            'woreda': '06',
            'kebele': '04',
            'phone': '+251114321001',
            'alt_phone': '+251911567890',
            'email': 'lideta.police@addisababa.gov.et',
            'address': 'Arat Kilo, near AAU, Addis Ababa',
            'latitude': 9.0389,
            'longitude': 38.7589,
            'hours_of_operation': '24/7',
            'services': 'Campus security, emergency response, crime prevention',
            'verified': True,
        },
        
        # Hospitals
        {
            'name': 'Black Lion Hospital',
            'type': 'hospital',
            'description': 'Major referral hospital with comprehensive emergency services.',
            'region': 'Addis Ababa',
            'zone': 'Lideta',
            'woreda': '07',
            'kebele': '02',
            'phone': '+251115517011',
            'alt_phone': '+251911456789',
            'email': 'emergency@blacklion.gov.et',
            'address': 'Arat Kilo, near Addis Ababa University, Addis Ababa',
            'latitude': 9.0417,
            'longitude': 38.7612,
            'hours_of_operation': '24/7 Emergency, 8:00-17:00 Regular services',
            'services': 'Emergency medicine, surgery, trauma care, obstetrics, pediatrics',
            'verified': True,
        },
        {
            'name': 'St. Paul Hospital',
            'type': 'hospital',
            'description': 'Specialized hospital with excellent emergency and maternity services.',
            'region': 'Addis Ababa',
            'zone': 'Gulele',
            'woreda': '09',
            'kebele': '04',
            'phone': '+251115533666',
            'alt_phone': '+251911567890',
            'email': 'info@stpaul.gov.et',
            'address': 'Gulele, near Entoto Road, Addis Ababa',
            'latitude': 9.0736,
            'longitude': 38.7599,
            'hours_of_operation': '24/7 Emergency, 8:00-16:30 Regular services',
            'services': 'Emergency care, maternity, surgery, internal medicine',
            'verified': True,
        },
        {
            'name': 'Zewditu Memorial Hospital',
            'type': 'hospital',
            'description': 'Public hospital providing comprehensive medical services.',
            'region': 'Addis Ababa',
            'zone': 'Arada',
            'woreda': '01',
            'kebele': '03',
            'phone': '+251115513355',
            'alt_phone': '+251911678901',
            'email': 'info@zewditu.gov.et',
            'address': 'Arada, near Red Cross, Addis Ababa',
            'latitude': 9.0298,
            'longitude': 38.7478,
            'hours_of_operation': '24/7 Emergency, 8:00-17:00 Outpatient',
            'services': 'General medicine, emergency care, laboratory, radiology',
            'verified': True,
        },
        {
            'name': 'ALERT Hospital',
            'type': 'hospital',
            'description': 'Specialized hospital for dermatology and general medical services.',
            'region': 'Addis Ababa',
            'zone': 'Arada',
            'woreda': '08',
            'kebele': '06',
            'phone': '+251115512233',
            'alt_phone': '+251911789012',
            'email': 'emergency@alert.gov.et',
            'address': 'Arada, near Piazza, Addis Ababa',
            'latitude': 9.0334,
            'longitude': 38.7467,
            'hours_of_operation': '24/7 Emergency, 8:00-17:00 Outpatient',
            'services': 'Emergency medicine, dermatology, general medicine, surgery',
            'verified': True,
        },
        {
            'name': 'Yekatit 12 Hospital',
            'type': 'hospital',
            'description': 'Historic hospital providing comprehensive medical care.',
            'region': 'Addis Ababa',
            'zone': 'Gulele',
            'woreda': '05',
            'kebele': '08',
            'phone': '+251115544777',
            'alt_phone': '+251911890123',
            'email': 'info@yekatit12.gov.et',
            'address': 'Gulele, near Megenagna, Addis Ababa',
            'latitude': 9.0567,
            'longitude': 38.7845,
            'hours_of_operation': '24/7 Emergency, 8:00-17:00 Regular',
            'services': 'Emergency care, internal medicine, surgery, pediatrics',
            'verified': True,
        },
        
        # NGO/Support Organizations
        {
            'name': 'Ethiopian Women Lawyers Association',
            'type': 'ngo',
            'description': 'Legal aid and support for women facing gender-based violence.',
            'region': 'Addis Ababa',
            'zone': 'Bole',
            'woreda': '05',
            'kebele': '08',
            'phone': '+251115505050',
            'alt_phone': '+251911789012',
            'email': 'info@ewla.org.et',
            'address': 'Bole Sub-city, Atlas Hotel Area, Addis Ababa',
            'latitude': 8.9978,
            'longitude': 38.7854,
            'hours_of_operation': 'Mon-Fri 8:30-17:30, Emergency hotline 24/7',
            'services': 'Legal aid, counseling, advocacy, shelter referrals, court support',
            'verified': True,
        },
        {
            'name': 'Association for Women in Development',
            'type': 'ngo',
            'description': 'Support services for women and children in crisis situations.',
            'region': 'Addis Ababa',
            'zone': 'Kirkos',
            'woreda': '03',
            'kebele': '07',
            'phone': '+251115454545',
            'alt_phone': '+251911890123',
            'email': 'support@awid.org.et',
            'address': 'Kirkos, near Stadium, Addis Ababa',
            'latitude': 9.0089,
            'longitude': 38.7398,
            'hours_of_operation': 'Mon-Fri 8:00-17:00, Hotline 24/7',
            'services': 'Psychosocial support, economic empowerment, emergency assistance',
            'verified': True,
        },
        {
            'name': 'Network of Ethiopian Women Associations',
            'type': 'ngo',
            'description': 'Umbrella organization coordinating women support services.',
            'region': 'Addis Ababa',
            'zone': 'Bole',
            'woreda': '02',
            'kebele': '05',
            'phone': '+251115757575',
            'alt_phone': '+251912012345',
            'email': 'info@newa.org.et',
            'address': 'Bole, near Airport Road, Addis Ababa',
            'latitude': 8.9845,
            'longitude': 38.7923,
            'hours_of_operation': 'Mon-Fri 8:30-17:30',
            'services': 'Coordination, advocacy, capacity building, referral services',
            'verified': True,
        },
        {
            'name': 'Marta Rehabilitation Center',
            'type': 'ngo',
            'description': 'Rehabilitation and support center for women in difficult situations.',
            'region': 'Addis Ababa',
            'zone': 'Kolfe Keranio',
            'woreda': '07',
            'kebele': '04',
            'phone': '+251115656565',
            'alt_phone': '+251912123456',
            'email': 'help@marta.org.et',
            'address': 'Kolfe, near Kotebe, Addis Ababa',
            'latitude': 8.9234,
            'longitude': 38.7234,
            'hours_of_operation': '24/7 Crisis intervention, 8:00-17:00 Services',
            'services': 'Crisis intervention, rehabilitation, skills training, counseling',
            'verified': True,
        },
        {
            'name': 'Children and Women Support Organization',
            'type': 'ngo',
            'description': 'Support services specifically for children and women protection.',
            'region': 'Addis Ababa',
            'zone': 'Akaky Kaliti',
            'woreda': '03',
            'kebele': '02',
            'phone': '+251115858585',
            'alt_phone': '+251912234567',
            'email': 'support@cwso.org.et',
            'address': 'Akaky Kaliti, near Ring Road, Addis Ababa',
            'latitude': 8.9123,
            'longitude': 38.7567,
            'hours_of_operation': 'Mon-Fri 8:00-17:00, Emergency 24/7',
            'services': 'Child protection, family mediation, emergency assistance, training',
            'verified': True,
        },
        
        # Government Offices
        {
            'name': 'Women and Children Affairs Bureau',
            'type': 'government',
            'description': 'Government office handling women and children protection cases.',
            'region': 'Addis Ababa',
            'zone': 'Addis Ketema',
            'woreda': '05',
            'kebele': '02',
            'phone': '+251115252525',
            'alt_phone': '+251911901234',
            'email': 'info@wcab.addis.gov.et',
            'address': 'Addis Ketema, near City Hall, Addis Ababa',
            'latitude': 9.0245,
            'longitude': 38.7523,
            'hours_of_operation': 'Mon-Fri 8:30-17:30',
            'services': 'Child protection, women affairs, family mediation, legal support',
            'verified': True,
        },
        {
            'name': 'Justice Office - Legal Aid Department',
            'type': 'government',
            'description': 'Government legal aid services for vulnerable populations.',
            'region': 'Addis Ababa',
            'zone': 'Lideta',
            'woreda': '03',
            'kebele': '01',
            'phone': '+251115353535',
            'alt_phone': '+251912012345',
            'email': 'legalaid@justice.gov.et',
            'address': 'Lideta, near Federal Court, Addis Ababa',
            'latitude': 9.0423,
            'longitude': 38.7634,
            'hours_of_operation': 'Mon-Fri 8:30-17:30',
            'services': 'Legal aid, court representation, legal advice, mediation',
            'verified': True,
        },
        
        # Shelters
        {
            'name': 'Safe Haven Women Shelter',
            'type': 'shelter',
            'description': 'Emergency shelter and rehabilitation center for women in crisis.',
            'region': 'Addis Ababa',
            'zone': 'Nifas Silk',
            'woreda': '02',
            'kebele': '06',
            'phone': '+251115606060',
            'alt_phone': '+251912012345',
            'email': 'intake@safehaven.org.et',
            'address': 'Nifas Silk, Confidential Location, Addis Ababa',
            'latitude': 8.9567,
            'longitude': 38.7234,
            'hours_of_operation': '24/7 Admission, Support services 8:00-18:00',
            'services': 'Emergency shelter, counseling, legal aid, skills training, childcare',
            'verified': True,
        },
        {
            'name': 'Bethany House',
            'type': 'shelter',
            'description': 'Temporary accommodation and support for women and children.',
            'region': 'Addis Ababa',
            'zone': 'Gulele',
            'woreda': '06',
            'kebele': '09',
            'phone': '+251115707070',
            'alt_phone': '+251912123456',
            'email': 'admissions@bethanyhouse.org.et',
            'address': 'Gulele, Confidential Location, Addis Ababa',
            'latitude': 9.0678,
            'longitude': 38.7890,
            'hours_of_operation': '24/7 Emergency admission, 8:00-18:00 Services',
            'services': 'Temporary shelter, psychosocial support, job training, family reunification',
            'verified': True,
        },
    ]

    agencies = []
    for agency_data in agencies_data:
        agency = Agency.objects.create(**agency_data)
        agencies.append(agency)

    print(f"✓ Created {len(agencies)} agencies")
    return agencies


def create_reports(users):
    """Create sample incident reports"""
    print("Creating incident reports...")
    
    incident_types = ['rape', 'assault', 'domestic_violence', 'harassment', 'other']
    status_choices = ['submitted', 'processing', 'resolved', 'closed']
    
    descriptions = {
        'rape': [
            'Incident occurred late at night while walking home from work',
            'Attacked by unknown person in isolated area near market',
            'Need immediate medical and legal assistance urgently',
            'Incident reported to seek justice and support services',
            'Seeking help and counseling services for recovery'
        ],
        'assault': [
            'Physical attack by known individual during argument',
            'Unprovoked assault in public place near bus station',
            'Sustained injuries requiring immediate medical attention',
            'Witnessed assault on another person in neighborhood',
            'Group attack in residential area during evening'
        ],
        'domestic_violence': [
            'Ongoing physical abuse at home by family member',
            'Escalating violence by intimate partner over months',
            'Pattern of intimidation and threats against children',
            'Multiple instances of violence requiring intervention',
            'Need immediate safe accommodation away from abuser'
        ],
        'harassment': [
            'Persistent unwanted contact and threatening messages',
            'Workplace harassment by supervisor affecting work',
            'Street harassment while commuting to office daily',
            'Online harassment and threats via social media',
            'Stalking behavior causing fear for personal safety'
        ],
        'other': [
            'Suspicious activity in neighborhood affecting safety',
            'Feeling unsafe due to recent incidents in area',
            'Witnessed crime but afraid to report elsewhere',
            'Need information about available safety resources',
            'General safety concerns for family members'
        ]
    }

    reports = []
    for i in range(15):  # Create 15 reports
        user = random.choice(users)
        incident_type = random.choice(incident_types)
        description = random.choice(descriptions[incident_type])
        
        # Generate location near user's location if they have one
        if user.latitude and user.longitude:
            lat_offset = random.uniform(-0.02, 0.02)
            lng_offset = random.uniform(-0.02, 0.02)
            latitude = user.latitude + lat_offset
            longitude = user.longitude + lng_offset
            location = f"GPS: {latitude:.6f}, {longitude:.6f}"
        else:
            # Default Addis Ababa coordinates with variation
            latitude = 9.0054 + random.uniform(-0.08, 0.08)
            longitude = 38.7636 + random.uniform(-0.08, 0.08)
            location = f"GPS: {latitude:.6f}, {longitude:.6f}"

        # Create report with some submitted in the past
        submitted_at = timezone.now() - timedelta(days=random.randint(0, 45))
        
        report = IncidentReport.objects.create(
            user=user,
            type=incident_type,
            description=description,
            location=location,
            latitude=latitude,
            longitude=longitude,
            status=random.choice(status_choices),
            submitted_at=submitted_at,
            ip_address=f"192.168.{random.randint(1, 10)}.{random.randint(1, 255)}",
            device_info=random.choice([
                'Telegram/Android 12',
                'Telegram/iOS 16.2',
                'Telegram/Android 11',
                'Telegram/iOS 15.5',
                'Telegram/Android 13',
                'Telegram/iOS 17.0'
            ])
        )
        reports.append(report)

    print(f"✓ Created {len(reports)} incident reports")
    return reports


def create_notifications(users, reports, agencies):
    """Create sample notifications"""
    print("Creating notifications...")
    
    notification_types = ['report_status', 'nearby_agency', 'system', 'safety_tip']
    priorities = ['low', 'medium', 'high', 'urgent']
    
    notification_data = {
        'report_status': [
            ('Report Received', 'Your incident report has been received and assigned ID #{report_id}. We will review it shortly.'),
            ('Report Under Review', 'Your report is currently being reviewed by our specialized team for appropriate action.'),
            ('Additional Information Needed', 'Please provide additional details for your report to help us assist you better.'),
            ('Support Services Contacted', 'We have contacted appropriate support services on your behalf.'),
            ('Report Updated', 'Your incident report status has been updated. Please check for details.'),
        ],
        'nearby_agency': [
            ('Emergency Services Nearby', 'A police station is located 0.5km from your current location and available 24/7.'),
            ('Hospital Alert', 'Black Lion Hospital emergency services are the nearest medical facility to you.'),
            ('Support Center Available', 'Women support services are available within 1km of your area with counseling.'),
            ('Legal Aid Office', 'Legal assistance is available at nearby women lawyers association during business hours.'),
            ('Shelter Information', 'Emergency shelter services are available in your area with immediate admission.'),
        ],
        'system': [
            ('System Maintenance', 'The system will undergo maintenance tonight from 2-4 AM for improvements.'),
            ('New Feature Available', 'Voice recording feature is now available for incident reports.'),
            ('Language Support Added', 'The app now supports Afaan Oromo language interface.'),
            ('Privacy Update', 'Our privacy policy has been updated to better protect your personal data.'),
            ('Security Enhancement', 'New security measures have been implemented for your protection and privacy.'),
        ],
        'safety_tip': [
            ('Personal Safety Tip', 'Always inform someone you trust about your whereabouts when going out alone.'),
            ('Digital Safety', 'Keep your personal information private on social media platforms and apps.'),
            ('Emergency Contacts', 'Keep emergency contact numbers easily accessible on your phone at all times.'),
            ('Safe Transportation', 'Use reliable transportation options and avoid traveling alone at night.'),
            ('Home Security', 'Ensure your doors and windows are properly secured when at home.'),
        ]
    }

    notifications = []
    for i in range(25):  # Create 25 notifications
        user = random.choice(users)
        notification_type = random.choice(notification_types)
        title, message_template = random.choice(notification_data[notification_type])
        
        # Customize message based on type
        if notification_type == 'report_status' and reports:
            user_reports = [r for r in reports if r.user == user]
            if user_reports:
                related_report = random.choice(user_reports)
            else:
                related_report = random.choice(reports)
            message = message_template.format(report_id=str(related_report.id)[:8])
        else:
            related_report = None
            message = message_template

        # Randomly assign related agency for nearby_agency notifications
        related_agency = None
        if notification_type == 'nearby_agency':
            related_agency = random.choice(agencies)

        # Create notification with some in the past
        created_at = timezone.now() - timedelta(hours=random.randint(0, 168))  # Up to 1 week ago
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=random.choice(priorities),
            related_report=related_report,
            related_agency=related_agency,
            is_read=random.choice([True, False, False]),  # Bias towards unread
            is_sent=True,
            created_at=created_at
        )
        
        # Mark as read for some notifications with realistic timing
        if notification.is_read:
            notification.read_at = created_at + timedelta(minutes=random.randint(5, 1440))  # 5 min to 1 day
            notification.save(update_fields=['read_at'])

        notifications.append(notification)

    print(f"✓ Created {len(notifications)} notifications")
    return notifications


def create_notification_channels(users):
    """Create notification channels for users"""
    print("Creating notification channels...")
    
    channels = []
    for user in users:
        # Create telegram channel for all users
        telegram_channel = NotificationChannel.objects.create(
            user=user,
            channel_type='telegram',
            is_enabled=True,
            telegram_chat_id=user.telegram_id
        )
        channels.append(telegram_channel)
        
        # Create websocket channel for most users
        if random.choice([True, True, False]):  # 2/3 probability
            websocket_channel = NotificationChannel.objects.create(
                user=user,
                channel_type='websocket',
                is_enabled=True
            )
            channels.append(websocket_channel)
        
        # Create email channel for some users
        if random.choice([True, False]):  # 1/2 probability
            email_channel = NotificationChannel.objects.create(
                user=user,
                channel_type='email',
                is_enabled=random.choice([True, False]),
                email_address=f"user{user.telegram_id}@example.com"
            )
            channels.append(email_channel)

    print(f"✓ Created {len(channels)} notification channels")
    return channels


def main():
    """Main execution function"""
    print("🚀 Starting database population...")
    print("=" * 50)
    
    # Option to clear data
    import sys
    if '--clear' in sys.argv:
        clear_data()
        print()
    
    try:
        with transaction.atomic():
            # Create all data
            users = create_users()
            agencies = create_agencies()
            reports = create_reports(users)
            notifications = create_notifications(users, reports, agencies)
            channels = create_notification_channels(users)
            
            print("=" * 50)
            print("✅ Database population completed successfully!")
            print(f"📊 Summary:")
            print(f"   • {len(users)} User Profiles")
            print(f"   • {len(agencies)} Agencies")
            print(f"   • {len(reports)} Incident Reports")
            print(f"   • {len(notifications)} Notifications")
            print(f"   • {len(channels)} Notification Channels")
            print()
            print("🎯 The database is now ready for testing!")
            
    except Exception as e:
        print(f"❌ Error during database population: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)