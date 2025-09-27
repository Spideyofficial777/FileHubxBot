# Don't Remove Credit @Spideyofficial777
# Ask Doubt on telegram @Spideyofficial777
#
# Copyright (C) 2025 by Spidey Official, < https://t.me/Spideyofficial777 >
#
# All rights reserved.
#

import motor.motor_asyncio
from datetime import datetime, timedelta
from config import * # DB_URI, DB_NAME
import logging

logger = logging.getLogger(__name__)

class EmailDatabase:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.db = self.client[DB_NAME]
        self.email_collection = self.db['email_subscriptions']
        self.email_stats = self.db['email_stats']

    async def add_email(self, user_id: int, email: str, name: str = None, username: str = None):
        """Add or update user email subscription"""
        try:
            await self.email_collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'email': email.lower().strip(),
                        'name': name,
                        'username': username,
                        'joined_date': datetime.now(),
                        'is_active': True,
                        'last_updated': datetime.now(),
                        'subscription_count': 1
                    }
                },
                upsert=True
            )
            
            # Update statistics
            await self.update_stats('subscriptions_added')
            return True
        except Exception as e:
            logger.error(f"Error adding email: {e}")
            return False

    async def remove_email(self, user_id: int):
        """Remove user email subscription"""
        try:
            result = await self.email_collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_active': False,
                        'removed_date': datetime.now(),
                        'last_updated': datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                await self.update_stats('subscriptions_removed')
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing email: {e}")
            return False

    async def get_email(self, user_id: int):
        """Get user email subscription information"""
        try:
            return await self.email_collection.find_one({'user_id': user_id, 'is_active': True})
        except Exception as e:
            logger.error(f"Error getting email: {e}")
            return None

    async def get_all_emails(self):
        """Get all active subscriber emails"""
        try:
            cursor = self.email_collection.find({'is_active': True})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting all emails: {e}")
            return []

    async def get_total_users(self):
        """Get total number of email subscribers"""
        try:
            return await self.email_collection.count_documents({'is_active': True})
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0

    async def get_active_subscribers(self):
        """Get subscribers who joined in last 30 days"""
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            return await self.email_collection.count_documents({
                'is_active': True,
                'joined_date': {'$gte': thirty_days_ago}
            })
        except Exception as e:
            logger.error(f"Error counting active subscribers: {e}")
            return 0

    async def get_recent_activity(self, days: int = 7):
        """Get recent subscription activity"""
        try:
            since_date = datetime.now() - timedelta(days=days)
            pipeline = [
                {'$match': {'last_updated': {'$gte': since_date}}},
                {'$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$last_updated'}},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'_id': 1}}
            ]
            cursor = self.email_collection.aggregate(pipeline)
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []

    async def update_stats(self, stat_type: str):
        """Update email statistics"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            await self.email_stats.update_one(
                {'date': today, 'stat_type': 'daily'},
                {
                    '$inc': {stat_type: 1},
                    '$set': {'last_updated': datetime.now()}
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error updating stats: {e}")

    async def search_subscriptions(self, query: str):
        """Search subscriptions by email or name"""
        try:
            regex_query = {'$regex': query, '$options': 'i'}
            cursor = self.email_collection.find({
                'is_active': True,
                '$or': [
                    {'email': regex_query},
                    {'name': regex_query},
                    {'username': regex_query}
                ]
            })
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error searching subscriptions: {e}")
            return []

    async def get_subscription_analytics(self):
        """Get subscription analytics"""
        try:
            # Total subscriptions
            total = await self.get_total_users()
            
            # Monthly growth
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_growth = await self.email_collection.count_documents({
                'is_active': True,
                'joined_date': {'$gte': current_month}
            })
            
            # Weekly growth
            week_ago = datetime.now() - timedelta(days=7)
            weekly_growth = await self.email_collection.count_documents({
                'is_active': True,
                'joined_date': {'$gte': week_ago}
            })
            
            return {
                'total_subscriptions': total,
                'monthly_growth': monthly_growth,
                'weekly_growth': weekly_growth,
                'growth_rate': round((weekly_growth / total * 100), 2) if total > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}