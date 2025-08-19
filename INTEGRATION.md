# Flight Simulator Integration Guide

This guide covers integrating Simviator microservices with real flight simulators for authentic aviation guidance and training.

## Overview

Simviator supports two primary flight simulator platforms:
- **X-Plane 11/12** (Easiest integration via UDP)
- **Microsoft Flight Simulator 2020** (Advanced integration via SimConnect)

## X-Plane Integration (Recommended for Beginners)

### Prerequisites
- X-Plane 11 or 12
- Network connectivity between X-Plane and Simviator services
- UDP port 49000 available (default)

### Step 1: Configure X-Plane Data Output

1. **Open X-Plane**
2. **Go to Settings → Data Input & Output**
3. **Enable the following data sets:**
   - **Row 3: Speeds** - Airspeed, ground speed, vertical speed
   - **Row 8: Joystick Ail/Elv/Rud** - Control surface positions
   - **Row 14: Gear/Flap/S-Brakes** - Landing gear and flap positions
   - **Row 17: Pitch, Roll, Headings** - Aircraft attitude
   - **Row 20: Latitude, Longitude, Altitude** - Position data
   - **Row 25: Throttle Command** - Engine power settings
   - **Row 26: Throttle Actual** - Actual engine parameters

4. **Set Network Configuration:**
   - IP Address: `127.0.0.1` (if running locally)
   - Port: `49000`
   - Rate: `20 Hz` (recommended for smooth data flow)

### Step 2: Update Simviator Service

Replace the simulated data connection in `services/simviator/main.py`:

```python
# Add to imports
import socket
import struct
from typing import Dict, Any

class XPlaneDataReceiver:
    """Receives and parses X-Plane UDP data."""
    
    def __init__(self, port: int = 49000):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.socket.settimeout(1.0)  # 1 second timeout
        
    def parse_data_packet(self, data: bytes) -> Dict[str, Any]:
        """Parse X-Plane data packet."""
        if len(data) < 5 or data[:4] != b'DATA':
            return {}
            
        flight_data = {}
        offset = 5  # Skip header
        
        while offset + 36 <= len(data):
            index = struct.unpack('<I', data[offset:offset+4])[0]
            values = struct.unpack('<8f', data[offset+4:offset+36])
            
            # Map data indices to flight parameters
            if index == 3:  # Speeds
                flight_data.update({
                    'airspeed': values[0],
                    'ground_speed': values[2],
                    'vertical_speed': values[1]
                })
            elif index == 17:  # Attitude
                flight_data.update({
                    'pitch': values[0],
                    'roll': values[1],
                    'heading': values[2]
                })
            elif index == 20:  # Position
                flight_data.update({
                    'latitude': values[0],
                    'longitude': values[1],
                    'altitude': values[2]
                })
            elif index == 14:  # Gear/Flaps
                flight_data.update({
                    'gear_position': values[0],
                    'flap_position': values[1]
                })
            elif index == 25:  # Throttle
                flight_data.update({
                    'throttle_1': values[0],
                    'throttle_2': values[1] if values[1] != -999.0 else None
                })
                
            offset += 36
            
        return flight_data
    
    def get_flight_data(self) -> Dict[str, Any]:
        """Get current flight data from X-Plane."""
        try:
            data, addr = self.socket.recvfrom(1024)
            return self.parse_data_packet(data)
        except socket.timeout:
            return {}
        except Exception as e:
            print(f"Error receiving X-Plane data: {e}")
            return {}

# Replace SimulatedFlightData class with:
class FlightDataManager:
    """Manages real or simulated flight data."""
    
    def __init__(self, use_xplane: bool = True):
        self.use_xplane = use_xplane
        if use_xplane:
            try:
                self.xplane_receiver = XPlaneDataReceiver()
                print("X-Plane integration enabled")
            except Exception as e:
                print(f"Failed to initialize X-Plane connection: {e}")
                self.use_xplane = False
        
        if not self.use_xplane:
            self.simulated_data = SimulatedFlightData()
            print("Using simulated flight data")
    
    def get_current_data(self) -> Dict[str, Any]:
        """Get current flight data."""
        if self.use_xplane:
            data = self.xplane_receiver.get_flight_data()
            if data:  # If we received valid data
                return data
            
        # Fallback to simulated data
        return self.simulated_data.get_current_data()
```

### Step 3: Test Integration

1. **Start X-Plane** with data output enabled
2. **Run Simviator services:**
   ```bash
   python launch_services.py
   ```
3. **Verify data flow:**
   ```bash
   curl http://localhost:8001/flight-data
   ```

### Step 4: Flight Phase Detection

The characters will automatically respond to real flight phases:

- **Pre-flight**: Aircraft on ground, engines off
- **Taxi**: Ground movement, low speed
- **Takeoff**: Increasing airspeed, positive climb rate
- **Climb**: Sustained positive vertical speed
- **Cruise**: Level flight, steady altitude
- **Descent**: Negative vertical speed
- **Approach**: Descending, gear/flaps extended
- **Landing**: Touchdown detection
- **Rollout**: Ground contact, decreasing speed

## Microsoft Flight Simulator Integration (Advanced)

### Prerequisites
- Microsoft Flight Simulator 2020
- SimConnect SDK installed
- Visual Studio Build Tools (for compilation)
- Python `pywin32` package

### Step 1: Install SimConnect SDK

1. **Download MSFS SDK** from Microsoft Developer Portal
2. **Install SDK** to default location (`C:\MSFS SDK`)
3. **Install Python dependencies:**
   ```bash
   pip install pywin32 comtypes
   ```

