# Contributing to Simviator Microservices

Thank you for your interest in contributing to this professional flight simulation enhancement system. Your contributions help make aviation simulation more immersive and educational for pilots, enthusiasts, and learners worldwide.

## Ways to Contribute

### Aviation Content Development
- **Character personalities** - Create new ATC controllers, pilots, or aviation personalities
- **Radio phraseology** - Improve ICAO standard communications and regional variations
- **Flight procedures** - Add realistic flight phase commentary and guidance
- **Regional specialisation** - Adapt characters for different countries and airspaces

### Technical Integration
- **Flight simulator support** - Add support for new simulators beyond X-Plane and MSFS
- **Bot platform integration** - Discord, Twitch, YouTube, or other streaming platforms
- **API development** - Enhance microservice coordination and communication
- **Performance optimisation** - Improve resource usage and response times

### Documentation and Examples
- **Integration guides** - Step-by-step setup for different flight simulators
- **Character development tutorials** - How to create authentic aviation personalities
- **Deployment documentation** - Docker, cloud, and scaling configurations
- **Aviation accuracy guides** - Ensuring realistic and educational content

### Testing and Quality Assurance
- **Flight scenario testing** - Real-world flight phase testing
- **Cross-platform compatibility** - Different operating systems and simulators
- **Performance testing** - Service coordination and resource usage
- **Aviation authenticity** - Ensuring realistic and educational content

## Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/simviator-microservices.git
   cd simviator-microservices
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Test the system**
   ```bash
   python launch_services.py --test
   python launch_services.py --all
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-contribution-name
   ```

### Development Standards

**Python Code Standards**
- Follow PEP 8 conventions
- Use type hints for function parameters and return values
- Include docstrings for all public functions and classes
- Keep microservice functions focused and modular

**Aviation Accuracy Standards**
- Use proper ICAO phraseology and terminology
- Research real-world procedures and communications
- Cite sources for aviation-specific content
- Maintain educational value and authenticity

**Documentation Standards**
- Document all public APIs and configuration options
- Include usage examples for new features
- Update README if adding major functionality
- Add inline comments for aviation-specific logic

## Character Development Guidelines

### Creating Aviation Personalities

1. **Research authentic backgrounds**
   ```python
   # Good: Based on real aviation roles and experience
   character = GuidanceCharacter(
       name="Tower Control Cork",
       background="10-year veteran at Cork Airport, handles mix of commercial and GA traffic",
       personality=GuidancePersonality.PROFESSIONAL_RELAXED,
       speech_patterns=["Right then {callsign}", "Grand job", "Safe travels"],
       expertise_areas=["approach_control", "irish_airspace", "weather_calls"],
       response_likelihood=0.8,
       professional_level=7
   )
   ```

2. **Maintain educational value**
   - Characters should teach proper radio procedures
   - Include realistic decision-making and prioritisation
   - Provide context for aviation procedures and safety

3. **Respect aviation culture**
   - Avoid stereotypes or unrealistic portrayals
   - Research regional differences in procedures and terminology
   - Maintain professionalism even in casual characters

### Character Testing
- Test with various flight phases (taxi, takeoff, cruise, approach, landing)
- Verify phrase patterns work naturally in different contexts
- Ensure educational content is accurate and helpful
- Test personality consistency across different scenarios

## Technical Contribution Guidelines

### Microservice Development

1. **Service independence**
   - Each service should function independently
   - Use proper API boundaries and contracts
   - Implement health checks and monitoring
   - Handle graceful shutdown and error recovery

2. **Aviation data integration**
   ```python
   # Flight data integration example
   class FlightDataConnector:
       def connect_xplane(self, host: str, port: int) -> bool:
           """Connect to X-Plane UDP data output"""
           # Implementation with proper error handling
           
       def parse_flight_phase(self, data: dict) -> FlightPhase:
           """Determine current flight phase from telemetry"""
           # Aviation-accurate phase detection
   ```

3. **Configuration management**
   - Use environment variables for sensitive data
   - Provide sensible defaults for all configuration
   - Document all configuration options
   - Support both development and production deployments

### Bot Platform Integration

1. **Platform-specific considerations**
   - Respect rate limits and API guidelines
   - Handle authentication securely
   - Implement proper error handling and retries
   - Support graceful degradation when platforms are unavailable

2. **Personality synchronisation**
   - Ensure character personalities work across platforms
   - Adapt communication style to platform constraints
   - Maintain educational value in all formats

### Code Contribution Process

