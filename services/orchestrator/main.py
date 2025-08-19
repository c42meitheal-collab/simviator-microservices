#!/usr/bin/env python3
"""
Orchestrator Service - Coordination and Event Management

A service for coordinating multiple microservices:
- Service health monitoring
- Event routing between services
- Unified configuration management
- Cross-service coordination

Architecture: Orchestrator for Simviator + Bot Control ecosystem
Dependencies: HTTP clients, event bus (Redis/NATS optional)
"""

import asyncio
import logging
import json
import signal
import sys
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse

@dataclass
class ServiceEndpoint:
    """Configuration for a managed service"""
    name: str
    url: str
    health_endpoint: str = "/health"
    required: bool = True
    restart_attempts: int = 3
    restart_delay: float = 5.0

@dataclass
class OrchestratorConfig:
    """Configuration for Orchestrator service"""
    service_name: str = "orchestrator"
    service_port: int = 8000
    
    # Managed services
    services: List[ServiceEndpoint] = None
    
    # Health monitoring
    health_check_interval: float = 10.0
    health_timeout: float = 5.0
    
    # Event management
    event_bus_enabled: bool = False
    event_bus_url: str = "redis://localhost:6379"
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    def __post_init__(self):
        if self.services is None:
            self.services = [
                ServiceEndpoint(
                    name="simviator",
                    url="http://localhost:8001",
                    health_endpoint="/health",
                    required=True
                ),
                ServiceEndpoint(
                    name="bot_control", 
                    url="http://localhost:8002",
                    health_endpoint="/health",
                    required=False
                )
            ]

