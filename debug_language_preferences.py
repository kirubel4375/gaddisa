#!/usr/bin/env python3
"""
Language Preference Debug Utility
=================================

This script provides comprehensive debugging and testing capabilities for the
Emergency Bot language preference system. It can be used to:

1. Test language operations in isolation
2. Verify database operations
3. Generate debug reports
4. Simulate user language changes
5. Check system health

Usage:
    python debug_language_preferences.py --help
    python debug_language_preferences.py --test-user 123456 --language am
    python debug_language_preferences.py --health-check
    python debug_language_preferences.py --generate-report
"""

import os
import sys
import django
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

# Import after Django setup
from emergency_bot.accounts.models import UserProfile
from emergency_bot.utils.translations import get_user_language, update_user_language, get_text
from language_debug_logging import setup_language_logging, get_language_logger, create_debug_summary

# Setup logging
setup_language_logging()
logger = get_language_logger(__name__)

class LanguageDebugger:
    """Main class for language preference debugging"""
    
    def __init__(self):
        self.valid_languages = ['en', 'am', 'om']
        self.language_names = {
            'en': 'English',
            'am': 'Amharic',
            'om': 'Afaan Oromo'
        }
        logger.info("Language Debugger initialized")
    
    def test_user_language_operations(self, user_id, target_language=None):
        """Test all language operations for a specific user"""
        logger.info(f"Testing language operations for user {user_id}")
        
        results = {
            'user_id': user_id,
            'timestamp': datetime.now(),
            'tests': {}
        }
        
        # Test 1: Get current language
        try:
            current_lang = get_user_language(user_id)
            results['tests']['get_language'] = {
                'success': True,
                'result': current_lang,
                'error': None
            }
            logger.info(f"Current language for user {user_id}: {current_lang}")
        except Exception as e:
            results['tests']['get_language'] = {
                'success': False,
                'result': None,
                'error': str(e)
            }
            logger.error(f"Failed to get language for user {user_id}: {e}")
        
        # Test 2: Update language (if target specified)
        if target_language:
            if target_language not in self.valid_languages:
                logger.error(f"Invalid target language: {target_language}")
                results['tests']['update_language'] = {
                    'success': False,
                    'result': None,
                    'error': f"Invalid language: {target_language}"
                }
            else:
                try:
                    success = update_user_language(user_id, target_language)
                    results['tests']['update_language'] = {
                        'success': success,
                        'result': target_language if success else None,
                        'error': None if success else "Update returned False"
                    }
                    
                    if success:
                        logger.info(f"Successfully updated language to {target_language} for user {user_id}")
                        
                        # Test 3: Verify update
                        try:
                            new_lang = get_user_language(user_id)
                            verification_success = (new_lang == target_language)
                            results['tests']['verify_update'] = {
                                'success': verification_success,
                                'result': new_lang,
                                'error': None if verification_success else f"Expected {target_language}, got {new_lang}"
                            }
                            
                            if verification_success:
                                logger.info(f"Verified: Language successfully changed to {new_lang}")
                            else:
                                logger.error(f"Verification failed: Expected {target_language}, got {new_lang}")
                                
                        except Exception as e:
                            results['tests']['verify_update'] = {
                                'success': False,
                                'result': None,
                                'error': str(e)
                            }
                            logger.error(f"Failed to verify language update: {e}")
                    else:
                        logger.error(f"Failed to update language to {target_language} for user {user_id}")
                        
                except Exception as e:
                    results['tests']['update_language'] = {
                        'success': False,
                        'result': None,
                        'error': str(e)
                    }
                    logger.error(f"Exception during language update: {e}")
        
        # Test 4: Test translation functionality
        try:
            current_lang = results['tests']['get_language']['result'] or 'en'
            test_text = get_text('welcome_message', current_lang)
            results['tests']['translation'] = {
                'success': bool(test_text),
                'result': test_text[:50] + "..." if len(test_text) > 50 else test_text,
                'error': None if test_text else "No translation found"
            }
            logger.info(f"Translation test successful for language {current_lang}")
        except Exception as e:
            results['tests']['translation'] = {
                'success': False,
                'result': None,
                'error': str(e)
            }
            logger.error(f"Translation test failed: {e}")
        
        return results
    
    def check_database_health(self):
        """Check database health and user profile integrity"""
        logger.info("Checking database health")
        
        health_report = {
            'timestamp': datetime.now(),
            'database_accessible': False,
            'user_count': 0,
            'language_distribution': {},
            'issues': []
        }
        
        try:
            # Test database connection
            user_count = UserProfile.objects.count()
            health_report['database_accessible'] = True
            health_report['user_count'] = user_count
            logger.info(f"Database accessible. Total users: {user_count}")
            
            # Check language distribution
            for lang_code in self.valid_languages:
                count = UserProfile.objects.filter(language=lang_code).count()
                health_report['language_distribution'][lang_code] = count
                logger.info(f"Users with language {lang_code}: {count}")
            
            # Check for users with invalid languages
            invalid_lang_users = UserProfile.objects.exclude(language__in=self.valid_languages)
            if invalid_lang_users.exists():
                invalid_count = invalid_lang_users.count()
                health_report['issues'].append(f"Found {invalid_count} users with invalid language codes")
                logger.warning(f"Found {invalid_count} users with invalid language codes")
                
                # Show first 5 examples
                for user in invalid_lang_users[:5]:
                    health_report['issues'].append(f"User {user.telegram_id} has invalid language: {user.language}")
                    logger.warning(f"User {user.telegram_id} has invalid language: {user.language}")
            
            # Check for users without consent
            no_consent_users = UserProfile.objects.filter(data_consent=False)
            if no_consent_users.exists():
                no_consent_count = no_consent_users.count()
                health_report['issues'].append(f"Found {no_consent_count} users without data consent")
                logger.info(f"Found {no_consent_count} users without data consent")
            
        except Exception as e:
            health_report['issues'].append(f"Database error: {str(e)}")
            logger.error(f"Database health check failed: {e}")
        
        return health_report
    
    def simulate_language_changes(self, user_id):
        """Simulate multiple language changes to test system robustness"""
        logger.info(f"Simulating language changes for user {user_id}")
        
        simulation_results = {
            'user_id': user_id,
            'timestamp': datetime.now(),
            'changes': [],
            'success_rate': 0.0,
            'issues': []
        }
        
        # Get initial language
        try:
            initial_language = get_user_language(user_id)
            logger.info(f"Initial language for user {user_id}: {initial_language}")
        except Exception as e:
            simulation_results['issues'].append(f"Failed to get initial language: {e}")
            logger.error(f"Failed to get initial language: {e}")
            return simulation_results
        
        # Test each language change
        test_sequence = ['en', 'am', 'om', 'en']  # Full cycle
        successful_changes = 0
        
        for target_lang in test_sequence:
            change_result = {
                'target_language': target_lang,
                'success': False,
                'error': None,
                'timestamp': datetime.now()
            }
            
            try:
                success = update_user_language(user_id, target_lang)
                if success:
                    # Verify the change
                    actual_lang = get_user_language(user_id)
                    if actual_lang == target_lang:
                        change_result['success'] = True
                        successful_changes += 1
                        logger.info(f"Successfully changed language to {target_lang}")
                    else:
                        change_result['error'] = f"Expected {target_lang}, got {actual_lang}"
                        logger.error(f"Language change verification failed: {change_result['error']}")
                else:
                    change_result['error'] = "update_user_language returned False"
                    logger.error(f"Language change failed: {change_result['error']}")
                    
            except Exception as e:
                change_result['error'] = str(e)
                logger.error(f"Exception during language change to {target_lang}: {e}")
            
            simulation_results['changes'].append(change_result)
        
        # Calculate success rate
        simulation_results['success_rate'] = successful_changes / len(test_sequence) * 100
        logger.info(f"Language change simulation completed. Success rate: {simulation_results['success_rate']:.1f}%")
        
        return simulation_results
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive system health and debug report"""
        logger.info("Generating comprehensive language system report")
        
        report = {
            'timestamp': datetime.now(),
            'system_info': {},
            'database_health': {},
            'test_results': {},
            'recommendations': []
        }
        
        # System information
        report['system_info'] = {
            'python_version': sys.version,
            'django_version': django.VERSION,
            'valid_languages': self.valid_languages,
            'language_names': self.language_names
        }
        
        # Database health check
        report['database_health'] = self.check_database_health()
        
        # Test with a sample user (create if needed)
        test_user_id = "debug_test_user_999999"
        logger.info(f"Running tests with test user: {test_user_id}")
        
        # Clean up test user first
        try:
            UserProfile.objects.filter(telegram_id=test_user_id).delete()
            logger.debug(f"Cleaned up existing test user {test_user_id}")
        except:
            pass
        
        # Run tests
        report['test_results']['basic_operations'] = self.test_user_language_operations(test_user_id, 'am')
        report['test_results']['language_simulation'] = self.simulate_language_changes(test_user_id)
        
        # Clean up test user
        try:
            UserProfile.objects.filter(telegram_id=test_user_id).delete()
            logger.debug(f"Cleaned up test user {test_user_id}")
        except:
            pass
        
        # Generate recommendations
        if report['database_health']['issues']:
            report['recommendations'].append("Database issues detected - see health check details")
        
        if report['test_results']['basic_operations']['tests'].get('update_language', {}).get('success') == False:
            report['recommendations'].append("Language update operations are failing - check database connectivity and permissions")
        
        success_rate = report['test_results']['language_simulation']['success_rate']
        if success_rate < 100:
            report['recommendations'].append(f"Language change success rate is {success_rate:.1f}% - investigate failed operations")
        
        if not report['recommendations']:
            report['recommendations'].append("All tests passed - language system appears to be functioning correctly")
        
        logger.info("Comprehensive report generation completed")
        return report
    
    def print_report(self, report, detailed=False):
        """Print a formatted report to console"""
        print("\n" + "="*80)
        print("LANGUAGE PREFERENCE DEBUG REPORT")
        print("="*80)
        print(f"Generated: {report['timestamp']}")
        print()
        
        if 'database_health' in report:
            health = report['database_health']
            print("DATABASE HEALTH:")
            print(f"  Accessible: {health['database_accessible']}")
            print(f"  Total Users: {health['user_count']}")
            print("  Language Distribution:")
            for lang, count in health.get('language_distribution', {}).items():
                lang_name = self.language_names.get(lang, lang)
                print(f"    {lang_name} ({lang}): {count} users")
            
            if health.get('issues'):
                print("  Issues:")
                for issue in health['issues']:
                    print(f"    - {issue}")
            print()
        
        if 'test_results' in report:
            print("TEST RESULTS:")
            
            # Basic operations
            if 'basic_operations' in report['test_results']:
                basic = report['test_results']['basic_operations']
                print(f"  Basic Operations (User {basic['user_id']}):")
                for test_name, result in basic['tests'].items():
                    status = "✓ PASS" if result['success'] else "✗ FAIL"
                    print(f"    {test_name}: {status}")
                    if not result['success'] and result['error']:
                        print(f"      Error: {result['error']}")
                    elif result['result']:
                        print(f"      Result: {result['result']}")
            
            # Language simulation
            if 'language_simulation' in report['test_results']:
                sim = report['test_results']['language_simulation']
                print(f"  Language Change Simulation (User {sim['user_id']}):")
                print(f"    Success Rate: {sim['success_rate']:.1f}%")
                if detailed:
                    for change in sim['changes']:
                        status = "✓" if change['success'] else "✗"
                        print(f"    {status} Change to {change['target_language']}")
                        if change['error']:
                            print(f"      Error: {change['error']}")
            print()
        
        if 'recommendations' in report:
            print("RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
            print()
        
        print("="*80)
        print("For detailed logs, check the files in the 'logs/' directory")
        print("="*80)

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Debug and test the Emergency Bot language preference system"
    )
    
    parser.add_argument(
        '--test-user',
        type=str,
        help="Test language operations for a specific user ID"
    )
    
    parser.add_argument(
        '--language',
        type=str,
        choices=['en', 'am', 'om'],
        help="Target language for user test (requires --test-user)"
    )
    
    parser.add_argument(
        '--health-check',
        action='store_true',
        help="Run database health check"
    )
    
    parser.add_argument(
        '--simulate',
        type=str,
        help="Simulate language changes for a specific user ID"
    )
    
    parser.add_argument(
        '--generate-report',
        action='store_true',
        help="Generate comprehensive system report"
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help="Show detailed output for reports"
    )
    
    parser.add_argument(
        '--log-summary',
        action='store_true',
        help="Show summary of recent log entries"
    )
    
    args = parser.parse_args()
    
    debugger = LanguageDebugger()
    
    # Show log summary if requested
    if args.log_summary:
        print("\n" + "="*60)
        print("RECENT LOG SUMMARY")
        print("="*60)
        print(create_debug_summary())
        return
    
    # Test specific user
    if args.test_user:
        print(f"\nTesting language operations for user: {args.test_user}")
        results = debugger.test_user_language_operations(args.test_user, args.language)
        debugger.print_report({'test_results': {'basic_operations': results}}, args.detailed)
        return
    
    # Health check
    if args.health_check:
        print("\nRunning database health check...")
        health = debugger.check_database_health()
        debugger.print_report({'database_health': health}, args.detailed)
        return
    
    # Simulate language changes
    if args.simulate:
        print(f"\nSimulating language changes for user: {args.simulate}")
        results = debugger.simulate_language_changes(args.simulate)
        debugger.print_report({'test_results': {'language_simulation': results}}, args.detailed)
        return
    
    # Generate comprehensive report
    if args.generate_report:
        print("\nGenerating comprehensive system report...")
        report = debugger.generate_comprehensive_report()
        debugger.print_report(report, args.detailed)
        return
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    main()