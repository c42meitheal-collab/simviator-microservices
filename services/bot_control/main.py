#!/usr/bin/env python3
"""
Bot Control Service - Multi-platform AI Bot Management

A focused service providing:
- Discord bot management
- Twitch chat integration
- Character/personality synchronisation with Simviator
- Cross-platform event coordination

Architecture: Microservice designed to coordinate with Simviator
Dependencies: Platform-specific (discord.py, twitchio, etc.)
"""

import asyncio
import logging
import json
import signal
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse

@dataclass
class BotConfig:
    """Configuration for Bot Control service"""
    service_name: str = "bot_control"
    service_port: int = 8002
    
    # Discord configuration
    discord_enabled: bool = False
    discord_token: Optional[str] = None
    discord_guild_id: Optional[str] = None
    
    # Twitch configuration
    twitch_enabled: bool = False
    twitch_oauth: Optional[str] = None
    twitch_channel: Optional[str] = None
    
    # Personality management
    default_personality: str = "friendly_helper"
    personality_sync_enabled: bool = True
    
    # Cross-service integration
    simviator_service_url: str = "http://localhost:8001"
    event_sync_enabled: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

class PersonalityManager:
    """Manage bot personalities across platforms"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.logger = logging.getLogger('PersonalityManager')
        
        # Current personality state
        self.current_personality = config.default_personality
        self.personality_context = {}
        self.flight_context = {}
        
        # Available personalities
        self.personalities = {
            'friendly_helper': {
                'name': 'Friendly Helper',
                'description': 'Helpful and cheerful assistant',
                'response_style': 'casual_friendly',
                'aviation_knowledge': 'basic'
            },
            'dublin_control': {
                'name': 'Dublin Control',
                'description': 'Professional ATC-style responses',
                'response_style': 'professional_atc',
                'aviation_knowledge': 'expert'
            },
            'aviation_expert': {
                'name': 'Aviation Expert',
                'description': 'Technical aviation knowledge specialist',
                'response_style': 'technical_professional',
                'aviation_knowledge': 'expert'
            },
            'captain_murphy': {
                'name': 'Captain Murphy',
                'description': 'Veteran pilot with stories and wisdom',
                'response_style': 'experienced_storyteller',
                'aviation_knowledge': 'expert'
            },
            'sarah_spotter': {
                'name': 'Sarah (Aviation Enthusiast)',
                'description': 'Excited aircraft spotter',
                'response_style': 'enthusiastic_casual',
                'aviation_knowledge': 'intermediate'
            }
        }
    
    def set_personality(self, personality_id: str) -> bool:
        """Set current bot personality"""
        
        if personality_id not in self.personalities:
            self.logger.error(f"Unknown personality: {personality_id}")
            return False
        
        old_personality = self.current_personality
        self.current_personality = personality_id
        
        self.logger.info(f"Personality changed: {old_personality} -> {personality_id}")
        return True
    
    def update_flight_context(self, flight_data: Dict[str, Any]):
        """Update personality context with flight information"""
        
        self.flight_context = {
            'callsign': flight_data.get('callsign', 'unknown'),
            'phase': flight_data.get('phase', 'unknown'),
            'altitude': flight_data.get('altitude', 0),
            'aircraft_type': flight_data.get('aircraft_type', 'unknown'),
            'last_updated': datetime.now().isoformat()
        }
        
        # Adjust personality context based on flight phase
        phase = flight_data.get('phase', '')
        if phase in ['takeoff', 'landing']:
            self.personality_context['alertness'] = 'high'
            self.personality_context['technical_focus'] = True
        elif phase == 'cruise':
            self.personality_context['alertness'] = 'normal'
            self.personality_context['technical_focus'] = False
        
        self.logger.debug(f"Updated flight context: {self.flight_context}")
    
    def get_current_personality(self) -> Dict[str, Any]:
        """Get current personality information"""
        
        personality_info = self.personalities[self.current_personality].copy()
        personality_info['id'] = self.current_personality
        personality_info['context'] = self.personality_context.copy()
        personality_info['flight_context'] = self.flight_context.copy()
        
        return personality_info
    
    def generate_response_context(self, message_content: str) -> Dict[str, Any]:
        """Generate context for bot response generation"""
        
        personality_info = self.get_current_personality()
        
        return {
            'personality': personality_info,
            'message': message_content,
            'timestamp': datetime.now().isoformat(),
            'flight_context_available': bool(self.flight_context),
            'technical_mode': self.personality_context.get('technical_focus', False)
        }

class DiscordBot:
    """Discord bot implementation"""
    
    def __init__(self, config: BotConfig, personality_manager: PersonalityManager):
        self.config = config
        self.personality_manager = personality_manager
        self.logger = logging.getLogger('DiscordBot')
        
        self.bot = None
        self.connected = False
        
    async def start(self):
        """Start Discord bot"""
        
        if not self.config.discord_enabled:
            self.logger.info("Discord bot disabled in configuration")
            return
        
        if not self.config.discord_token:
            self.logger.error("Discord token not configured")
            return
        
        self.logger.info("Discord bot would start here")
        self.logger.info("(Discord.py integration not implemented in this focused demo)")
        
        # Simulate connection
        self.connected = True
        self.logger.info("Discord bot simulation: Connected")
    
    async def stop(self):
        """Stop Discord bot"""
        
        if self.connected:
            self.logger.info("Discord bot simulation: Disconnecting")
            self.connected = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get Discord bot status"""
        
        return {
            'enabled': self.config.discord_enabled,
            'connected': self.connected,
            'token_configured': bool(self.config.discord_token),
            'guild_id': self.config.discord_guild_id
        }

