from typing import Optional, Dict, Any

class Temp:
    """
    Temporary storage class for bot runtime variables.
    
    Attributes:
        ME: The bot's own user information
        U_NAME: Bot username
        B_NAME: Bot display name
        B_LINK: Bot invite link
        _cache: Dictionary for temporary storage
    """
    
    ME: Optional[Dict[str, Any]] = None
    U_NAME: Optional[str] = None
    B_NAME: Optional[str] = None
    B_LINK: Optional[str] = None
    _cache: Dict[str, Any] = {}

    @classmethod
    def set_bot_info(cls, username: str, display_name: str, invite_link: str) -> None:
        """
        Set basic bot information.
        
        Args:
            username: The bot's username (without @)
            display_name: The bot's display name
            invite_link: Full invite link to the bot
        """
        cls.U_NAME = username
        cls.B_NAME = display_name
        cls.B_LINK = invite_link

    @classmethod
    def set_me(cls, user_data: Dict[str, Any]) -> None:
        """
        Set the bot's own user information.
        
        Args:
            user_data: Dictionary containing user information from Telegram
        """
        cls.ME = user_data
        if not cls.U_NAME and 'username' in user_data:
            cls.U_NAME = user_data['username']

    @classmethod
    def cache_set(cls, key: str, value: Any, ttl: int = 0) -> None:
        """
        Store a temporary value in cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (0 = no expiration)
        """
        cls._cache[key] = {
            'value': value,
            'expires': time.time() + ttl if ttl > 0 else None
        }

    @classmethod
    def cache_get(cls, key: str) -> Optional[Any]:
        """
        Retrieve a cached value.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            The cached value or None if not found/expired
        """
        item = cls._cache.get(key)
        if not item:
            return None
            
        if item['expires'] and item['expires'] < time.time():
            del cls._cache[key]
            return None
            
        return item['value']

    @classmethod
    def cache_clear(cls, key: str = None) -> None:
        """
        Clear cache items.
        
        Args:
            key: Specific key to clear (None clears all)
        """
        if key:
            cls._cache.pop(key, None)
        else:
            cls._cache.clear()

    @classmethod
    def get_bot_mention(cls) -> str:
        """
        Get formatted bot mention.
        
        Returns:
            String in format "[Bot Name](t.me/username)"
        """
        if cls.U_NAME and cls.B_NAME:
            return f"[{cls.B_NAME}](https://t.me/{cls.U_NAME})"
        return "the bot"

    @classmethod
    def get_bot_info(cls) -> Dict[str, Optional[str]]:
        """
        Get all bot information.
        
        Returns:
            Dictionary with bot info (username, name, link)
        """
        return {
            'username': cls.U_NAME,
            'name': cls.B_NAME,
            'link': cls.B_LINK
        }