class ServiceHealthMonitor:
    """Monitor health of registered services"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.logger = logging.getLogger('ServiceHealthMonitor')
        
        # Service state tracking
        self.service_states: Dict[str, Dict[str, Any]] = {}
        self.health_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        
        # HTTP session for health checks
        self.session: Optional[aiohttp.ClientSession] = None
        self.monitoring = False
        
        # Initialize service states
        for service in config.services:
            self.service_states[service.name] = {
                'status': 'unknown',
                'last_check': None,
                'last_success': None,
                'consecutive_failures': 0,
                'total_checks': 0,
                'total_failures': 0,
                'response_time_ms': 0
            }
    
    def add_health_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Add callback for health state changes"""
        self.health_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start health monitoring"""
        
        self.logger.info("Starting service health monitoring")
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.health_timeout)
        )
        self.monitoring = True
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        
        self.logger.info("Stopping service health monitoring")
        self.monitoring = False
        
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _monitoring_loop(self):
        """Main health monitoring loop"""
        
        while self.monitoring:
            try:
                # Check all services
                for service in self.config.services:
                    await self._check_service_health(service)
                
                # Wait before next check
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _check_service_health(self, service: ServiceEndpoint):
        """Check health of a specific service"""
        
        service_name = service.name
        state = self.service_states[service_name]
        
        check_start = datetime.now()
        state['last_check'] = check_start
        state['total_checks'] += 1
        
        try:
            # Make health check request
            health_url = f"{service.url.rstrip('/')}{service.health_endpoint}"
            
            async with self.session.get(health_url) as response:
                response_time = (datetime.now() - check_start).total_seconds() * 1000
                state['response_time_ms'] = response_time
                
                if response.status == 200:
                    # Health check successful
                    old_status = state['status']
                    state['status'] = 'healthy'
                    state['last_success'] = check_start
                    state['consecutive_failures'] = 0
                    
                    if old_status != 'healthy':
                        self.logger.info(f"Service {service_name} is now healthy")
                        await self._notify_health_change(service_name, state)
                
                else:
                    # HTTP error response
                    await self._handle_health_failure(service, f"HTTP {response.status}")
        
        except asyncio.TimeoutError:
            await self._handle_health_failure(service, "timeout")
        except aiohttp.ClientError as e:
            await self._handle_health_failure(service, f"connection error: {e}")
        except Exception as e:
            await self._handle_health_failure(service, f"unexpected error: {e}")
    
    async def _handle_health_failure(self, service: ServiceEndpoint, error: str):
        """Handle health check failure"""
        
        service_name = service.name
        state = self.service_states[service_name]
        
        old_status = state['status']
        state['consecutive_failures'] += 1
        state['total_failures'] += 1
        state['status'] = 'unhealthy'
        
        self.logger.warning(f"Health check failed for {service_name}: {error} "
                           f"(consecutive failures: {state['consecutive_failures']})")
        
        if old_status != 'unhealthy':
            await self._notify_health_change(service_name, state)
    
    async def _notify_health_change(self, service_name: str, state: Dict[str, Any]):
        """Notify callbacks of health state change"""
        
        for callback in self.health_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(service_name, state.copy())
                else:
                    callback(service_name, state.copy())
            except Exception as e:
                self.logger.error(f"Error in health callback: {e}")
    
    def get_service_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of all services"""
        return {name: state.copy() for name, state in self.service_states.items()}
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall health summary"""
        
        total_services = len(self.service_states)
        healthy_services = sum(1 for state in self.service_states.values() 
                             if state['status'] == 'healthy')
        
        # Check if any required services are unhealthy
        required_unhealthy = []
        for service in self.config.services:
            if service.required and self.service_states[service.name]['status'] != 'healthy':
                required_unhealthy.append(service.name)
        
        overall_status = 'healthy' if not required_unhealthy else 'degraded'
        if healthy_services == 0:
            overall_status = 'critical'
        
        return {
            'overall_status': overall_status,
            'total_services': total_services,
            'healthy_services': healthy_services,
            'unhealthy_services': total_services - healthy_services,
            'required_unhealthy': required_unhealthy,
            'last_check': max((state['last_check'] for state in self.service_states.values() 
                             if state['last_check']), default=None)
        }

class EventCoordinator:
    """Coordinate events between services"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.logger = logging.getLogger('EventCoordinator')
        
        # Event routing rules
        self.event_routes: Dict[str, List[str]] = {
            # Simviator events -> Bot Control
            'simviator.flight.phase_changed': ['bot_control'],
            'simviator.commentary.generated': ['bot_control'],
            'simviator.emergency.declared': ['bot_control'],
            
            # Bot Control events -> Simviator
            'bot_control.personality.changed': ['simviator'],
            'bot_control.command.received': ['simviator'],
        }
        
        # Event history for debugging
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    async def publish_event(self, event_type: str, data: Dict[str, Any], source_service: str):
        """Publish an event to relevant services"""
        
        event = {
            'type': event_type,
            'data': data,
            'source': source_service,
            'timestamp': datetime.now().isoformat(),
            'id': f"{source_service}_{int(datetime.now().timestamp())}"
        }
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Route to target services
        target_services = self.event_routes.get(event_type, [])
        
        if target_services:
            self.logger.info(f"Routing event {event_type} from {source_service} to {target_services}")
            
            for target_service in target_services:
                await self._deliver_event(target_service, event)
        else:
            self.logger.debug(f"No routing rules for event type: {event_type}")
    
    async def _deliver_event(self, target_service: str, event: Dict[str, Any]):
        """Deliver event to target service"""
        
        # Find service endpoint
        service_endpoint = None
        for service in self.config.services:
            if service.name == target_service:
                service_endpoint = service
                break
        
        if not service_endpoint:
            self.logger.error(f"Unknown target service: {target_service}")
            return
        
        try:
            # In a real implementation, this would:
            # 1. POST to service's event endpoint
            # 2. Or publish to message queue
            # 3. Handle delivery confirmation
            
            self.logger.debug(f"Event delivered to {target_service}: {event['type']}")
            
        except Exception as e:
            self.logger.error(f"Failed to deliver event to {target_service}: {e}")
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event routing statistics"""
        
        total_events = len(self.event_history)
        
        # Count events by type
        event_types = {}
        source_services = {}
        
        for event in self.event_history:
            event_type = event['type']
            source = event['source']
            
            event_types[event_type] = event_types.get(event_type, 0) + 1
            source_services[source] = source_services.get(source, 0) + 1
        
        return {
            'total_events': total_events,
            'event_types': event_types,
            'source_services': source_services,
            'routing_rules': len(self.event_routes),
            'recent_events': self.event_history[-10:]  # Last 10 events
        }

class OrchestratorService:
    """Main Orchestrator service"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.logger = logging.getLogger('OrchestratorService')
        
        # Core components
        self.health_monitor = ServiceHealthMonitor(config)
        self.event_coordinator = EventCoordinator(config)
        
        # Service state
        self.running = False
        self.start_time = datetime.now()
        
        # Setup health monitoring callbacks
        self.health_monitor.add_health_callback(self._on_service_health_change)
        
        # Setup signal handling
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _on_service_health_change(self, service_name: str, state: Dict[str, Any]):
        """Handle service health state changes"""
        
        status = state['status']
        self.logger.info(f"Service {service_name} health changed to: {status}")
        
        # Could trigger alerts, restart attempts, etc.
        if status == 'unhealthy':
            consecutive_failures = state['consecutive_failures']
            if consecutive_failures >= 3:
                self.logger.warning(f"Service {service_name} has failed {consecutive_failures} consecutive health checks")
    
    async def start(self):
        """Start the Orchestrator service"""
        
        self.logger.info(f"Starting Orchestrator service on port {self.config.service_port}")
        self.logger.info(f"Managing services: {[s.name for s in self.config.services]}")
        
        self.running = True
        
        # Start health monitoring
        await self.health_monitor.start_monitoring()
        
        # Start coordination loop
        coordination_task = asyncio.create_task(self._coordination_loop())
        
        try:
            # Keep service running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Service error: {e}")
        finally:
            # Clean shutdown
            await self.health_monitor.stop_monitoring()
            coordination_task.cancel()
            try:
                await coordination_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Orchestrator service stopped")
    
    async def _coordination_loop(self):
        """Main coordination loop"""
        
        while self.running:
            try:
                # Perform periodic coordination tasks
                await self._check_service_coordination()
                
                # Wait before next coordination cycle
                await asyncio.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(10)
    
    async def _check_service_coordination(self):
        """Check if services need coordination"""
        
        overall_health = self.health_monitor.get_overall_health()
        
        if overall_health['overall_status'] == 'healthy':
            # All services healthy - could trigger optimization events
            pass
        elif overall_health['overall_status'] == 'degraded':
            # Some services unhealthy - could trigger fallback modes
            self.logger.warning(f"System degraded: {overall_health['required_unhealthy']} services unavailable")
        elif overall_health['overall_status'] == 'critical':
            # Critical situation - could trigger emergency procedures
            self.logger.error("System critical: No healthy services")
    
    def stop(self):
        """Stop the service"""
        self.logger.info("Stopping Orchestrator service...")
        self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        uptime = datetime.now() - self.start_time
        
        return {
            'service': self.config.service_name,
            'status': 'running' if self.running else 'stopped',
            'uptime_seconds': uptime.total_seconds(),
            'managed_services': [s.name for s in self.config.services],
            'health_summary': self.health_monitor.get_overall_health(),
            'service_states': self.health_monitor.get_service_states(),
            'event_statistics': self.event_coordinator.get_event_statistics(),
            'config': asdict(self.config)
        }

