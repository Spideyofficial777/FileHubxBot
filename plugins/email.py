# Don't Remove Credit @hacker_x_official_777
# Ask Doubt on telegram @hacker_x_official_777
#
# Copyright (C) 2025 by Hacker X Official, < https://t.me/hacker_x_official_777 >.
#
# Enhanced Email Notification System with Robust Error Handling
#

import smtplib
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Tuple
import re
import time
import random
from database.db_email import EmailDatabase
from config import *

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedSpideyEmailSystem:
    def __init__(self):
        self.db = EmailDatabase()
        self.smtp_config = self._get_smtp_config()
        self.is_connected = False
        self.smtp_connection = None
        self.test_results = {}
        self.connection_attempts = 0
        self.max_retries = SMTP_RETRY_ATTEMPTS
        self.current_smtp_index = 0
        
    def _get_smtp_config(self) -> Dict:
        """Get SMTP configuration with fallback options"""
        primary_config = {
            'server': SMTP_SERVER,
            'port': SMTP_PORT,
            'username': SMTP_USERNAME,
            'password': SMTP_PASSWORD,
            'from_email': FROM_EMAIL,
            'from_name': FROM_NAME,
            'admin_email': ADMIN_EMAIL,
            'use_tls': SMTP_USE_TLS,
            'use_ssl': SMTP_USE_SSL,
            'timeout': SMTP_TIMEOUT
        }
        
        # Add backup servers
        primary_config['backup_servers'] = BACKUP_SMTP_SERVERS
        return primary_config

    async def connect_smtp(self, use_backup: bool = False) -> Tuple[bool, str]:
        """Enhanced SMTP connection with robust error handling and backup servers"""
        try:
            if use_backup and self.current_smtp_index > 0:
                backup_server = self.smtp_config['backup_servers'][self.current_smtp_index - 1]
                server = backup_server['server']
                port = backup_server['port']
                server_type = "Backup"
            else:
                server = self.smtp_config['server']
                port = self.smtp_config['port']
                server_type = "Primary"

            logger.info(f"🔗 Attempting to connect to {server_type} SMTP: {server}:{port}")

            # Enhanced connection parameters
            connection_params = {
                'hostname': server,
                'port': port,
                'timeout': self.smtp_config['timeout'],
                'use_tls': self.smtp_config['use_tls']
            }

            # Handle SSL connection
            if self.smtp_config['use_ssl']:
                connection_params['use_tls'] = False
                connection_params['start_tls'] = False

            self.smtp_connection = aiosmtplib.SMTP(**connection_params)
            
            # Connect with retry logic
            await self.smtp_connection.connect()
            logger.info(f"✅ SMTP connection established to {server}")

            # Login with credentials
            await self.smtp_connection.login(
                self.smtp_config['username'],
                self.smtp_config['password']
            )
            logger.info("✅ SMTP login successful")
            
            self.is_connected = True
            self.connection_attempts = 0
            return True, f"Connected to {server_type} server: {server}"

        except aiosmtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ SMTP Authentication failed: {e}"
            logger.error(error_msg)
            return False, error_msg

        except aiosmtplib.SMTPConnectError as e:
            error_msg = f"❌ SMTP Connection failed: {e}"
            logger.error(error_msg)
            
            # Try backup servers
            if not use_backup and self.smtp_config['backup_servers']:
                return await self._try_backup_servers()
            
            return False, error_msg

        except Exception as e:
            error_msg = f"❌ Unexpected SMTP error: {e}"
            logger.error(error_msg)
            return False, error_msg

    async def _try_backup_servers(self) -> Tuple[bool, str]:
        """Try connecting to backup SMTP servers"""
        for i, backup_server in enumerate(self.smtp_config['backup_servers']):
            self.current_smtp_index = i + 1
            logger.info(f"🔄 Trying backup server {i+1}: {backup_server['server']}")
            
            success, message = await self.connect_smtp(use_backup=True)
            if success:
                return True, f"Connected to backup server {i+1}: {backup_server['server']}"
            
            await asyncio.sleep(SMTP_RETRY_DELAY)  # Wait before trying next server
        
        return False, "All SMTP servers failed to connect"

    async def ensure_connection(self) -> bool:
        """Ensure we have a valid SMTP connection"""
        if self.is_connected and self.smtp_connection:
            try:
                # Test connection by sending NOOP command
                await self.smtp_connection.noop()
                return True
            except Exception:
                self.is_connected = False
                self.smtp_connection = None

        # Reconnect if needed
        if self.connection_attempts < self.max_retries:
            self.connection_attempts += 1
            success, message = await self.connect_smtp()
            if success:
                return True
            else:
                logger.warning(f"Connection attempt {self.connection_attempts} failed: {message}")
                await asyncio.sleep(SMTP_RETRY_DELAY)
                return await self.ensure_connection()  # Retry recursively
        
        logger.error("Max connection attempts reached")
        return False

    async def disconnect_smtp(self):
        """Safely disconnect from SMTP server"""
        if self.smtp_connection and self.is_connected:
            try:
                await self.smtp_connection.quit()
                self.is_connected = False
                logger.info("🔌 SMTP connection closed safely")
            except Exception as e:
                logger.error(f"Error disconnecting SMTP: {e}")
            finally:
                self.smtp_connection = None

    # Enhanced Email Validation
    def is_valid_email(self, email: str) -> bool:
        """Comprehensive email validation"""
        if not email or not isinstance(email, str):
            return False
        
        # Basic pattern matching
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False
        
        # Additional checks
        if len(email) > 254:  # RFC 5321 limit
            return False
        
        if email.count('@') != 1:
            return False
        
        return True

    # Enhanced Email Sending with Retry Logic
    async def send_email(self, to_email: str, subject: str, html_content: str, 
                        text_content: str = None, max_retries: int = 3) -> Dict:
        """Enhanced email sending with comprehensive error handling"""
        test_id = f"send_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"
        
        for attempt in range(max_retries):
            try:
                # Ensure connection
                if not await self.ensure_connection():
                    return {
                        'success': False,
                        'error': 'SMTP connection unavailable',
                        'test_id': test_id,
                        'attempt': attempt + 1
                    }

                # Create message
                message = MIMEMultipart('alternative')
                message['From'] = f"{self.smtp_config['from_name']} <{self.smtp_config['from_email']}>"
                message['To'] = to_email
                message['Subject'] = subject
                message['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
                message['Message-ID'] = f"<{test_id}@{self.smtp_config['server'].split('.')[0]}>"

                # Create text version if not provided
                if text_content is None:
                    # Simple HTML to text conversion
                    text_content = re.sub('<[^<]+?>', '', html_content)
                    text_content = re.sub('\n+', '\n', text_content).strip()
                
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                part2 = MIMEText(html_content, 'html', 'utf-8')
                
                message.attach(part1)
                message.attach(part2)

                # Send email
                logger.info(f"📤 Attempt {attempt + 1}: Sending email to {to_email}")
                
                await self.smtp_connection.send_message(message)
                
                logger.info(f"✅ Email sent successfully to {to_email} (Attempt {attempt + 1})")
                return {
                    'success': True,
                    'message': 'Email sent successfully',
                    'test_id': test_id,
                    'recipient': to_email,
                    'attempt': attempt + 1,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'server': self.smtp_config['server'] if self.current_smtp_index == 0 else 
                             f"Backup {self.current_smtp_index}: {self.smtp_config['backup_servers'][self.current_smtp_index-1]['server']}"
                }

            except aiosmtplib.SMTPRecipientsRefused as e:
                error_msg = f"❌ Recipient refused: {to_email}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': f'Recipient email refused: {to_email}',
                    'test_id': test_id,
                    'attempt': attempt + 1
                }

            except aiosmtplib.SMTPSenderRefused as e:
                error_msg = f"❌ Sender refused: {e}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': f'Sender authentication failed: {str(e)}',
                    'test_id': test_id,
                    'attempt': attempt + 1
                }

            except aiosmtplib.SMTPDataError as e:
                error_msg = f"❌ SMTP data error: {e}"
                logger.error(error_msg)
                if attempt < max_retries - 1:
                    await asyncio.sleep(SMTP_RETRY_DELAY)
                    continue
                return {
                    'success': False,
                    'error': f'SMTP data error: {str(e)}',
                    'test_id': test_id,
                    'attempt': attempt + 1
                }

            except Exception as e:
                error_msg = f"❌ Email sending failed (Attempt {attempt + 1}): {str(e)}"
                logger.error(error_msg)
                
                if attempt < max_retries - 1:
                    # Reset connection for retry
                    self.is_connected = False
                    self.smtp_connection = None
                    await asyncio.sleep(SMTP_RETRY_DELAY)
                    continue
                
                return {
                    'success': False,
                    'error': str(e),
                    'test_id': test_id,
                    'attempt': attempt + 1
                }

        return {
            'success': False,
            'error': f'All {max_retries} attempts failed',
            'test_id': test_id
        }

    # Enhanced Test Function
    async def test_email_service(self, user_id: int = None, user_email: str = None) -> Dict:
        """Comprehensive email service test with detailed reporting"""
        test_id = f"full_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_start = datetime.now()
        
        test_results = {
            'test_id': test_id,
            'timestamp': test_start.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': {},
            'configuration': {
                'smtp_server': self.smtp_config['server'],
                'smtp_port': self.smtp_config['port'],
                'from_email': self.smtp_config['from_email'],
                'admin_email': self.smtp_config['admin_email'],
                'backup_servers': len(self.smtp_config['backup_servers'])
            }
        }

        try:
            logger.info(f"🧪 Starting comprehensive email test: {test_id}")

            # Test 1: SMTP Connection
            logger.info("1️⃣ Testing SMTP connection...")
            connection_success, connection_msg = await self.connect_smtp()
            test_results['tests']['smtp_connection'] = {
                'success': connection_success,
                'message': connection_msg,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }

            if not connection_success:
                test_results['overall_success'] = False
                test_results['error'] = 'SMTP connection failed'
                test_results['duration'] = (datetime.now() - test_start).total_seconds()
                return test_results

            # Test 2: Admin Email Test
            logger.info("2️⃣ Testing admin email delivery...")
            admin_test_html = self._get_admin_test_template("Service Test", test_results['configuration'])
            admin_result = await self.send_email(
                self.smtp_config['admin_email'],
                "✅ Admin Test - FileHubX Bot Email System",
                admin_test_html,
                "Admin test email from FileHubX Bot"
            )
            test_results['tests']['admin_email'] = admin_result

            # Test 3: User Email Test (if provided)
            if user_email and self.is_valid_email(user_email):
                logger.info(f"3️⃣ Testing user email delivery: {user_email}")
                user_test_html = self._get_user_test_template("User Test")
                user_result = await self.send_email(
                    user_email,
                    "✅ Test Email - FileHubX Bot",
                    user_test_html,
                    "User test email from FileHubX Bot"
                )
                test_results['tests']['user_email'] = user_result
            else:
                test_results['tests']['user_email'] = {
                    'success': False,
                    'message': 'No valid user email provided'
                }

            # Test 4: Connection Stability
            logger.info("4️⃣ Testing connection stability...")
            stability_test = await self._test_connection_stability()
            test_results['tests']['connection_stability'] = stability_test

            # Calculate results
            successful_tests = sum(1 for test in test_results['tests'].values() if test.get('success', False))
            total_tests = len(test_results['tests'])
            
            test_results['overall_success'] = successful_tests == total_tests
            test_results['success_rate'] = f"{successful_tests}/{total_tests}"
            test_results['success_percentage'] = round((successful_tests / total_tests) * 100, 2)
            test_results['duration'] = round((datetime.now() - test_start).total_seconds(), 2)

            # Store results
            self.test_results[test_id] = test_results
            
            logger.info(f"📊 Test completed: {test_results['success_rate']} tests passed in {test_results['duration']}s")
            
            return test_results

        except Exception as e:
            error_msg = f"❌ Comprehensive test failed: {str(e)}"
            logger.error(error_msg)
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            test_results['duration'] = round((datetime.now() - test_start).total_seconds(), 2)
            return test_results

    async def _test_connection_stability(self) -> Dict:
        """Test SMTP connection stability"""
        try:
            start_time = time.time()
            tests_passed = 0
            total_tests = 3
            
            for i in range(total_tests):
                try:
                    await self.smtp_connection.noop()
                    tests_passed += 1
                    await asyncio.sleep(1)  # Wait between tests
                except Exception:
                    break
            
            stability = tests_passed / total_tests
            return {
                'success': stability >= 0.66,  # At least 2/3 tests pass
                'message': f'Stability: {tests_passed}/{total_tests} tests passed',
                'stability_score': round(stability * 100, 2)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Stability test failed: {str(e)}',
                'stability_score': 0
            }

    # Enhanced Template Methods (keep your existing templates, just fix MIME imports)
    def _get_admin_test_template(self, test_type: str, config: Dict) -> str:
        """Admin test template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Admin Test</title></head>
        <body>
            <h2>✅ Admin Test Successful</h2>
            <p><strong>Test Type:</strong> {test_type}</p>
            <p><strong>Server:</strong> {config.get('smtp_server')}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """

    def _get_user_test_template(self, test_type: str) -> str:
        """User test template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>User Test</title></head>
        <body>
            <h2>🎉 Test Successful!</h2>
            <p>FileHubX Bot email system is working correctly.</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """

    # Keep all your existing template methods (get_thankyou_template, etc.)
    # ... [Your existing template methods remain the same] ...

    # Enhanced Subscription Management
    async def subscribe_user(self, user_id: int, email: str, name: str = None, username: str = None) -> Dict:
        """Enhanced user subscription with better error handling"""
        try:
            # Validate email
            if not self.is_valid_email(email):
                return {'success': False, 'error': '❌ Invalid email format'}

            # Check existing subscription
            existing = await self.db.get_email(user_id)
            if existing and existing.get('is_active'):
                return {'success': False, 'error': '⚠️ Already subscribed to email notifications'}

            # Test email service first
            test_result = await self.quick_test(email)
            if not test_result['success']:
                return {
                    'success': False, 
                    'error': f'❌ Email service unavailable: {test_result.get("error", "Please try again later")}'
                }

            # Add to database
            await self.db.add_email(user_id, email, name, username)
            total_subscribers = await self.db.get_total_users()

            # Prepare user data
            user_data = {
                'user_id': user_id,
                'name': name or 'User',
                'username': username,
                'total_subscribers': total_subscribers
            }

            # Send welcome email
            welcome_html = self.get_thankyou_template(user_data)
            email_result = await self.send_email(
                email,
                "🎉 Welcome to FileHubX Bot!",
                welcome_html
            )

            return {
                'success': True,
                'email_sent': email_result['success'],
                'message': '✅ Successfully subscribed to email notifications!',
                'subscription_id': f"sub_{user_id}_{int(time.time())}"
            }

        except Exception as e:
            logger.error(f"Subscription error for user {user_id}: {e}")
            return {'success': False, 'error': f'❌ Subscription failed: {str(e)}'}

    async def quick_test(self, recipient_email: str) -> Dict:
        """Quick email test"""
        try:
            test_html = "<h3>Quick Test</h3><p>Email system test.</p>"
            return await self.send_email(recipient_email, "Quick Test", test_html)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Add the missing methods that were causing errors
    async def get_subscription_status(self, user_id: int) -> Dict:
        """Get user's email subscription status"""
        try:
            email_info = await self.db.get_email(user_id)
            if email_info and email_info.get('is_active'):
                return {
                    'success': True,
                    'subscribed': True,
                    'email': email_info.get('email'),
                    'subscription_date': email_info.get('joined_date'),
                    'name': email_info.get('name')
                }
            return {'success': True, 'subscribed': False}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def unsubscribe_user(self, user_id: int) -> Dict:
        """Unsubscribe user from email notifications"""
        try:
            success = await self.db.remove_email(user_id)
            return {
                'success': success,
                'message': 'Unsubscribed successfully' if success else 'Not subscribed'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def get_system_stats(self) -> Dict:
        """Get email system statistics"""
        try:
            total = await self.db.get_total_users()
            active = await self.db.get_active_subscribers()
            return {
                'success': True,
                'stats': {
                    'total_subscribers': total,
                    'active_subscribers': active,
                    'smtp_status': 'Connected' if self.is_connected else 'Disconnected'
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global instance
email_system = EnhancedSpideyEmailSystem()

async def initialize_email_system():
    """Initialize email system with connection test"""
    logger.info("🔄 Initializing enhanced email system...")
    success, message = await email_system.connect_smtp()
    if success:
        logger.info("✅ Email system initialized successfully")
    else:
        logger.warning(f"⚠️ Email system initialization warning: {message}")
    return success

async def shutdown_email_system():
    """Shutdown email system gracefully"""
    await email_system.disconnect_smtp()
    logger.info("🔴 Email system shutdown completed")
