# Simviator Microservices

Professional flight simulation enhancement system built as microservices. Provides real-time aviation commentary, character-driven guidance, and multi-platform bot integration for X-Plane, MSFS, and other flight simulators.

## 🎯 What It Does

Simviator transforms flight simulation from a solo technical exercise into an immersive, educational aviation experience with:

- **Professional Aviation Commentary** - Real-time ATC-style guidance using ICAO standards
- **Character-Driven Experience** - Bored Dublin Control, veteran pilots, aviation enthusiasts
- **Multi-Platform Integration** - Discord bots, Twitch chat, streaming overlays
- **Educational Focus** - Learn proper radio phraseology and aviation procedures
- **Flight Sim Ready** - Designed for X-Plane and MSFS integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ORCHESTRATOR  │    │    SIMVIATOR    │    │   BOT CONTROL   │
│   (Port 8000)   │    │   (Port 8001)   │    │   (Port 8002)   │
│                 │    │                 │    │                 │
│ • Health Monitor│◄──►│ • Aviation Eng. │◄──►│ • Discord Bots  │
│ • Event Router  │    │ • Character Sys.│    │ • Twitch Bots   │
│ • Service Coord │    │ • Flight Monitor│    │ • Personalities │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Three focused microservices:**
- **Orchestrator** - Service coordination, health monitoring, event routing
- **Simviator** - Aviation commentary engine with character personalities  
- **Bot Control** - Multi-platform bot management and personality sync

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/simviator-microservices.git
cd simviator-microservices
pip install -r requirements.txt
```

### 2. Test the System
```bash
python launch_services.py --test
```

### 3. Start All Services
```bash
python launch_services.py --all
```

### 4. Watch the Magic
Services will simulate a Dublin → London flight with professional aviation commentary:

```
[Dublin Control]: Right then EI-SIM, passing One Five Thousand feet, continue climb
[Captain Murphy]: Pro tip EI-SIM - this altitude works well for this route
[Approach Control]: EI-SIM, traffic advisory, maintain separation
```

## 💻 Current State

**Working Now:**
- ✅ Complete microservice architecture
- ✅ Aviation pronunciation engine (ICAO standards)
- ✅ Character system with authentic personalities
- ✅ Service orchestration and health monitoring
- ✅ Simulated flight data with realistic phase progression
- ✅ Professional logging and configuration management

**Ready for Integration:**
- ✅ X-Plane UDP connection framework
- ✅ MSFS SimConnect architecture
- ✅ Discord/Twitch bot scaffolding
- ✅ Event-driven coordination system

## 🛩️ Flight Simulator Integration

### X-Plane (Easiest)
1. Enable UDP output in X-Plane (Data Input & Output)
2. Replace simulated data connection in `services/simviator/main.py`
3. Characters respond to real flight phases automatically

### MSFS (More Complex)
1. Install SimConnect SDK
2. Configure MSFS interface
3. Professional aviation guidance for real flights

See [INTEGRATION.md](docs/INTEGRATION.md) for detailed setup instructions.

## 🎭 Characters

**Dublin Control** - *Professional but world-weary*
- 20-year veteran controller, seen everything twice
- "*sigh* Right then EI-SIM, nothing I haven't seen before..."

**Captain Murphy** - *Veteran pilot with stories*
- Retired Aer Lingus captain, 35 years commercial aviation  
- "In my day, we'd handle that by... Pro tip - watch out for..."

**Sarah (Aviation Enthusiast)** - *Excited aircraft spotter*
- Aviation YouTuber with endless trivia
- "Oh wow, look at that! Did you know that aircraft type..."

**Approach Control** - *Busy but competent*
- Multiple aircraft, efficient communication
- "Quick one EI-SIM - traffic twelve o'clock, monitor"

## 🔧 Service Management

### Interactive Mode
```bash
python launch_services.py --interactive
```

Commands:
- `start simviator` - Start specific service
- `stop orchestrator` - Stop specific service  
- `status` - Show all service status
- `test` - Run service tests
- `quit` - Exit gracefully

### Individual Services
```bash
# Start just the aviation commentary
python services/simviator/main.py

# Test specific service
python services/orchestrator/main.py --test

# Custom configuration
python services/bot_control/main.py --config my_config.json
```

## 📁 Project Structure

```
simviator-microservices/
├── launch_services.py          # Service launcher
├── requirements.txt            # Dependencies
├── README.md                  # This file
│
├── services/
│   ├── orchestrator/          # Service coordination
│   │   └── main.py
│   ├── simviator/             # Aviation commentary engine
│   │   ├── main.py
│   │   ├── aviation_pronunciation.py
│   │   └── flight_guidance_character.py
│   └── bot_control/           # Multi-platform bots
│       └── main.py
│
├── config/                    # Configuration examples
├── docs/                      # Documentation
└── tests/                     # Test files
```

## 🔌 Integration with AI Overlord

This microservice architecture integrates seamlessly with AI Overlord bot control panels:

```python
# AI Overlord discovers and manages Simviator services
services = await ai_overlord.discover_services("http://localhost:8000")
await ai_overlord.coordinate_flight_session({
    'services': ['simviator', 'discord_bot', 'stream_overlay'],
    'personality': 'educational_instructor'
})
```

## 🎯 Use Cases

**Personal Flight Simulation**
- Professional aviation guidance during flight
- Learn proper radio phraseology
- Realistic ATC-style commentary

**Content Creation**
- Stream with professional aviation commentary
- Discord community integration
- Educational aviation content

**Flight Training**
- Cost-effective alternative to premium ATC services
- Character-driven learning experiences
- Progressive difficulty based on user skill

## 🛠️ Development

### Adding New Characters
```python
# In services/simviator/flight_guidance_character.py
self.characters["new_character"] = GuidanceCharacter(
    name="New Character",
    personality=GuidancePersonality.CUSTOM,
    speech_patterns=["Custom phrase patterns..."],
    expertise_areas=["specific_expertise"],
    response_likelihood=0.7,
    professional_level=8
)
```

### Extending Flight Sim Support
1. Add new connector in `services/simviator/main.py`
2. Implement flight data parsing
3. Characters automatically adapt to real flight phases

### Adding Bot Platforms
1. Extend `services/bot_control/main.py`
2. Add new bot implementation
3. Leverage existing personality system

## 📊 Performance

- **Minimal Dependencies** - Core services need only `aiohttp`
- **Low Resource Usage** - Template-based characters, no ML inference
- **Scalable Architecture** - Independent services, horizontal scaling ready
- **Fast Startup** - Services operational in seconds

## 🐛 Troubleshooting

**Services won't start:**
```bash
# Check dependencies
pip install -r requirements.txt

# Test individual services
python services/simviator/main.py --test
```

**No commentary generated:**
- Check service logs for errors
- Verify character probability settings
- Test with `force_character_guidance()` method

**Integration issues:**
- Verify port availability (8000, 8001, 8002)
- Check firewall settings
- Review service health monitoring

## 📝 License

MIT License - feel free to use, modify, and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/simviator-microservices/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/simviator-microservices/discussions)
- **Email**: [your.email@domain.com](mailto:your.email@domain.com)

---

**Ready for professional flight simulation enhancement!** 🛩️

*Transform your flight sim from technical exercise to immersive aviation experience with authentic character-driven guidance and professional commentary.*