def setup_logging(config: OrchestratorConfig):
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

def load_config(config_file: Optional[str] = None) -> OrchestratorConfig:
    """Load configuration from file or create default"""
    
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Convert service configs to ServiceEndpoint objects
            if 'services' in config_data:
                services = []
                for service_data in config_data['services']:
                    services.append(ServiceEndpoint(**service_data))
                config_data['services'] = services
            
            return OrchestratorConfig(**config_data)
        except Exception as e:
            print(f"Error loading config from {config_file}: {e}")
    
    # Return default config
    return OrchestratorConfig()

def save_default_config(config_file: str):
    """Save default configuration to file"""
    
    config = OrchestratorConfig()
    config_data = asdict(config)
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"Default configuration saved to {config_file}")

async def test_service():
    """Test the orchestrator service components"""
    
    print("[ORCHESTRATOR] Testing Orchestrator Service Components")
    print("=" * 60)
    
    print("\n1. Testing Service Health Monitor:")
    config = OrchestratorConfig()
    health_monitor = ServiceHealthMonitor(config)
    
    print(f"   Monitoring {len(config.services)} services:")
    for service in config.services:
        print(f"     - {service.name} ({service.url})")
    
    print("\n2. Testing Event Coordinator:")
    event_coordinator = EventCoordinator(config)
    
    # Simulate some events
    await event_coordinator.publish_event(
        'simviator.flight.phase_changed', 
        {'from': 'climb', 'to': 'cruise'}, 
        'simviator'
    )
    
    stats = event_coordinator.get_event_statistics()
    print(f"   Event statistics: {stats['total_events']} events processed")
    
    print("\n3. Testing Full Service:")
    orchestrator = OrchestratorService(config)
    
    # Start service for a brief test
    start_task = asyncio.create_task(orchestrator.start())
    
    # Let it run briefly
    await asyncio.sleep(5)
    
    # Get status
    status = orchestrator.get_status()
    print(f"   Service status: {status['status']}")
    print(f"   Health summary: {status['health_summary']['overall_status']}")
    print(f"   Services monitored: {len(status['service_states'])}")
    
    # Stop service
    orchestrator.stop()
    await start_task
    
    print("\n[OK] Orchestrator Service test completed")

async def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Orchestrator Service - Microservice Coordination")
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
    service = OrchestratorService(config)
    
    try:
        await service.start()
    except KeyboardInterrupt:
        print("\nService interrupted by user")
    except Exception as e:
        print(f"Service error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
