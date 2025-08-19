#!/usr/bin/env python3
"""
Simviator Service - Flight Simulation Commentary and Character System

A focused service providing:
- Real-time flight commentary using ICAO standards
- Professional aviation character guidance
- Flight data monitoring and processing
- Event publishing for other services

Architecture: Microservice designed to run independently
Dependencies: Minimal - aviation core only
"""

import asyncio
import logging
import json
import signal
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse

# Import our core components
from aviation_pronunciation import AviationPronunciationEngine, test_aviation_pronunciation
from flight_guidance_character import FlightGuidanceCharacterSystem, test_guidance_system

@dataclass
class SimviatorConfig:
    """Configuration for Simviator service"""
    service_name: str = "simviator"
    service_port: int = 8001
    
    # Flight monitoring
    flight_sim_type: str = "auto"  # auto, xplane, msfs
    update_interval: float = 1.0    # seconds
    
    # Character system
    default_character: str = "dublin_control"
    guidance_enabled: bool = True
    
    # Audio/Voice
    voice_enabled: bool = False
    voice_engine: str = "system"  # system, azure, amazon
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

class FlightMonitor:
    """Monitor flight simulation data"""
    
    def __init__(self, config: SimviatorConfig):
        self.config = config
        self.logger = logging.getLogger('FlightMonitor')
        self.running = False
        self.current_data: Dict[str, Any] = {}
        
        # Event callbacks
        self.data_callbacks = []
    
    def add_data_callback(self, callback):
        """Add callback for flight data updates"""
        self.data_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start monitoring flight simulation data"""
        self.logger.info(f"Starting flight monitoring ({self.config.flight_sim_type})")
        self.running = True
        
        # For now, simulate flight data - real implementation would connect to X-Plane/MSFS
        await self._simulate_flight_loop()
    
    async def _simulate_flight_loop(self):
        """Simulate flight data for testing"""
        
        # Simulate a flight from Dublin to London
        flight_phases = ['ground', 'taxi', 'takeoff', 'climb', 'cruise', 'descent', 'approach', 'landing']
        current_phase_idx = 0
        altitude = 0
        speed = 0
        heading = 90  # East
        
        phase_durations = {
            'ground': 30, 'taxi': 60, 'takeoff': 10, 'climb': 120, 
            'cruise': 300, 'descent': 120, 'approach': 60, 'landing': 10
        }
        
        phase_start_time = datetime.now()
        
        while self.running:
            try:
                current_time = datetime.now()
                current_phase = flight_phases[current_phase_idx]
                
                # Update flight parameters based on phase
                if current_phase == 'ground':
                    altitude = 0
                    speed = 0
                elif current_phase == 'taxi':
                    altitude = 0
                    speed = 15
                elif current_phase == 'takeoff':
                    altitude = min(1000, altitude + 100)
                    speed = min(150, speed + 10)
                elif current_phase == 'climb':
                    altitude = min(35000, altitude + 200)
                    speed = min(400, speed + 5)
                elif current_phase == 'cruise':
                    altitude = 35000
                    speed = 450
                elif current_phase == 'descent':
                    altitude = max(3000, altitude - 200)
                    speed = max(250, speed - 5)
                elif current_phase == 'approach':
                    altitude = max(1000, altitude - 100)
                    speed = max(150, speed - 10)
                elif current_phase == 'landing':
                    altitude = max(0, altitude - 100)
                    speed = max(0, speed - 15)
                
                # Build flight data
                flight_data = {
                    'timestamp': current_time.isoformat(),
                    'callsign': 'EI-SIM',
                    'aircraft_type': 'B737',
                    'phase': current_phase,
                    'altitude': altitude,
                    'speed': speed,
                    'heading': heading,
                    'latitude': 53.4 + (current_phase_idx * 0.1),  # Rough Dublin to London
                    'longitude': -6.3 + (current_phase_idx * 0.2),
                    'traffic_count': current_phase_idx % 4,  # Vary traffic
                    'weather': 'clear',
                    'emergency': False
                }
                
                # Store current data
                self.current_data = flight_data
                
                # Notify callbacks
                for callback in self.data_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(flight_data)
                        else:
                            callback(flight_data)
                    except Exception as e:
                        self.logger.error(f"Error in data callback: {e}")
                
                # Check if should advance to next phase
                elapsed = (current_time - phase_start_time).total_seconds()
                if elapsed >= phase_durations.get(current_phase, 60):
                    if current_phase_idx < len(flight_phases) - 1:
                        current_phase_idx += 1
                        phase_start_time = current_time
                        self.logger.info(f"Flight phase changed to: {flight_phases[current_phase_idx]}")
                    else:
                        # Flight complete - restart
                        current_phase_idx = 0
                        phase_start_time = current_time
                        altitude = 0
                        speed = 0
                        self.logger.info("Flight completed - restarting simulation")
                
                await asyncio.sleep(self.config.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in flight monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def stop_monitoring(self):
        """Stop flight monitoring"""
        self.logger.info("Stopping flight monitoring")
        self.running = False
    
    def get_current_data(self) -> Dict[str, Any]:
        """Get current flight data"""
        return self.current_data.copy()

class CommentaryEngine:
    """Generate flight commentary using pronunciation and character systems"""
    
    def __init__(self, config: SimviatorConfig):
        self.config = config
        self.logger = logging.getLogger('CommentaryEngine')
        
        # Core systems
        self.pronunciation_engine = AviationPronunciationEngine()
        self.guidance_system = FlightGuidanceCharacterSystem()
        
        # Commentary callbacks
        self.commentary_callbacks = []
        
        # Add guidance callback
        self.guidance_system.add_guidance_callback(self._on_guidance_generated)
    
    def add_commentary_callback(self, callback):
        """Add callback for commentary output"""
        self.commentary_callbacks.append(callback)
    
    async def _on_guidance_generated(self, character_name: str, message: str):
        """Handle guidance from character system"""
        
        # Format as commentary
        commentary = {
            'timestamp': datetime.now().isoformat(),
            'type': 'guidance',
            'character': character_name,
            'message': message,
            'raw_message': message,
            'pronunciation_applied': True
        }
        
        # Notify callbacks
        for callback in self.commentary_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(commentary)
                else:
                    callback(commentary)
            except Exception as e:
                self.logger.error(f"Error in commentary callback: {e}")
    
    async def process_flight_data(self, flight_data: Dict[str, Any]):
        """Process flight data and generate commentary"""
        
        if not self.config.guidance_enabled:
            return
        
        # Pass to guidance system for character commentary
        await self.guidance_system.process_flight_situation(flight_data)
        
        # Could add other commentary types here (weather, navigation, etc.)
    
    async def generate_position_report(self, flight_data: Dict[str, Any]) -> str:
        """Generate properly pronounced position report"""
        
        lat = flight_data.get('latitude', 0)
        lon = flight_data.get('longitude', 0)
        alt = flight_data.get('altitude', 0)
        hdg = flight_data.get('heading', 0)
        
        return self.pronunciation_engine.format_position_report(lat, lon, alt, hdg)
    
    async def generate_traffic_call(self, callsign: str, aircraft_type: str, 
                                  distance: float, bearing: int, altitude_diff: int) -> str:
        """Generate properly pronounced traffic call"""
        
        return self.pronunciation_engine.format_traffic_call(
            callsign, aircraft_type, distance, bearing, altitude_diff)
    
    def get_guidance_status(self) -> Dict[str, Any]:
        """Get status of guidance character system"""
        return self.guidance_system.get_character_status()

class SimviatorService:
    """Main Simviator service"""
    
    def __init__(self, config: SimviatorConfig):
        self.config = config
        self.logger = logging.getLogger('SimviatorService')
        
        # Core components
        self.flight_monitor = FlightMonitor(config)
        self.commentary_engine = CommentaryEngine(config)
        
        # Service state
        self.running = False
        self.start_time = datetime.now()
        
        # Connect components
        self.flight_monitor.add_data_callback(self.commentary_engine.process_flight_data)
        self.commentary_engine.add_commentary_callback(self._on_commentary_generated)
        
        # Setup signal handling
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _on_commentary_generated(self, commentary: Dict[str, Any]):
        """Handle generated commentary"""
        
        # Log commentary
        char = commentary.get('character', 'System')
        msg = commentary.get('message', '')
        self.logger.info(f"[{char}] {msg}")
        
        # Could publish to event bus here for other services
        # await self.event_publisher.publish('simviator.commentary', commentary)
    
    async def start(self):
        """Start the Simviator service"""
        
        self.logger.info(f"Starting Simviator service on port {self.config.service_port}")
        self.logger.info(f"Configuration: {asdict(self.config)}")
        
        self.running = True
        
        # Start flight monitoring
        monitor_task = asyncio.create_task(self.flight_monitor.start_monitoring())
        
        try:
            # Keep service running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Service error: {e}")
        finally:
            # Clean shutdown
            self.flight_monitor.stop_monitoring()
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Simviator service stopped")
    
    def stop(self):
        """Stop the service"""
        self.logger.info("Stopping Simviator service...")
        self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        
        uptime = datetime.now() - self.start_time
        
        return {
            'service': self.config.service_name,
            'status': 'running' if self.running else 'stopped',
            'uptime_seconds': uptime.total_seconds(),
            'current_flight_data': self.flight_monitor.get_current_data(),
            'guidance_status': self.commentary_engine.get_guidance_status(),
            'config': asdict(self.config)
        }

def setup_logging(config: SimviatorConfig):
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

def load_config(config_file: Optional[str] = None) -> SimviatorConfig:
    """Load configuration from file or create default"""
    
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            return SimviatorConfig(**config_data)
        except Exception as e:
            print(f"Error loading config from {config_file}: {e}")
    
    # Return default config
    return SimviatorConfig()

def save_default_config(config_file: str):
    """Save default configuration to file"""
    
    config = SimviatorConfig()
    config_data = asdict(config)
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"Default configuration saved to {config_file}")

async def test_service():
    """Test the service components"""
    
    print("[SIMVIATOR] Testing Simviator Service Components")
    print("=" * 60)
    
    print("\n1. Testing Aviation Pronunciation Engine:")
    test_aviation_pronunciation()
    
    print("\n2. Testing Flight Guidance Character System:")
    await test_guidance_system()
    
    print("\n3. Testing Service Integration:")
    config = SimviatorConfig()
    config.update_interval = 0.5  # Faster for testing
    
    service = SimviatorService(config)
    
    # Start service for a short time
    start_task = asyncio.create_task(service.start())
    
    # Let it run for a few seconds
    await asyncio.sleep(10)
    
    # Stop service
    service.stop()
    await start_task
    
    print("\n[OK] Service test completed")

async def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Simviator Service - Flight Commentary System")
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
    service = SimviatorService(config)
    
    try:
        await service.start()
    except KeyboardInterrupt:
        print("\nService interrupted by user")
    except Exception as e:
        print(f"Service error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
