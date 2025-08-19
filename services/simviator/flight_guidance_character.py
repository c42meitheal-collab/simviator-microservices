#!/usr/bin/env python3
"""
[SIMVIATOR] Simviator Flight Guidance Character System
A sophisticated "guidance" system that provides professional flight assistance
positioned as educational support rather than formal ATC services.

Features:
- Bored/harried ATC controller character with authentic personality
- Real-time traffic awareness and conflict resolution
- Professional phraseology with character quirks
- Cost-effective alternative to premium ATC services
- Adapts consciousness council into passenger characters
- Educational positioning (not competing with paid ATC)
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from aviation_pronunciation import AviationPronunciationEngine

class GuidancePersonality(Enum):
    """Flight guidance character personalities"""
    BORED_CONTROLLER = "bored_controller"      # Seen it all, slightly weary but professional
    HARRIED_CONTROLLER = "harried_controller"  # Busy day, multiple aircraft, efficient
    VETERAN_PILOT = "veteran_pilot"            # Experienced passenger giving advice
    NERVOUS_STUDENT = "nervous_student"        # Learning passenger asking questions
    ENTHUSIAST_SPOTTER = "enthusiast_spotter"  # Aircraft enthusiast with trivia
    SAFETY_OFFICER = "safety_officer"         # Safety-focused, procedure-oriented

@dataclass
class GuidanceCharacter:
    """Individual guidance character definition"""
    
    name: str
    personality: GuidancePersonality
    background: str
    speech_patterns: List[str]
    expertise_areas: List[str]
    response_likelihood: float  # 0.0 to 1.0 - how often they speak
    professional_level: int     # 1-10, affects phraseology accuracy
    
    # Character state
    current_mood: str = "neutral"
    tiredness_level: float = 0.0  # 0.0 to 1.0
    last_spoke: Optional[datetime] = None
    spoke_count_session: int = 0

@dataclass
class GuidanceContext:
    """Context for guidance communications"""
    
    # Flight situation
    aircraft_callsign: str = "unknown"
    flight_phase: str = "unknown"
    complexity_level: int = 1  # 1-10, affects character engagement
    
    # Environmental factors
    traffic_density: int = 0
    weather_conditions: str = "clear"
    emergency_situation: bool = False
    
    # Character interaction history
    active_characters: List[str] = field(default_factory=list)
    conversation_flow: List[Dict[str, Any]] = field(default_factory=list)
    dominant_character: Optional[str] = None

class FlightGuidanceCharacterSystem:
    """Main system for flight guidance characters"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger('FlightGuidanceCharacters')
        
        # Core systems integration
        self.pronunciation_engine = AviationPronunciationEngine()
        
        # Character system
        self.characters: Dict[str, GuidanceCharacter] = {}
        self.guidance_context = GuidanceContext()
        
        # Output callbacks
        self.guidance_callbacks: List[Callable[[str, str], None]] = []  # (character_name, message)
        
        # Rate limiting and cooldowns
        self.last_guidance_time = datetime.now()
        self.guidance_cooldown_seconds = 3.0
        
        # Character management
        self.max_active_characters = 2  # Usually just 1-2 speaking at once
        self.character_rotation_minutes = 15  # Rotate speaking characters
        
        self._initialize_characters()
    
    def _initialize_characters(self):
        """Initialize the cast of guidance characters"""
        
        # The bored controller - professional but world-weary
        self.characters["dublin_control"] = GuidanceCharacter(
            name="Dublin Control",
            personality=GuidancePersonality.BORED_CONTROLLER,
            background="20-year veteran controller at Dublin, seen everything twice",
            speech_patterns=[
                "Right then, {callsign}...",
                "Copy that, {callsign}, been there before...",
                "Ah yes, {callsign}, another day another dollar...",
                "Sure thing, {callsign}, nothing new under the sun...",
                "Roger, {callsign}, same old same old...",
                "*sigh* Alright {callsign}, let's sort this out...",
                "Been doing this since before you were flying, {callsign}...",
            ],
            expertise_areas=["traffic_management", "conflict_resolution", "airspace_procedures"],
            response_likelihood=0.8,
            professional_level=9
        )
        
        # The harried controller - busy but competent
        self.characters["approach_control"] = GuidanceCharacter(
            name="Approach Control", 
            personality=GuidancePersonality.HARRIED_CONTROLLER,
            background="Busy approach controller, multiple aircraft, efficient communication",
            speech_patterns=[
                "Quick one, {callsign} -",
                "{callsign}, expedite -",
                "Rapid fire, {callsign} -", 
                "Keep it moving, {callsign} -",
                "No time to chat, {callsign} -",
                "{callsign}, immediately -",
                "Speed it up, {callsign} -",
            ],
            expertise_areas=["approach_procedures", "sequencing", "emergency_handling"],
            response_likelihood=0.6,
            professional_level=8
        )
        
        # Veteran pilot passenger - wisdom and experience
        self.characters["captain_murphy"] = GuidanceCharacter(
            name="Captain Murphy",
            personality=GuidancePersonality.VETERAN_PILOT,
            background="Retired Aer Lingus captain, 35 years commercial aviation",
            speech_patterns=[
                "In my day, we'd handle that by...",
                "Reminds me of a flight back in '87...",
                "Pro tip - watch out for...",
                "I've seen this before, best to...",
                "Old pilot trick - when you see...",
                "After 10,000 hours, you learn that...",
                "Back when I flew the 737...",
            ],
            expertise_areas=["commercial_procedures", "weather_flying", "emergency_procedures"],
            response_likelihood=0.4,
            professional_level=10
        )
        
        # Aviation enthusiast passenger - excitement and knowledge
        self.characters["sarah_spotter"] = GuidanceCharacter(
            name="Sarah (Aviation Enthusiast)",
            personality=GuidancePersonality.ENTHUSIAST_SPOTTER,
            background="Aircraft spotter and aviation YouTuber",
            speech_patterns=[
                "Oh wow, look at that!",
                "Did you know that aircraft type...",
                "That's a rare sight -",
                "Perfect example of...",
                "I love seeing...",
                "Fun fact about that...",
                "My subscribers would love this...",
            ],
            expertise_areas=["aircraft_recognition", "aviation_trivia", "spotting_locations"],
            response_likelihood=0.3,
            professional_level=6
        )
        
        self.logger.info(f"Initialized {len(self.characters)} guidance characters")
    
    def add_guidance_callback(self, callback: Callable[[str, str], None]):
        """Add callback for guidance output (character_name, message)"""
        self.guidance_callbacks.append(callback)
    
    async def process_flight_situation(self, flight_data: Dict[str, Any]):
        """Process current flight situation and generate guidance if appropriate"""
        
        # Update guidance context
        await self._update_guidance_context(flight_data)
        
        # Check if guidance is warranted
        if not self._should_provide_guidance():
            return
        
        # Determine situation complexity and urgency
        situation_analysis = await self._analyze_situation(flight_data)
        
        # Select appropriate character(s) to respond
        responding_characters = self._select_responding_characters(situation_analysis)
        
        # Generate guidance from selected character(s)
        for character_name in responding_characters:
            guidance = await self._generate_character_guidance(character_name, situation_analysis, flight_data)
            if guidance:
                await self._output_guidance(character_name, guidance)
                
                # Update character state
                character = self.characters[character_name]
                character.last_spoke = datetime.now()
                character.spoke_count_session += 1
                
                # Add to conversation flow
                self.guidance_context.conversation_flow.append({
                    'timestamp': datetime.now(),
                    'character': character_name,
                    'message': guidance,
                    'situation': situation_analysis['situation_type']
                })
                
                # Respect cooldown between characters
                if len(responding_characters) > 1:
                    await asyncio.sleep(2.0)
    
    async def _update_guidance_context(self, flight_data: Dict[str, Any]):
        """Update guidance context with current flight state"""
        
        self.guidance_context.aircraft_callsign = flight_data.get('callsign', 'unknown aircraft')
        self.guidance_context.flight_phase = flight_data.get('phase', 'unknown')
        
        # Assess traffic density
        self.guidance_context.traffic_density = flight_data.get('traffic_count', 0)
        
        # Assess weather conditions  
        self.guidance_context.weather_conditions = flight_data.get('weather', 'clear')
        
        # Check for emergency situations
        self.guidance_context.emergency_situation = flight_data.get('emergency', False)
        
        # Calculate complexity level (1-10)
        complexity = 1
        complexity += min(self.guidance_context.traffic_density // 2, 3)  # More traffic = more complex
        if self.guidance_context.emergency_situation:
            complexity += 4
        if flight_data.get('weather_severity', 0) > 5:
            complexity += 2
        
        self.guidance_context.complexity_level = min(complexity, 10)
    
    async def _analyze_situation(self, flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the current situation to determine response strategy"""
        
        situation_analysis = {
            'situation_type': 'routine',
            'urgency_level': 1,  # 1-10
            'requires_technical_guidance': False,
            'traffic_concerns': [],
            'weather_concerns': [],
            'educational_opportunities': [],
            'character_preferences': []
        }
        
        # Analyze traffic situation
        if self.guidance_context.traffic_density > 3:
            situation_analysis['traffic_concerns'] = ['Multiple aircraft in vicinity']
            situation_analysis['situation_type'] = 'traffic_advisory'
            situation_analysis['urgency_level'] = max(3, situation_analysis['urgency_level'])
            situation_analysis['requires_technical_guidance'] = True
            situation_analysis['character_preferences'].extend(['dublin_control', 'approach_control'])
        
        # Analyze phase-specific opportunities
        phase = flight_data.get('phase', '')
        if phase in ['takeoff', 'landing']:
            situation_analysis['educational_opportunities'].append('critical_phase_procedures')
            situation_analysis['character_preferences'].extend(['captain_murphy', 'approach_control'])
        elif phase == 'cruise':
            situation_analysis['educational_opportunities'].append('navigation_efficiency')
            situation_analysis['character_preferences'].extend(['captain_murphy', 'sarah_spotter'])
        
        # Analyze interesting aircraft or locations
        if flight_data.get('altitude', 0) > 30000:
            situation_analysis['educational_opportunities'].append('high_altitude_operations')
        
        # Check for rare aircraft or special situations
        aircraft_type = flight_data.get('aircraft_type', '')
        if aircraft_type and aircraft_type not in ['B737', 'A320', 'B777']:  # Common types
            situation_analysis['educational_opportunities'].append('aircraft_recognition')
            situation_analysis['character_preferences'].append('sarah_spotter')
        
        return situation_analysis
    
    def _should_provide_guidance(self) -> bool:
        """Determine if guidance should be provided based on rate limiting and context"""
        
        now = datetime.now()
        
        # Check basic cooldown
        if (now - self.last_guidance_time).total_seconds() < self.guidance_cooldown_seconds:
            return False
        
        # Higher complexity situations override longer cooldowns
        base_cooldown = self.guidance_cooldown_seconds
        complexity_factor = max(1, 11 - self.guidance_context.complexity_level)
        effective_cooldown = base_cooldown * complexity_factor
        
        if (now - self.last_guidance_time).total_seconds() < effective_cooldown:
            return False
        
        # Emergency situations always get guidance
        if self.guidance_context.emergency_situation:
            return True
        
        # Random factor to make guidance feel natural
        base_probability = 0.3  # 30% base chance
        complexity_bonus = self.guidance_context.complexity_level * 0.05
        final_probability = min(base_probability + complexity_bonus, 0.8)
        
        return random.random() < final_probability
    
    def _select_responding_characters(self, situation_analysis: Dict[str, Any]) -> List[str]:
        """Select which character(s) should respond to the situation"""
        
        # Filter available characters
        available_characters = []
        now = datetime.now()
        
        for char_name, character in self.characters.items():
            # Check if character is rested enough
            if character.last_spoke:
                minutes_since_spoke = (now - character.last_spoke).total_seconds() / 60
                if minutes_since_spoke < 5:  # 5 minute minimum between same character
                    continue
            
            # Check response likelihood
            if random.random() > character.response_likelihood:
                continue
            
            available_characters.append(char_name)
        
        if not available_characters:
            return []
        
        # Prioritize based on situation preferences
        preferred_characters = []
        for char_name in situation_analysis.get('character_preferences', []):
            if char_name in available_characters:
                preferred_characters.append(char_name)
        
        # If no preferred characters, use available ones
        if not preferred_characters:
            preferred_characters = available_characters
        
        # Select based on urgency
        urgency = situation_analysis['urgency_level']
        if urgency >= 7:
            # High urgency - professional characters only
            professional_chars = [c for c in preferred_characters 
                                if self.characters[c].professional_level >= 8]
            if professional_chars:
                return [random.choice(professional_chars)]
        
        # Normal selection - usually just one character
        selected = [random.choice(preferred_characters)]
        
        # Occasionally have multiple characters (conversation feel)
        if (situation_analysis['situation_type'] == 'routine' and 
            len(preferred_characters) > 1 and 
            random.random() < 0.2):  # 20% chance of multiple speakers
            
            second_char = random.choice([c for c in preferred_characters if c != selected[0]])
            selected.append(second_char)
        
        return selected
    
    async def _generate_character_guidance(self, character_name: str, situation_analysis: Dict[str, Any], 
                                         flight_data: Dict[str, Any]) -> Optional[str]:
        """Generate guidance message from specific character"""
        
        character = self.characters[character_name]
        
        # For now, use template-based guidance - can be enhanced with LLM later
        return self._generate_template_guidance(character, situation_analysis, flight_data)
    
    def _generate_template_guidance(self, character: GuidanceCharacter, situation_analysis: Dict[str, Any], 
                                  flight_data: Dict[str, Any]) -> str:
        """Generate guidance using character templates"""
        
        callsign = self.guidance_context.aircraft_callsign
        
        # Template-based guidance by character
        templates = {
            GuidancePersonality.BORED_CONTROLLER: [
                f"Right then {callsign}, traffic observed, suggest maintaining current altitude.",
                f"{callsign}, been watching that traffic, no immediate concerns.",
                f"Copy {callsign}, standard procedures apply here.",
                f"*sigh* {callsign}, nothing I haven't seen before.",
            ],
            GuidancePersonality.HARRIED_CONTROLLER: [
                f"{callsign}, traffic advisory, maintain separation.",
                f"Quick one {callsign} - traffic twelve o'clock, monitor.",
                f"{callsign}, expedite climb if able.",
                f"Keep it moving {callsign}, busy airspace today.",
            ],
            GuidancePersonality.VETERAN_PILOT: [
                f"In my experience {callsign}, watch that traffic pattern.",
                f"{callsign}, old pilot trick - keep your head on a swivel.",
                f"Reminds me of a flight I had {callsign}, stay alert.",
                f"Pro tip {callsign} - this altitude works well for this route.",
            ],
            GuidancePersonality.ENTHUSIAST_SPOTTER: [
                f"Oh wow {callsign}, great view of that traffic!",
                f"{callsign}, perfect example of traffic management!",
                f"Look at that {callsign}, textbook flying!",
                f"Fun fact {callsign} - this is a busy corridor!",
            ]
        }
        
        character_templates = templates.get(character.personality, templates[GuidancePersonality.BORED_CONTROLLER])
        guidance = random.choice(character_templates)
        
        # Apply character-specific processing
        if character.personality == GuidancePersonality.BORED_CONTROLLER:
            # Occasionally add sighs or weary expressions
            if random.random() < 0.3:
                sigh_variants = ["*sigh*", "Right then,", "Ah,", "Well,"]
                guidance = f"{random.choice(sigh_variants)} {guidance}"
        
        elif character.personality == GuidancePersonality.HARRIED_CONTROLLER:
            # Ensure brevity and efficiency
            guidance = guidance.replace("please", "").replace(" really", "").replace(" very", "")
        
        return guidance
    
    async def _output_guidance(self, character_name: str, guidance: str):
        """Output guidance through all registered callbacks"""
        
        self.logger.info(f"{character_name}: {guidance}")
        
        for callback in self.guidance_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(character_name, guidance)
                else:
                    callback(character_name, guidance)
            except Exception as e:
                self.logger.error(f"Error in guidance callback: {e}")
        
        # Update timing
        self.last_guidance_time = datetime.now()
    
    async def handle_emergency_situation(self, emergency_data: Dict[str, Any]):
        """Handle emergency situations with immediate guidance"""
        
        self.guidance_context.emergency_situation = True
        self.guidance_context.complexity_level = 10
        
        # Select most professional character immediately
        professional_chars = [name for name, char in self.characters.items() 
                            if char.professional_level >= 8]
        
        if professional_chars:
            selected_char = professional_chars[0]  # Use most professional
            
            emergency_guidance = await self._generate_emergency_guidance(selected_char, emergency_data)
            if emergency_guidance:
                await self._output_guidance(selected_char, emergency_guidance)
    
    async def _generate_emergency_guidance(self, character_name: str, emergency_context: Dict[str, Any]) -> str:
        """Generate emergency-specific guidance"""
        
        character = self.characters[character_name]
        callsign = self.guidance_context.aircraft_callsign
        
        # Emergency templates by character
        emergency_templates = {
            "dublin_control": [
                f"{callsign}, understand emergency. State intentions, assistance available.",
                f"{callsign}, roger emergency. Clearing airspace, priority handling.",
                f"{callsign}, emergency services alerted. Proceed as required.",
            ],
            "approach_control": [
                f"{callsign}, emergency acknowledged. Immediate vectors available.",
                f"{callsign}, priority approach cleared. Emergency equipment standing by.",
                f"{callsign}, understand emergency. Runway available, cleared immediate.",
            ],
            "captain_murphy": [
                f"{callsign}, stay calm. Run your emergency checklist first.",
                f"{callsign}, been through this before. Follow procedures, you'll be fine.",
                f"{callsign}, emergency training kicks in now. Trust your procedures.",
            ]
        }
        
        templates = emergency_templates.get(character_name, emergency_templates["dublin_control"])
        return random.choice(templates)
    
    def get_character_status(self) -> Dict[str, Any]:
        """Get status of all guidance characters"""
        
        status = {
            'total_characters': len(self.characters),
            'active_characters': [],
            'character_details': {},
            'recent_activity': len(self.guidance_context.conversation_flow),
            'system_status': 'operational'
        }
        
        now = datetime.now()
        for name, character in self.characters.items():
            
            # Determine if character is active
            is_active = False
            if character.last_spoke:
                minutes_since = (now - character.last_spoke).total_seconds() / 60
                is_active = minutes_since < 30  # Active if spoke in last 30 minutes
            
            if is_active:
                status['active_characters'].append(name)
            
            status['character_details'][name] = {
                'personality': character.personality.value,
                'professional_level': character.professional_level,
                'response_likelihood': character.response_likelihood,
                'session_messages': character.spoke_count_session,
                'last_spoke': character.last_spoke.isoformat() if character.last_spoke else None,
                'current_mood': character.current_mood,
                'expertise_areas': character.expertise_areas
            }
        
        return status
    
    async def force_character_guidance(self, character_name: str, situation_override: Optional[str] = None) -> Optional[str]:
        """Force a specific character to provide guidance (for testing/demos)"""
        
        if character_name not in self.characters:
            self.logger.error(f"Character {character_name} not found")
            return None
        
        # Create mock situation if needed
        mock_situation = {
            'situation_type': situation_override or 'routine',
            'urgency_level': 3,
            'traffic_concerns': [],
            'weather_concerns': [],
            'educational_opportunities': ['general_guidance'],
            'character_preferences': [character_name]
        }
        
        mock_flight_data = {
            'callsign': self.guidance_context.aircraft_callsign,
            'phase': self.guidance_context.flight_phase,
            'altitude': 25000,
            'speed': 400,
            'heading': 90
        }
        
        guidance = await self._generate_character_guidance(character_name, mock_situation, mock_flight_data)
        
        if guidance:
            await self._output_guidance(character_name, guidance)
        
        return guidance

# Utility functions and testing

async def test_guidance_system():
    """Test the flight guidance character system"""
    
    guidance_system = FlightGuidanceCharacterSystem()
    
    # Add test callback
    def print_guidance(character_name: str, message: str):
        print(f"[VOICE] {character_name}: {message}")
    
    guidance_system.add_guidance_callback(print_guidance)
    
    print("[GUIDANCE] Testing Flight Guidance Character System")
    print("=" * 60)
    
    # Test routine flight
    await guidance_system.process_flight_situation({
        'callsign': 'EI-XYZ',
        'phase': 'cruise',
        'altitude': 35000,
        'speed': 450,
        'heading': 90,
        'aircraft_type': 'B737'
    })
    
    await asyncio.sleep(2)
    
    # Test traffic situation
    await guidance_system.process_flight_situation({
        'callsign': 'EI-XYZ',
        'phase': 'cruise',
        'altitude': 35000,
        'speed': 450,
        'heading': 90,
        'traffic_count': 5
    })
    
    await asyncio.sleep(2)
    
    # Test emergency
    await guidance_system.handle_emergency_situation({
        'type': 'engine_failure',
        'severity': 'high'
    })
    
    await asyncio.sleep(2)
    
    # Test specific character
    await guidance_system.force_character_guidance('sarah_spotter', 'aircraft_spotting')
    
    # Show character status
    status = guidance_system.get_character_status()
    print(f"\n[STATUS] Character Status: {status['total_characters']} characters, {len(status['active_characters'])} active")
    
    print("\n[OK] Flight Guidance Character System test completed")

if __name__ == "__main__":
    asyncio.run(test_guidance_system())
