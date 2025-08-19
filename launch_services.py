#!/usr/bin/env python3
"""
Service Launcher - Start Simviator Microservices

Simple launcher for the microservice architecture:
- Orchestrator (port 8000) - Service coordination
- Simviator (port 8001) - Flight commentary system  
- Bot Control (port 8002) - Discord/Twitch integration

Usage:
    python launch_services.py --all                # Start all services
    python launch_services.py --service simviator  # Start specific service
    python launch_services.py --test               # Test services
"""

import asyncio
import subprocess
import sys
import signal
import time
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class ServiceLauncher:
    """Launch and manage microservices"""
    
    def __init__(self):
        self.services_dir = Path(__file__).parent / 'services'
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = True
        
        # Service definitions
        self.services = {
            'orchestrator': {
                'path': self.services_dir / 'orchestrator',
                'script': 'main.py',
                'port': 8000,
                'required': True,
                'dependencies': []
            },
            'simviator': {
                'path': self.services_dir / 'simviator', 
                'script': 'main.py',
                'port': 8001,
                'required': True,
                'dependencies': []
            },
            'bot_control': {
                'path': self.services_dir / 'bot_control',
                'script': 'main.py', 
                'port': 8002,
                'required': False,
                'dependencies': ['simviator']
            }
        }
        
        # Setup signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down services...")
        self.running = False
    
    async def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        
        if service_name not in self.services:
            print(f"[ERROR] Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        service_path = service['path']
        script_path = service_path / service['script']
        
        if not script_path.exists():
            print(f"[ERROR] Service script not found: {script_path}")
            return False
        
        print(f"[START] Starting {service_name} service on port {service['port']}...")
        
        try:
            # Start service process
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(service_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = process
            
            # Give service time to start
            await asyncio.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"[OK] {service_name} service started (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"[ERROR] {service_name} service failed to start")
                if stdout:
                    print(f"STDOUT: {stdout}")
                if stderr:
                    print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error starting {service_name}: {e}")
            return False
    
    async def stop_service(self, service_name: str):
        """Stop a specific service"""
        
        if service_name in self.processes:
            process = self.processes[service_name]
            
            print(f"[STOP] Stopping {service_name} service...")
            
            try:
                # Try graceful shutdown first
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    print(f"[OK] {service_name} service stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    process.kill()
                    process.wait()
                    print(f"[WARN] {service_name} service force-killed")
                    
            except Exception as e:
                print(f"[ERROR] Error stopping {service_name}: {e}")
            finally:
                del self.processes[service_name]
    
    async def start_all_services(self):
        """Start all services in dependency order"""
        
        print("[LAUNCH] Starting Simviator Microservices")
        print("=" * 50)
        
        # Start services in dependency order
        start_order = ['orchestrator', 'simviator', 'bot_control']
        
        for service_name in start_order:
            service = self.services[service_name]
            
            # Check dependencies
            for dep in service['dependencies']:
                if dep not in self.processes:
                    print(f"[WARN] Dependency {dep} not running for {service_name}")
                    if service['required']:
                        continue
            
            success = await self.start_service(service_name)
            
            if not success and service['required']:
                print(f"[ERROR] Required service {service_name} failed to start")
                return False
        
        print("\n[INFO] Services started. Monitoring...")
        return True
    
    async def stop_all_services(self):
        """Stop all services"""
        
        print("\n[STOP] Stopping all services...")
        
        # Stop in reverse order
        service_names = list(self.processes.keys())
        service_names.reverse()
        
        for service_name in service_names:
            await self.stop_service(service_name)
    
    async def monitor_services(self):
        """Monitor running services"""
        
        while self.running and self.processes:
            for service_name, process in list(self.processes.items()):
                if process.poll() is not None:
                    # Service has stopped
                    stdout, stderr = process.communicate()
                    print(f"[DEAD] {service_name} service stopped unexpectedly")
                    if stderr:
                        print(f"Error: {stderr}")
                    
                    del self.processes[service_name]
                    
                    # Attempt restart if required
                    service = self.services[service_name]
                    if service['required']:
                        print(f"[RESTART] Attempting to restart {service_name}...")
                        await self.start_service(service_name)
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    async def test_services(self):
        """Test individual services"""
        
        print("[TEST] Testing Simviator Services")
        print("=" * 40)
        
        # Test each service individually
        for service_name, service in self.services.items():
            print(f"\n[SERVICE] Testing {service_name} service:")
            
            service_path = service['path']
            script_path = service_path / service['script']
            
            if not script_path.exists():
                print(f"   [ERROR] Script not found: {script_path}")
                continue
            
            try:
                # Run service in test mode
                result = subprocess.run(
                    [sys.executable, str(script_path), '--test'],
                    cwd=str(service_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"   [OK] {service_name} test passed")
                    if result.stdout:
                        # Show last few lines of output
                        lines = result.stdout.strip().split('\n')
                        for line in lines[-3:]:
                            print(f"   [OUT] {line}")
                else:
                    print(f"   [ERROR] {service_name} test failed (code {result.returncode})")
                    if result.stderr:
                        print(f"   Error: {result.stderr}")
                        
            except subprocess.TimeoutExpired:
                print(f"   [TIMEOUT] {service_name} test timed out")
            except Exception as e:
                print(f"   [ERROR] {service_name} test error: {e}")
        
        print("\n[COMPLETE] Service testing completed")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        
        status = {
            'total_services': len(self.services),
            'running_services': len(self.processes),
            'service_details': {}
        }
        
        for service_name, service in self.services.items():
            is_running = service_name in self.processes
            process = self.processes.get(service_name)
            
            status['service_details'][service_name] = {
                'running': is_running,
                'port': service['port'],
                'required': service['required'],
                'pid': process.pid if process else None,
                'path': str(service['path'])
            }
        
        return status
    
    async def run_interactive(self):
        """Run in interactive mode"""
        
        print("[MANAGER] Simviator Service Manager")
        print("=" * 40)
        print("Commands:")
        print("  start <service>  - Start specific service")
        print("  stop <service>   - Stop specific service")
        print("  restart <service>- Restart specific service")
        print("  status          - Show service status")
        print("  test            - Test services")
        print("  quit            - Exit")
        print()
        
        while self.running:
            try:
                command = input("simviator> ").strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    break
                elif cmd == 'start' and len(command) > 1:
                    await self.start_service(command[1])
                elif cmd == 'stop' and len(command) > 1:
                    await self.stop_service(command[1])
                elif cmd == 'restart' and len(command) > 1:
                    await self.stop_service(command[1])
                    await asyncio.sleep(2)
                    await self.start_service(command[1])
                elif cmd == 'status':
                    status = self.get_service_status()
                    print(f"Services: {status['running_services']}/{status['total_services']} running")
                    for name, details in status['service_details'].items():
                        status_icon = "[RUNNING]" if details['running'] else "[STOPPED]"
                        print(f"  {status_icon} {name} (port {details['port']})")
                elif cmd == 'test':
                    await self.test_services()
                else:
                    print("Unknown command. Try: start, stop, restart, status, test, quit")
                    
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                print(f"Command error: {e}")
        
        await self.stop_all_services()

async def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Simviator Service Launcher")
    parser.add_argument('--all', action='store_true', help='Start all services')
    parser.add_argument('--service', help='Start specific service')
    parser.add_argument('--test', action='store_true', help='Test services')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--stop', action='store_true', help='Stop all services')
    
    args = parser.parse_args()
    
    launcher = ServiceLauncher()
    
    try:
        if args.test:
            await launcher.test_services()
        elif args.service:
            success = await launcher.start_service(args.service)
            if success:
                await launcher.monitor_services()
        elif args.all:
            success = await launcher.start_all_services()
            if success:
                await launcher.monitor_services()
        elif args.interactive:
            await launcher.run_interactive()
        elif args.stop:
            await launcher.stop_all_services()
        else:
            # Default: interactive mode
            await launcher.run_interactive()
            
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    finally:
        await launcher.stop_all_services()
        print("[COMPLETE] Service launcher stopped")

if __name__ == "__main__":
    asyncio.run(main())
