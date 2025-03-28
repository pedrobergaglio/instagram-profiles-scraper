import logging
import random
from typing import Optional, List
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.last_rotation = datetime.utcnow()
        self.rotation_interval = timedelta(minutes=30)  # Rotate proxies every 30 minutes
        self._load_proxies()
        logger.info("Initialized ProxyManager")

    def _load_proxies(self):
        """Load proxies from environment variables or configuration."""
        # Try to get proxy from environment variable
        proxy = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
        if proxy:
            self.proxies.append(proxy)
            logger.info(f"Loaded proxy from environment: {proxy}")
        
        # TODO: Add support for loading proxy list from file or API
        # For now, we'll use a default proxy if none are configured
        if not self.proxies:
            logger.warning("No proxies configured, will proceed without proxy")

    def get_next_proxy(self) -> Optional[str]:
        """Get the next proxy in the rotation."""
        if not self.proxies:
            return None

        # Check if it's time to rotate
        now = datetime.utcnow()
        if now - self.last_rotation >= self.rotation_interval:
            self.rotate_proxies()

        # Get next proxy
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        logger.info(f"Using proxy: {proxy}")
        return proxy

    def rotate_proxies(self):
        """Rotate the proxy list."""
        if self.proxies:
            random.shuffle(self.proxies)
            self.current_index = 0
            self.last_rotation = datetime.utcnow()
            logger.info("Rotated proxy list")

    def add_proxy(self, proxy: str):
        """Add a new proxy to the list."""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            logger.info(f"Added new proxy: {proxy}")

    def remove_proxy(self, proxy: str):
        """Remove a proxy from the list."""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            logger.info(f"Removed proxy: {proxy}")

    def get_proxy_count(self) -> int:
        """Get the number of available proxies."""
        return len(self.proxies)

    def clear_proxies(self):
        """Clear all proxies from the list."""
        self.proxies = []
        self.current_index = 0
        logger.info("Cleared all proxies") 