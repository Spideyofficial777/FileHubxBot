# This is the testing db for the sending email to the user we are created this only for the testing

# Add this method to your existing EmailDatabase class
async def log_test_result(self, test_id: str, test_data: Dict):
    """Log email test results"""
    try:
        await self.email_stats.update_one(
            {'test_id': test_id},
            {
                '$set': {
                    'test_data': test_data,
                    'timestamp': datetime.now(),
                    'type': 'email_test'
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error logging test result: {e}")
        return False

async def get_test_logs(self, limit: int = 10):
    """Get recent test logs"""
    try:
        cursor = self.email_stats.find({'type': 'email_test'}).sort('timestamp', -1).limit(limit)
        return await cursor.to_list(length=limit)
    except Exception as e:
        logger.error(f"Error getting test logs: {e}")
        return []