### For Bug Fixes
1. Create an issue describing the bug with aviation context
2. Create a branch: `bugfix/aviation-issue-description`
3. Implement the fix with tests
4. Test with realistic flight scenarios
5. Submit a pull request referencing the issue

### For New Features
1. Create an issue discussing the proposed feature
2. Include aviation use cases and educational value
3. Wait for maintainer feedback before implementation
4. Create a branch: `feature/aviation-feature-description`
5. Implement with documentation and tests
6. Submit a pull request with comprehensive description

### For Character/Content Additions
1. Research the aviation background thoroughly
2. Test character interactions in multiple scenarios
3. Ensure educational accuracy and value
4. Include source citations for aviation procedures
5. Submit with usage examples and testing results

### Pull Request Guidelines

**Title and Description**
- Use clear, aviation-focused titles
- Explain the aviation problem being solved
- List any changes to character behaviour or procedures
- Include testing with flight scenarios

**Aviation Quality**
- All aviation content verified for accuracy
- Characters maintain educational value
- Procedures follow ICAO standards where applicable
- Regional variations properly researched and documented

**Technical Quality**
- All tests pass including aviation scenario tests
- Services start and coordinate properly
- Documentation updated appropriately
- Code follows project conventions

## Aviation Research and Accuracy

### Reliable Sources
- **ICAO Standards** - International procedures and phraseology
- **National AIP (Aeronautical Information Publication)** - Country-specific procedures
- **Aviation Training Materials** - Educational resources from flight schools
- **Real Pilot/Controller Experience** - Community feedback and expertise

### Verification Process
- Cross-reference aviation content with multiple sources
- Test with real pilots and controllers when possible
- Maintain bibliography of aviation sources used
- Update content when procedures or standards change

## Reporting Issues

### Bug Reports
- Include flight simulator and version information
- Provide flight scenario that triggers the issue
- Include character responses and expected behaviour
- Specify aviation accuracy concerns if applicable

### Aviation Accuracy Issues
- Cite authoritative sources for correct procedures
- Explain the educational impact of the inaccuracy
- Provide specific examples and context
- Suggest improvements or corrections

### Feature Requests
- Describe the aviation use case or scenario
- Explain the educational or training value
- Consider implementation complexity
- Provide examples from real aviation environments

## Contributor License Agreement

By contributing to this project, you agree that:

1. **You retain copyright** to your contributions
2. **You grant permission** for your contributions to be included in both free (academic/research/personal) and commercial versions of the software
3. **You understand** that your contributions will be subject to the project's dual licensing model
4. **You confirm** that any aviation content is accurate and educational
5. **You accept** that commercial licensing revenue is not shared with contributors

For significant contributions (major features, character systems, integration modules), separate licensing arrangements may be negotiated.

### Special Provisions for Aviation Content
- Character personalities and commentary may be freely used by end users
- Aviation procedures and educational content remain under project license
- You may retain credit for original character creation and aviation research

## Commercial Use and Licensing

This project uses dual licensing:
- **Free for academic, research, personal flight simulation, and aviation education**
- **Commercial use requires paid licensing**

Commercial licensing enquiries: c42meitheal@gmail.com

### Why This Approach?
- Ensures the system remains available for aviation education and training
- Provides sustainable funding for continued development and aviation accuracy
- Allows commercial flight training organisations to use the system with proper licensing
- Protects the intellectual property whilst encouraging aviation education

## Recognition

Contributors are recognised in:
- Project acknowledgments with aviation credentials
- Release notes for significant contributions
- Character creator credits in the system
- Special recognition for aviation accuracy improvements

## Getting Help

- **Documentation**: Start with README and INTEGRATION.md
- **Aviation Questions**: Cite sources and include use cases
- **Technical Issues**: Check existing issues before creating new ones
- **Direct Contact**: c42meitheal@gmail.com for licensing or major contributions

## Code of Conduct

We are committed to providing a welcoming environment for aviation enthusiasts, developers, and educators:
- Maintain professionalism reflecting aviation industry standards
- Respect diverse aviation backgrounds and experience levels
- Focus on educational value and accuracy
- Help newcomers to both aviation and development
- Be constructive in all feedback and discussions

## Long-term Vision

This project aims to:
- **Enhance aviation education** - Make flight simulation more educational and realistic
- **Support pilot training** - Provide cost-effective alternatives to expensive training systems  
- **Preserve aviation culture** - Maintain authentic procedures and communications
- **Enable accessibility** - Make aviation education available to diverse learners
- **Build sustainably** - Balance open source values with commercial viability for aviation industry

Your contributions help achieve these goals and benefit the entire aviation simulation and education community.

Thank you for contributing to better, more educational flight simulation experiences!
