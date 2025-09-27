# this is the test email for the testing our service to gate the send the email on the user 

# Don't Remove Credit @hacker_x_official_777
# Ask Doubt on telegram @hacker_x_official_777
#
# Copyright (C) 2025 by Hacker X Official, < https://t.me/hacker_x_official_777 >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import smtplib
import asyncio
import aiosmtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import re
from database.db_email import EmailDatabase
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpideyEmailNotificationSystem:
    def __init__(self):
        self.db = EmailDatabase()
        self.smtp_config = {
            'server': SMTP_SERVER,
            'port': SMTP_PORT,
            'username': SMTP_USERNAME,
            'password': SMTP_PASSWORD,
            'from_email': FROM_EMAIL,
            'from_name': FROM_NAME,
            'admin_email': ADMIN_EMAIL
        }
        self.is_connected = False
        self.smtp_connection = None
        self.test_results = {}

    async def connect_smtp(self):
        """Establish SMTP connection with retry mechanism"""
        try:
            logger.info(f"🔗 Attempting to connect to SMTP server: {self.smtp_config['server']}:{self.smtp_config['port']}")
            
            self.smtp_connection = aiosmtplib.SMTP(
                hostname=self.smtp_config['server'],
                port=self.smtp_config['port'],
                use_tls=True,
                timeout=30
            )
            
            await self.smtp_connection.connect()
            logger.info("✅ SMTP connection established")
            
            await self.smtp_connection.login(
                self.smtp_config['username'],
                self.smtp_config['password']
            )
            logger.info("✅ SMTP login successful")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ SMTP connection failed: {e}")
            self.is_connected = False
            return False

    async def disconnect_smtp(self):
        """Close SMTP connection"""
        if self.smtp_connection and self.is_connected:
            try:
                await self.smtp_connection.quit()
                self.is_connected = False
                logger.info("🔌 SMTP connection closed")
            except Exception as e:
                logger.error(f"Error disconnecting SMTP: {e}")

    # Email Validation
    def is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    # Test Email Template
    def get_test_template(self, test_type: str, user_data: Dict = None) -> str:
        """Test email template for testing service"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Test - FileHubX Bot</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 20px auto; 
                    background: #ffffff; 
                    border-radius: 15px; 
                    overflow: hidden; 
                    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(45deg, #FF416C, #FF4B2B); 
                    padding: 30px; 
                    text-align: center; 
                    color: white; 
                }}
                .content {{ 
                    padding: 30px; 
                    color: #333;
                    line-height: 1.6;
                }}
                .test-result {{
                    background: #e8f5e8;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #28a745;
                    margin: 20px 0;
                }}
                .test-info {{
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 Email Service Test</h1>
                    <p>FileHubX Bot Notification System</p>
                </div>
                <div class="content">
                    <div class="test-result">
                        <h2>✅ Test Successful!</h2>
                        <p><strong>Test Type:</strong> {test_type}</p>
                        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Service Status:</strong> Operational</p>
                    </div>
                    
                    <div class="test-info">
                        <h3>📊 Test Details:</h3>
                        <p>This is a test email to verify that the FileHubX Bot email notification system is working correctly.</p>
                        <p><strong>SMTP Server:</strong> {self.smtp_config['server']}</p>
                        <p><strong>Bot Username:</strong> @{BOT_USERNAME}</p>
                        <p><strong>Maintained by:</strong> @hacker_x_official_777</p>
                    </div>
                    
                    <h3>🔧 What was tested:</h3>
                    <ul>
                        <li>SMTP Connection</li>
                        <li>Email Sending Capability</li>
                        <li>HTML Template Rendering</li>
                        <li>System Integration</li>
                    </ul>
                    
                    <p style="text-align: center; color: #666; margin-top: 30px;">
                        <em>This is an automated test email. If you received this, the email system is working correctly.</em>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    def get_admin_test_template(self, test_type: str, test_details: Dict) -> str:
        """Admin test email template"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Test Report - FileHubX Bot</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .test-section {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .success {{ border-left: 4px solid #28a745; }}
                .error {{ border-left: 4px solid #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Admin Test Report</h1>
                    <p>FileHubX Bot Email System</p>
                </div>
                
                <div class="test-section success">
                    <h3>🧪 Test Configuration</h3>
                    <p><strong>Test Type:</strong> {test_type}</p>
                    <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>SMTP Server:</strong> {test_details.get('smtp_server', 'N/A')}</p>
                    <p><strong>Admin Email:</strong> {test_details.get('admin_email', 'N/A')}</p>
                </div>
                
                <div class="test-section success">
                    <h3>✅ Test Results</h3>
                    <p><strong>Status:</strong> COMPLETED</p>
                    <p><strong>User Test:</strong> {test_details.get('user_test', 'N/A')}</p>
                    <p><strong>Admin Test:</strong> {test_details.get('admin_test', 'N/A')}</p>
                    <p><strong>Total Tests:</strong> {test_details.get('total_tests', 0)}</p>
                </div>
                
                <div class="test-section">
                    <h3>📊 System Information</h3>
                    <p><strong>Bot:</strong> @{BOT_USERNAME}</p>
                    <p><strong>Maintained by:</strong> @hacker_x_official_777</p>
                    <p><strong>Test ID:</strong> {test_details.get('test_id', 'N/A')}</p>
                </div>
            </div>
        </body>
        </html>
        """

    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> Dict:
        """Send email with detailed error reporting"""
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Check connection
            if not self.is_connected:
                logger.info("🔗 Establishing SMTP connection...")
                connection_result = await self.connect_smtp()
                if not connection_result:
                    return {
                        'success': False,
                        'error': 'SMTP connection failed',
                        'test_id': test_id,
                        'step': 'connection'
                    }

            # Create message
            message = MimeMultipart('alternative')
            message['From'] = f"{self.smtp_config['from_name']} <{self.smtp_config['from_email']}>"
            message['To'] = to_email
            message['Subject'] = subject

            # Create text version
            if text_content is None:
                text_content = "Please enable HTML to view this email properly."
            
            part1 = MimeText(text_content, 'plain')
            part2 = MimeText(html_content, 'html')
            
            message.attach(part1)
            message.attach(part2)

            # Send email
            logger.info(f"📤 Sending email to {to_email}...")
            await self.smtp_connection.send_message(
                message,
                sender=self.smtp_config['from_email'],
                recipients=[to_email]
            )
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return {
                'success': True,
                'message': 'Email sent successfully',
                'test_id': test_id,
                'recipient': to_email,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            error_msg = f"❌ Failed to send email to {to_email}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': str(e),
                'test_id': test_id,
                'step': 'sending',
                'recipient': to_email
            }

    # Test Functions
    async def test_email_service(self, user_id: int = None, user_email: str = None) -> Dict:
        """Comprehensive email service test"""
        test_id = f"full_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_results = {
            'test_id': test_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tests': {}
        }

        try:
            # Test 1: SMTP Connection
            logger.info("🧪 Testing SMTP connection...")
            connection_test = await self.connect_smtp()
            test_results['tests']['smtp_connection'] = {
                'success': connection_test,
                'message': 'SMTP connection established' if connection_test else 'SMTP connection failed'
            }

            if not connection_test:
                test_results['overall_success'] = False
                test_results['error'] = 'SMTP connection failed'
                return test_results

            # Test 2: Send test email to admin
            logger.info("🧪 Sending test email to admin...")
            admin_test_html = self.get_admin_test_template("Service Test", {
                'smtp_server': self.smtp_config['server'],
                'admin_email': self.smtp_config['admin_email'],
                'test_id': test_id
            })
            
            admin_result = await self.send_email(
                self.smtp_config['admin_email'],
                "🧪 Admin Test - FileHubX Bot Email System",
                admin_test_html,
                "This is a test email to verify the admin notification system is working."
            )
            
            test_results['tests']['admin_email'] = admin_result

            # Test 3: Send test email to user (if provided)
            if user_email and self.is_valid_email(user_email):
                logger.info(f"🧪 Sending test email to user: {user_email}")
                user_test_html = self.get_test_template("User Test")
                
                user_result = await self.send_email(
                    user_email,
                    "🧪 Test Email - FileHubX Bot",
                    user_test_html,
                    "This is a test email from FileHubX Bot. If you received this, the email system is working correctly."
                )
                
                test_results['tests']['user_email'] = user_result
            else:
                test_results['tests']['user_email'] = {
                    'success': False,
                    'message': 'No valid user email provided for testing'
                }

            # Calculate overall success
            successful_tests = sum(1 for test in test_results['tests'].values() if test.get('success', False))
            total_tests = len(test_results['tests'])
            test_results['overall_success'] = successful_tests == total_tests
            test_results['success_rate'] = f"{successful_tests}/{total_tests}"

            # Store test results
            self.test_results[test_id] = test_results
            
            logger.info(f"📊 Test completed: {test_results['success_rate']} tests passed")
            return test_results

        except Exception as e:
            error_msg = f"❌ Comprehensive test failed: {str(e)}"
            logger.error(error_msg)
            test_results['overall_success'] = False
            test_results['error'] = str(e)
            return test_results

    async def quick_test(self, recipient_email: str) -> Dict:
        """Quick email test to specific recipient"""
        try:
            test_html = self.get_test_template("Quick Test")
            
            result = await self.send_email(
                recipient_email,
                "⚡ Quick Test - FileHubX Bot",
                test_html,
                "Quick test email from FileHubX Bot email system."
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'test_type': 'quick_test'
            }

    async def get_test_result(self, test_id: str) -> Dict:
        """Get specific test result by ID"""
        return self.test_results.get(test_id, {'error': 'Test ID not found'})

    # User Email Subscription Management
    async def subscribe_user(self, user_id: int, email: str, name: str = None, username: str = None) -> Dict:
        """Subscribe user to email notifications"""
        try:
            # Validate email
            if not self.is_valid_email(email):
                return {'success': False, 'error': '❌ Invalid email format'}

            # Check if already subscribed
            existing = await self.db.get_email(user_id)
            if existing and existing.get('is_active'):
                return {'success': False, 'error': '⚠️ Already subscribed'}

            # Add/update user email
            await self.db.add_email(user_id, email, name, username)
            
            # Get total subscribers
            total_subscribers = await self.db.get_total_users()

            # Prepare user data
            user_data = {
                'user_id': user_id,
                'name': name or 'User',
                'username': username,
                'total_subscribers': total_subscribers
            }

            # Test email service before sending actual emails
            test_result = await self.quick_test(email)
            if not test_result['success']:
                return {
                    'success': False, 
                    'error': f'❌ Email service test failed: {test_result.get("error", "Unknown error")}'
                }

            # Send thank you email to user
            thankyou_html = self.get_thankyou_template(user_data)
            thankyou_sent = await self.send_email(
                email,
                "🎉 Welcome to FileHubX Bot!",
                thankyou_html,
                f"Thank you for subscribing! Join our channels: t.me/spideyofficial777"
            )

            # Send notification to admin
            admin_html = self.get_admin_notification_template(user_data, email)
            admin_sent = await self.send_email(
                self.smtp_config['admin_email'],
                f"📧 New Subscription: {email}",
                admin_html,
                f"New subscriber: {name} ({email})"
            )

            return {
                'success': True,
                'user_email_sent': thankyou_sent['success'] if thankyou_sent else False,
                'admin_notification_sent': admin_sent['success'] if admin_sent else False,
                'message': '✅ Subscribed successfully!'
            }

        except Exception as e:
            logger.error(f"Error subscribing user {user_id}: {e}")
            return {'success': False, 'error': f'❌ Subscription failed: {str(e)}'}

    # Existing template functions (keep your previous templates)
    def get_thankyou_template(self, user_data: Dict) -> str:
        """Thank you email template after subscription"""
        # ... (keep your existing thank you template code)
        return "Thank you template HTML"

    def get_admin_notification_template(self, user_data: Dict, email: str) -> str:
        """Admin notification template"""
        # ... (keep your existing admin template code)
        return "Admin template HTML"

# Global email system instance
email_system = SpideyEmailNotificationSystem()

# Utility functions
async def initialize_email_system():
    return await email_system.connect_smtp()

async def shutdown_email_system():
    await email_system.disconnect_smtp()