class TwitchBot:
    """Twitch bot implementation"""
    
    def __init__(self, config: BotConfig, personality_manager: PersonalityManager):
        self.config = config
        self.personality_manager = personality_manager
        self.logger = logging.getLogger('TwitchBot')
        
        self.bot = None
        self.connected = False
    
    async def start(self):
        """Start Twitch bot"""
        
        if not self.config.twitch_enabled:
            self.logger.info("Twitch bot disabled in configuration")
            return
        
        if not self.config.twitch_oauth:
            self.logger.error("Twitch OAuth not configured")
            return
        
        self.logger.info("Twitch bot would start here")
        self.logger.info("(TwitchIO integration not implemented in this focused demo)")
        
        # Simulate connection
        self.connected = True
        self.logger.info("Twitch bot simulation: Connected")
    
    async def stop(self):
        """Stop Twitch bot"""
        
        if self.connected:
            self.logger.info("Twitch bot simulation: Disconnecting")
            self.connected = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get Twitch bot status"""
        
        return {
            'enabled': self.config.twitch_enabled,
            'connected': self.connected,
            'oauth_configured': bool(self.config.twitch_oauth),
            'channel': self.config.twitch_channel
        }

class EventSyncManager:
    """Manage synchronisation with other services (especially Simviator)"""
    
    def __init__(self, config: BotConfig, personality_manager: PersonalityManager):
        self.config = config
        self.personality_manager = personality_manager
        self.logger = logging.getLogger('EventSyncManager')
        
        self.simviator_connected = False
        self.last_flight_data = {}
        
    async def start_sync(self):
        """Start event synchronisation"""
        
        if not self.config.event_sync_enabled:
            self.logger.info("Event sync disabled")
            return
        
        # Start monitoring Simviator events
        asyncio.create_task(self._simviator_sync_loop())
    
    async def _simviator_sync_loop(self):
        """Monitor Simviator service for flight events"""
        
        self.logger.info(f"Starting sync with Simviator service: {self.config.simviator_service_url}")
        
        while True:
            try:
                # In a real implementation, this would:
                # 1. Poll Simviator API for current flight data
                # 2. Subscribe to Simviator events via WebSocket
                # 3. Update personality context when flight events occur
                
                # For demo: simulate flight data updates
                simulated_flight_data = {
                    'callsign': 'EI-SIM',
                    'phase': 'cruise',
                    'altitude': 35000,
                    'aircraft_type': 'B737',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Update personality context if data changed
                if simulated_flight_data != self.last_flight_data:
                    self.personality_manager.update_flight_context(simulated_flight_data)
                    self.last_flight_data = simulated_flight_data
                    self.logger.debug("Updated personality context from Simviator data")
                
                if not self.simviator_connected:
                    self.simviator_connected = True
                    self.logger.info("Simviator sync: Connected (simulated)")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in Simviator sync loop: {e}")
                self.simviator_connected = False
                await asyncio.sleep(10)  # Wait longer on error
    
    def get_status(self) -> Dict[str, Any]:
        """Get sync status"""
        
        return {
            'sync_enabled': self.config.event_sync_enabled,
            'simviator_connected': self.simviator_connected,
            'simviator_url': self.config.simviator_service_url,
            'last_flight_data': self.last_flight_data
        }

class BotControlService:
    """Main Bot Control service"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.logger = logging.getLogger('BotControlService')
        
        # Core components
        self.personality_manager = PersonalityManager(config)
        self.discord_bot = DiscordBot(config, self.personality_manager)
        self.twitch_bot = TwitchBot(config, self.personality_manager)
        self.event_sync = EventSyncManager(config, self.personality_manager)
        
        # Service state
        self.running = False
        self.start_time = datetime.now()
        
        # Setup signal handling
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the Bot Control service"""
        
        self.logger.info(f"Starting Bot Control service on port {self.config.service_port}")
        self.logger.info(f"Configuration: {asdict(self.config)}")
        
        self.running = True
        
        # Start all components
        await self.discord_bot.start()
        await self.twitch_bot.start()
        await self.event_sync.start_sync()
        
        try:
            # Keep service running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Service error: {e}")
        finally:
            # Clean shutdown
            await self.discord_bot.stop()
            await self.twitch_bot.stop()
        
        self.logger.info("Bot Control service stopped")
    
    def stop(self):
        """Stop the service"""
        self.logger.info("Stopping Bot Control service...")
        self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        
        uptime = datetime.now() - self.start_time
        
        return {
            'service': self.config.service_name,
            'status': 'running' if self.running else 'stopped',
            'uptime_seconds': uptime.total_seconds(),
            'personality_manager': {
                'current_personality': self.personality_manager.current_personality,
                'available_personalities': list(self.personality_manager.personalities.keys()),
                'flight_context': self.personality_manager.flight_context
            },
            'discord_bot': self.discord_bot.get_status(),
            'twitch_bot': self.twitch_bot.get_status(),
            'event_sync': self.event_sync.get_status(),
            'config': asdict(self.config)
        }

def setup_logging(config: BotConfig):
    """Setup logging configuration"""
    
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

def load_config(config_file: Optional[str] = None) -> BotConfig:
    """Load configuration from file or create default"""
    
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            return BotConfig(**config_data)
        except Exception as e:
            print(f"Error loading config from {config_file}: {e}")
    
    # Return default config
    return BotConfig()

def save_default_config(config_file: str):
    """Save default configuration to file"""
    
    config = BotConfig()
    config_data = asdict(config)
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"Default configuration saved to {config_file}")

async def test_service():
    """Test the bot service components"""
    
    print("[BOT] Testing Bot Control Service Components")
    print("=" * 60)
    
    # Test personality manager
    print("\n1. Testing Personality Manager:")
    config = BotConfig()
    personality_manager = PersonalityManager(config)
    
    print(f"   Default personality: {personality_manager.current_personality}")
    print(f"   Available personalities: {list(personality_manager.personalities.keys())}")
    
    # Test personality switching
    result = personality_manager.set_personality('dublin_control')
    print(f"   Personality switch to dublin_control: {'[OK]' if result else '[ERROR]'}")
    
    # Test flight context update
    flight_data = {
        'callsign': 'EI-TEST',
        'phase': 'takeoff',
        'altitude': 1500,
        'aircraft_type': 'B737'
    }
    personality_manager.update_flight_context(flight_data)
    current_personality = personality_manager.get_current_personality()
    print(f"   Flight context updated: {current_personality['flight_context']['callsign']}")
    
    print("\n2. Testing Service Integration:")
    service = BotControlService(config)
    
    # Start service for a short time
    start_task = asyncio.create_task(service.start())
    
    # Let it run for a few seconds
    await asyncio.sleep(3)
    
    # Get status
    status = service.get_status()
    print(f"   Service status: {status['status']}")
    print(f"   Discord enabled: {status['discord_bot']['enabled']}")
    print(f"   Twitch enabled: {status['twitch_bot']['enabled']}")
    print(f"   Event sync enabled: {status['event_sync']['sync_enabled']}")
    
    # Stop service
    service.stop()
    await start_task
    
    print("\n[OK] Bot Control Service test completed")

async def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Bot Control Service - Multi-platform Bot Management")
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--test', action='store_true', help='Run tests instead of service')
    parser.add_argument('--save-config', help='Save default config to file and exit')
    parser.add_argument('--port', type=int, help='Override service port')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       help='Override log level')
    
    args = parser.parse_args()
    
    # Handle config save
    if args.save_config:
        save_default_config(args.save_config)
        return
    
    # Handle test mode
    if args.test:
        await test_service()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Apply command line overrides
    if args.port:
        config.service_port = args.port
    if args.log_level:
        config.log_level = args.log_level
    
    # Setup logging
    setup_logging(config)
    
    # Create and start service
    service = BotControlService(config)
    
    try:
        await service.start()
    except KeyboardInterrupt:
        print("\nService interrupted by user")
    except Exception as e:
        print(f"Service error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