### Step 2: SimConnect Interface

Create `services/simviator/msfs_interface.py`:

```python
import ctypes
import ctypes.wintypes
from ctypes import wintypes, windll
import time
from typing import Dict, Any, Optional

class MSFSInterface:
    """Interface for Microsoft Flight Simulator via SimConnect."""
    
    def __init__(self):
        self.connected = False
        self.simconnect = None
        self._initialize_simconnect()
    
    def _initialize_simconnect(self):
        """Initialize SimConnect connection."""
        try:
            # Load SimConnect library
            self.simconnect = windll.LoadLibrary("C:\\MSFS SDK\\SimConnect SDK\\lib\\SimConnect.dll")
            
            # Define SimConnect functions
            self.simconnect.SimConnect_Open.argtypes = [
                ctypes.POINTER(ctypes.c_void_p),  # phSimConnect
                ctypes.c_char_p,                   # szName
                wintypes.HWND,                     # hWnd
                wintypes.DWORD,                    # UserEventWin32
                wintypes.HANDLE,                   # hEventHandle
                wintypes.DWORD                     # ConfigIndex
            ]
            
            # Open connection
            handle = ctypes.c_void_p()
            result = self.simconnect.SimConnect_Open(
                ctypes.byref(handle),
                b"Simviator",
                None, 0, None, 0
            )
            
            if result == 0:  # S_OK
                self.connection_handle = handle
                self.connected = True
                self._setup_data_requests()
                print("Connected to Microsoft Flight Simulator")
            else:
                print(f"Failed to connect to MSFS: Error {result}")
                
        except Exception as e:
            print(f"SimConnect initialization failed: {e}")
            self.connected = False
    
    def _setup_data_requests(self):
        """Set up data requests for flight parameters."""
        if not self.connected:
            return
            
        # Define data structure for flight data
        # This would include airspeed, altitude, heading, etc.
        # Implementation depends on specific SimConnect API usage
        pass
    
    def get_flight_data(self) -> Dict[str, Any]:
        """Get current flight data from MSFS."""
        if not self.connected:
            return {}
            
        # Request current data from SimConnect
        # Parse and return flight parameters
        # This is a simplified example - full implementation
        # would handle SimConnect message processing
        
        return {
            'airspeed': 0,
            'altitude': 0,
            'heading': 0,
            'vertical_speed': 0,
            # ... other parameters
        }
    
    def disconnect(self):
        """Close SimConnect connection."""
        if self.connected and self.simconnect:
            self.simconnect.SimConnect_Close(self.connection_handle)
            self.connected = False
```

### Step 3: Configure MSFS Integration

1. **Enable Developer Mode** in MSFS
2. **Start MSFS** and load a flight
3. **Update service configuration** in `config/orchestrator_example.json`:
   ```json
   {
     "flight_simulator": "msfs",
     "msfs_config": {
       "simconnect_port": 500,
       "update_rate": 10
     }
   }
   ```

### Step 4: Professional Features

MSFS integration enables advanced features:

- **Precise navigation guidance**
- **Real-time weather integration**
- **ATC communications simulation**
- **Emergency procedure training**
- **Instrument approach guidance**

## Environment Configuration

Add to your `.env` file:

```bash
# Flight Simulator Integration
FLIGHT_SIM_TYPE=xplane  # or 'msfs' or 'simulated'
XPLANE_UDP_PORT=49000
XPLANE_HOST=127.0.0.1
MSFS_SIMCONNECT_PORT=500

# Data Update Rates
FLIGHT_DATA_UPDATE_RATE=20  # Hz
CHARACTER_RESPONSE_RATE=2   # Hz

# Integration Features
ENABLE_REAL_WEATHER=true
ENABLE_ATC_SIMULATION=false
ENABLE_EMERGENCY_SCENARIOS=true
```

## Troubleshooting

### X-Plane Issues

**Problem**: No data received from X-Plane
- **Solution**: Verify data output settings and network configuration
- **Check**: Firewall settings allowing UDP traffic on port 49000

**Problem**: Intermittent data loss
- **Solution**: Reduce update rate to 10-15 Hz
- **Check**: Network stability and processing load

### MSFS Issues

**Problem**: SimConnect connection fails
- **Solution**: Ensure MSFS is running and Developer Mode is enabled
- **Check**: SimConnect SDK installation and path

**Problem**: Missing flight data
- **Solution**: Verify data request definitions match MSFS variables
- **Check**: SimConnect documentation for correct variable names

### General Issues

**Problem**: Character responses lag behind flight events
- **Solution**: Adjust `CHARACTER_RESPONSE_RATE` in configuration
- **Check**: Service performance and resource usage

**Problem**: Flight phase detection inaccurate
- **Solution**: Calibrate thresholds in flight phase detection logic
- **Check**: Data quality and update frequency

## Development Tips

1. **Start with X-Plane** - easier setup and debugging
2. **Use simulated mode** for development without flight simulator
3. **Monitor data flow** through service health endpoints
4. **Test with different aircraft** - each may have different characteristics
5. **Validate data ranges** - ensure realistic values for flight parameters

## Contributing

To add support for other simulators:

1. **Create interface class** following the pattern in `xplane_receiver.py`
2. **Implement data parsing** for simulator-specific formats
3. **Add configuration options** for new simulator
4. **Update flight phase detection** if needed
5. **Add integration tests** for new simulator support

For questions or contributions, see the main README.md file.
