# File: aviation_pronunciation.py
"""
Aviation Pronunciation Module
Implements proper radiotelephony procedures and ICAO pronunciation standards
Based on ICAO Annex 10, Volume II and UK CAP 413 Radiotelephony Manual
"""

import re
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

# ICAO Phonetic Alphabet
ICAO_PHONETIC_ALPHABET = {
    'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta',
    'E': 'Echo', 'F': 'Foxtrot', 'G': 'Golf', 'H': 'Hotel',
    'I': 'India', 'J': 'Juliet', 'K': 'Kilo', 'L': 'Lima',
    'M': 'Mike', 'N': 'November', 'O': 'Oscar', 'P': 'Papa',
    'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
    'U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'X-ray',
    'Y': 'Yankee', 'Z': 'Zulu'
}

# Number pronunciation for aviation
AVIATION_NUMBERS = {
    '0': 'Zero', '1': 'One', '2': 'Two', '3': 'Three', '4': 'Four',
    '5': 'Five', '6': 'Six', '7': 'Seven', '8': 'Eight', '9': 'Niner'
}

# Special aviation number groups
AVIATION_HUNDREDS = {
    '100': 'One Hundred',
    '200': 'Two Hundred',
    '300': 'Three Hundred',
    '400': 'Four Hundred',
    '500': 'Five Hundred',
    '600': 'Six Hundred',
    '700': 'Seven Hundred',
    '800': 'Eight Hundred',
    '900': 'Niner Hundred'
}

AVIATION_THOUSANDS = {
    '1000': 'One Thousand',
    '2000': 'Two Thousand',
    '3000': 'Three Thousand',
    '4000': 'Four Thousand',
    '5000': 'Five Thousand',
    '6000': 'Six Thousand',
    '7000': 'Seven Thousand',
    '8000': 'Eight Thousand',
    '9000': 'Niner Thousand',
    '10000': 'One Zero Thousand'
}

@dataclass
class AviationPhrase:
    """Standard aviation phrase with pronunciation guide"""
    
    text: str
    pronunciation: str
    category: str  # 'altitude', 'heading', 'frequency', 'callsign', etc.
    context: Optional[str] = None

class AviationPronunciationEngine:
    """Engine for converting text to proper aviation pronunciation"""
    
    def __init__(self):
        self.common_phrases = self._load_common_phrases()
        self.airport_pronunciations = self._load_airport_pronunciations()
        self.navigation_aids = self._load_navigation_aids()
    
    def _load_common_phrases(self) -> Dict[str, str]:
        """Load common aviation phrases and their pronunciations"""
        return {
            # Altitude phrases
            'FL': 'Flight Level',
            'ft': 'feet',
            'climbing': 'climbing',
            'descending': 'descending',
            'maintaining': 'maintaining',
            'level': 'level',
            
            # Speed phrases
            'kts': 'knots',
            'mach': 'mach',
            'indicated': 'indicated',
            'ground speed': 'ground speed',
            
            # Navigation phrases
            'heading': 'heading',
            'track': 'track',
            'course': 'course',
            'bearing': 'bearing',
            'radial': 'radial',
            
            # Weather phrases
            'wind': 'wind',
            'visibility': 'visibility',
            'ceiling': 'ceiling',
            'cloud': 'cloud',
            'CAVOK': 'Cav-Oh-Kay',
            'METAR': 'Met-Arr',
            'TAF': 'Taff',
            
            # Time phrases
            'UTC': 'Coordinated Universal Time',
            'Zulu': 'Zulu',
            'local': 'local time',
            
            # Traffic phrases
            'traffic': 'traffic',
            'contact': 'contact',
            'advisory': 'advisory',
            'no factor': 'no factor',
            
            # Standard phrases
            'roger': 'roger',
            'wilco': 'wilco',
            'affirm': 'affirm',
            'negative': 'negative',
            'standby': 'standby',
            'say again': 'say again'
        }
    
    def _load_airport_pronunciations(self) -> Dict[str, str]:
        """Load airport ICAO codes with proper pronunciations"""
        return {
            # Ireland
            'EIDW': 'Echo India Delta Whiskey',  # Dublin
            'EICK': 'Echo India Charlie Kilo',   # Cork
            'EINN': 'Echo India November November',  # Shannon
            'EISG': 'Echo India Sierra Golf',    # Sligo
            'EIKN': 'Echo India Kilo November',  # Knock
            
            # UK Major Airports
            'EGLL': 'Echo Golf Lima Lima',       # Heathrow
            'EGKK': 'Echo Golf Kilo Kilo',       # Gatwick
            'EGSS': 'Echo Golf Sierra Sierra',   # Stansted
            'EGGW': 'Echo Golf Golf Whiskey',    # Luton
            'EGLC': 'Echo Golf Lima Charlie',    # London City
            'EGPH': 'Echo Golf Papa Hotel',      # Edinburgh
            'EGPF': 'Echo Golf Papa Foxtrot',    # Glasgow
            'EGCC': 'Echo Golf Charlie Charlie', # Manchester
            'EGBB': 'Echo Golf Bravo Bravo',     # Birmingham
            'EGGP': 'Echo Golf Golf Papa',       # Liverpool
            'EGNX': 'Echo Golf November X-ray',  # East Midlands
            'EGNT': 'Echo Golf November Tango',  # Newcastle
            'EGTE': 'Echo Golf Tango Echo',      # Exeter
            'EGFF': 'Echo Golf Foxtrot Foxtrot', # Cardiff
            
            # International Examples
            'KJFK': 'Kilo Juliet Foxtrot Kilo',  # JFK
            'KLAX': 'Kilo Lima Alpha X-ray',     # LAX
            'KORD': 'Kilo Oscar Romeo Delta',    # O'Hare
            'LFPG': 'Lima Foxtrot Papa Golf',    # Charles de Gaulle
            'EDDF': 'Echo Delta Delta Foxtrot',  # Frankfurt
            'EHAM': 'Echo Hotel Alpha Mike',     # Amsterdam Schiphol
        }
    
    def _load_navigation_aids(self) -> Dict[str, str]:
        """Load navigation aid identifiers with pronunciations"""
        return {
            # VOR stations (examples)
            'DUB': 'Delta Uniform Bravo',        # Dublin VOR
            'SHA': 'Sierra Hotel Alpha',         # Shannon VOR
            'CRK': 'Charlie Romeo Kilo',         # Cork VOR
            'LON': 'Lima Oscar November',        # London VOR
            'BHD': 'Bravo Hotel Delta',          # Belfast VOR
            
            # NDB stations (examples)
            'DN': 'Delta November',              # Dublin NDB
            'SN': 'Sierra November',             # Shannon NDB
            'CK': 'Charlie Kilo',                # Cork NDB
        }
    
    def pronounce_icao_code(self, icao_code: str) -> str:
        """Convert ICAO code to phonetic pronunciation"""
        if not icao_code:
            return ""
        
        # Check if we have a specific pronunciation
        icao_upper = icao_code.upper()
        if icao_upper in self.airport_pronunciations:
            return self.airport_pronunciations[icao_upper]
        
        # Default: spell out each letter phonetically
        pronunciation_parts = []
        for char in icao_upper:
            if char in ICAO_PHONETIC_ALPHABET:
                pronunciation_parts.append(ICAO_PHONETIC_ALPHABET[char])
            elif char.isdigit():
                pronunciation_parts.append(AVIATION_NUMBERS[char])
            else:
                pronunciation_parts.append(char)  # Fallback for special characters
        
        return ' '.join(pronunciation_parts)
    
    def pronounce_altitude(self, altitude: Union[int, str]) -> str:
        """Convert altitude to proper aviation pronunciation"""
        if isinstance(altitude, str):
            try:
                altitude = int(altitude.replace(',', '').replace('ft', '').strip())
            except ValueError:
                return str(altitude)
        
        # Flight levels (above 18,000 ft in most countries)
        if altitude >= 18000 and altitude % 100 == 0:
            flight_level = altitude // 100
            if flight_level < 100:
                return f"Flight Level {self._pronounce_flight_level_number(flight_level)}"
            else:
                # For FL100 and above, read as individual digits
                fl_str = str(flight_level)
                digits = [AVIATION_NUMBERS[d] for d in fl_str]
                return f"Flight Level {' '.join(digits)}"
        
        # Standard altitude pronunciation
        return self._pronounce_altitude_feet(altitude)
    
    def _pronounce_flight_level_number(self, fl_number: int) -> str:
        """Pronounce flight level numbers properly"""
        if fl_number < 10:
            return f"Zero {AVIATION_NUMBERS[str(fl_number)]}"
        elif fl_number < 100:
            tens = fl_number // 10
            ones = fl_number % 10
            if ones == 0:
                # For round tens (20, 30, etc.)
                return f"{AVIATION_NUMBERS[str(tens)]} Zero"
            else:
                return f"{AVIATION_NUMBERS[str(tens)]} {AVIATION_NUMBERS[str(ones)]}"
        else:
            # For 100+, read as individual digits
            fl_str = str(fl_number)
            digits = [AVIATION_NUMBERS[d] for d in fl_str]
            return ' '.join(digits)
    
    def _pronounce_altitude_feet(self, altitude: int) -> str:
        """Pronounce altitude in feet"""
        if altitude == 0:
            return "Zero feet"
        
        # Handle thousands
        if altitude >= 1000:
            thousands = altitude // 1000
            hundreds = (altitude % 1000) // 100
            remainder = altitude % 100
            
            parts = []
            
            # Thousands part
            if thousands == 1:
                parts.append("One Thousand")
            else:
                thousands_digits = [AVIATION_NUMBERS[d] for d in str(thousands)]
                parts.append(' '.join(thousands_digits) + " Thousand")
            
            # Hundreds part
            if hundreds > 0:
                parts.append(f"{AVIATION_NUMBERS[str(hundreds)]} Hundred")
            
            # Remainder
            if remainder > 0:
                if remainder < 10:
                    parts.append(AVIATION_NUMBERS[str(remainder)])
                else:
                    remainder_digits = [AVIATION_NUMBERS[d] for d in str(remainder)]
                    parts.append(' '.join(remainder_digits))
            
            return ' '.join(parts) + " feet"
        
        # Handle hundreds
        elif altitude >= 100:
            hundreds = altitude // 100
            remainder = altitude % 100
            
            parts = [f"{AVIATION_NUMBERS[str(hundreds)]} Hundred"]
            
            if remainder > 0:
                if remainder < 10:
                    parts.append(AVIATION_NUMBERS[str(remainder)])
                else:
                    remainder_digits = [AVIATION_NUMBERS[d] for d in str(remainder)]
                    parts.append(' '.join(remainder_digits))
            
            return ' '.join(parts) + " feet"
        
        # Handle numbers less than 100
        else:
            if altitude < 10:
                return f"{AVIATION_NUMBERS[str(altitude)]} feet"
            else:
                digits = [AVIATION_NUMBERS[d] for d in str(altitude)]
                return ' '.join(digits) + " feet"
    
    def pronounce_heading(self, heading: Union[int, str]) -> str:
        """Convert heading to proper aviation pronunciation"""
        if isinstance(heading, str):
            try:
                heading = int(heading.replace('°', '').strip())
            except ValueError:
                return str(heading)
        
        # Normalize to 0-359
        heading = heading % 360
        
        # Convert to 3-digit format and pronounce each digit
        heading_str = f"{heading:03d}"
        digits = [AVIATION_NUMBERS[d] for d in heading_str]
        
        return ' '.join(digits)
    
    def pronounce_frequency(self, frequency: Union[float, str]) -> str:
        """Convert radio frequency to proper aviation pronunciation"""
        if isinstance(frequency, str):
            try:
                frequency = float(frequency.replace('MHz', '').strip())
            except ValueError:
                return str(frequency)
        
        # Split into whole and decimal parts
        freq_str = f"{frequency:.3f}"
        whole_part, decimal_part = freq_str.split('.')
        
        # Pronounce whole part
        whole_digits = [AVIATION_NUMBERS[d] for d in whole_part]
        whole_pronunciation = ' '.join(whole_digits)
        
        # Pronounce decimal part
        decimal_digits = [AVIATION_NUMBERS[d] for d in decimal_part]
        decimal_pronunciation = ' '.join(decimal_digits)
        
        return f"{whole_pronunciation} decimal {decimal_pronunciation}"
    
    def pronounce_speed(self, speed: Union[int, str], unit: str = "knots") -> str:
        """Convert speed to proper aviation pronunciation"""
        if isinstance(speed, str):
            try:
                speed = int(speed.replace('kts', '').replace('knots', '').strip())
            except ValueError:
                return str(speed)
        
        if speed == 0:
            return f"Zero {unit}"
        
        # For speeds, we usually group by meaningful chunks
        if speed < 100:
            if speed < 10:
                return f"{AVIATION_NUMBERS[str(speed)]} {unit}"
            else:
                digits = [AVIATION_NUMBERS[d] for d in str(speed)]
                return f"{' '.join(digits)} {unit}"
        else:
            # For speeds 100+, often pronounced as "two five zero" for 250
            digits = [AVIATION_NUMBERS[d] for d in str(speed)]
            return f"{' '.join(digits)} {unit}"
    
    def pronounce_time(self, time_str: str) -> str:
        """Convert time to proper aviation pronunciation"""
        # Handle UTC time format (e.g., "1430Z", "14:30", "2:30 PM")
        
        # Remove common suffixes
        clean_time = time_str.replace('Z', '').replace('UTC', '').replace('GMT', '').strip()
        
        # Try to parse different formats
        if ':' in clean_time:
            # Format: "14:30" or "2:30"
            parts = clean_time.split(':')
            if len(parts) == 2:
                hours = parts[0].zfill(2)
                minutes = parts[1].zfill(2)
                time_digits = hours + minutes
            else:
                return time_str  # Can't parse
        elif len(clean_time) == 4 and clean_time.isdigit():
            # Format: "1430"
            time_digits = clean_time
        elif len(clean_time) == 3 and clean_time.isdigit():
            # Format: "430" (assume leading zero)
            time_digits = '0' + clean_time
        else:
            return time_str  # Can't parse
        
        # Convert each digit
        digits = [AVIATION_NUMBERS[d] for d in time_digits]
        
        # Add "hours" in the middle for clarity
        if len(digits) == 4:
            return f"{digits[0]} {digits[1]} {digits[2]} {digits[3]} hours"
        else:
            return ' '.join(digits) + " hours"
    
    def pronounce_wind(self, direction: Union[int, str], speed: Union[int, str], 
                      gusts: Optional[Union[int, str]] = None) -> str:
        """Convert wind information to proper aviation pronunciation"""
        
        # Parse direction
        if isinstance(direction, str):
            if direction.lower() in ['vrb', 'variable']:
                direction_pronunciation = "variable"
            else:
                try:
                    direction = int(direction.replace('°', '').strip())
                    direction_pronunciation = self.pronounce_heading(direction)
                except ValueError:
                    direction_pronunciation = str(direction)
        else:
            direction_pronunciation = self.pronounce_heading(direction)
        
        # Parse speed
        if isinstance(speed, str):
            try:
                speed = int(speed.replace('kts', '').replace('knots', '').strip())
            except ValueError:
                speed_pronunciation = str(speed)
            else:
                speed_pronunciation = self.pronounce_speed(speed, "knots")
        else:
            speed_pronunciation = self.pronounce_speed(speed, "knots")
        
        # Build wind report
        wind_report = f"Wind {direction_pronunciation} at {speed_pronunciation}"
        
        # Add gusts if present
        if gusts is not None:
            if isinstance(gusts, str):
                try:
                    gusts = int(gusts.replace('kts', '').replace('knots', '').strip())
                except ValueError:
                    gusts_pronunciation = str(gusts)
                else:
                    gusts_pronunciation = self.pronounce_speed(gusts, "knots")
            else:
                gusts_pronunciation = self.pronounce_speed(gusts, "knots")
            
            wind_report += f", gusting {gusts_pronunciation}"
        
        return wind_report
    
    def pronounce_visibility(self, visibility: Union[float, str]) -> str:
        """Convert visibility to proper aviation pronunciation"""
        if isinstance(visibility, str):
            try:
                visibility = float(visibility.replace('SM', '').replace('km', '').strip())
            except ValueError:
                return str(visibility)
        
        # Check for special cases
        if visibility >= 10:
            return "Greater than one zero statute miles"
        elif visibility >= 1:
            # For visibility like 3.5, 2.25, etc.
            if visibility == int(visibility):
                # Whole number
                vis_str = str(int(visibility))
                digits = [AVIATION_NUMBERS[d] for d in vis_str]
                return f"{' '.join(digits)} statute miles"
            else:
                # Decimal
                vis_str = f"{visibility:.2f}".rstrip('0').rstrip('.')
                whole_part, decimal_part = vis_str.split('.') if '.' in vis_str else (vis_str, '')
                
                whole_digits = [AVIATION_NUMBERS[d] for d in whole_part] if whole_part else []
                decimal_digits = [AVIATION_NUMBERS[d] for d in decimal_part] if decimal_part else []
                
                pronunciation_parts = []
                if whole_digits:
                    pronunciation_parts.append(' '.join(whole_digits))
                if decimal_digits:
                    pronunciation_parts.append(f"point {' '.join(decimal_digits)}")
                
                return f"{' '.join(pronunciation_parts)} statute miles"
        else:
            # Less than 1 mile - use fractions or decimals
            vis_str = f"{visibility:.2f}".rstrip('0').rstrip('.')
            if '.' in vis_str:
                whole_part, decimal_part = vis_str.split('.')
                decimal_digits = [AVIATION_NUMBERS[d] for d in decimal_part]
                return f"Zero point {' '.join(decimal_digits)} statute miles"
            else:
                return f"{AVIATION_NUMBERS[vis_str]} statute miles"
    
    def format_traffic_call(self, callsign: str, aircraft_type: str, 
                           distance: float, bearing: int, altitude_diff: int) -> str:
        """Format a traffic call with proper pronunciation"""
        
        # Format callsign
        if callsign.isalpha():
            # All letters - use phonetic alphabet
            callsign_pronunciation = self.pronounce_icao_code(callsign)
        elif callsign.replace('-', '').replace(' ', '').isalnum():
            # Mixed letters and numbers
            callsign_parts = []
            current_part = ""
            current_type = None
            
            for char in callsign.upper():
                if char == '-' or char == ' ':
                    if current_part:
                        if current_type == 'letter':
                            callsign_parts.append(self.pronounce_icao_code(current_part))
                        else:
                            digits = [AVIATION_NUMBERS[d] for d in current_part]
                            callsign_parts.append(' '.join(digits))
                        current_part = ""
                        current_type = None
                elif char.isalpha():
                    if current_type == 'digit' and current_part:
                        digits = [AVIATION_NUMBERS[d] for d in current_part]
                        callsign_parts.append(' '.join(digits))
                        current_part = ""
                    current_part += char
                    current_type = 'letter'
                elif char.isdigit():
                    if current_type == 'letter' and current_part:
                        callsign_parts.append(self.pronounce_icao_code(current_part))
                        current_part = ""
                    current_part += char
                    current_type = 'digit'
            
            # Add final part
            if current_part:
                if current_type == 'letter':
                    callsign_parts.append(self.pronounce_icao_code(current_part))
                else:
                    digits = [AVIATION_NUMBERS[d] for d in current_part]
                    callsign_parts.append(' '.join(digits))
            
            callsign_pronunciation = ' '.join(callsign_parts)
        else:
            callsign_pronunciation = callsign
        
        # Format distance
        if distance >= 1:
            distance_int = int(round(distance))
            if distance_int < 10:
                distance_pronunciation = AVIATION_NUMBERS[str(distance_int)]
            else:
                distance_digits = [AVIATION_NUMBERS[d] for d in str(distance_int)]
                distance_pronunciation = ' '.join(distance_digits)
        else:
            distance_pronunciation = "Less than one"
        
        # Format bearing
        bearing_pronunciation = self.pronounce_heading(bearing)
        
        # Format altitude difference
        if altitude_diff > 500:
            altitude_phrase = f"{self._pronounce_number_simple(altitude_diff)} feet above"
        elif altitude_diff < -500:
            altitude_phrase = f"{self._pronounce_number_simple(abs(altitude_diff))} feet below"
        else:
            altitude_phrase = "at similar altitude"
        
        # Build traffic call
        traffic_call = (f"Traffic, {callsign_pronunciation}, {aircraft_type}, "
                       f"{distance_pronunciation} nautical miles, "
                       f"{bearing_pronunciation} o'clock, {altitude_phrase}")
        
        return traffic_call
    
    def _pronounce_number_simple(self, number: int) -> str:
        """Simple number pronunciation for general use"""
        if number < 10:
            return AVIATION_NUMBERS[str(number)]
        elif number < 100:
            tens = number // 10
            ones = number % 10
            if ones == 0:
                return f"{AVIATION_NUMBERS[str(tens)]} zero"
            else:
                return f"{AVIATION_NUMBERS[str(tens)]} {AVIATION_NUMBERS[str(ones)]}"
        else:
            # For larger numbers, read as digits
            digits = [AVIATION_NUMBERS[d] for d in str(number)]
            return ' '.join(digits)
    
    def format_position_report(self, latitude: float, longitude: float, 
                              altitude: int, heading: int) -> str:
        """Format a position report with proper pronunciation"""
        
        # Format latitude
        lat_deg = int(abs(latitude))
        lat_min = int((abs(latitude) - lat_deg) * 60)
        lat_hem = "North" if latitude >= 0 else "South"
        
        lat_deg_pronunciation = self._pronounce_number_simple(lat_deg)
        lat_min_pronunciation = self._pronounce_number_simple(lat_min)
        
        # Format longitude
        lon_deg = int(abs(longitude))
        lon_min = int((abs(longitude) - lon_deg) * 60)
        lon_hem = "East" if longitude >= 0 else "West"
        
        lon_deg_pronunciation = self._pronounce_number_simple(lon_deg)
        lon_min_pronunciation = self._pronounce_number_simple(lon_min)
        
        # Format altitude and heading
        altitude_pronunciation = self.pronounce_altitude(altitude)
        heading_pronunciation = self.pronounce_heading(heading)
        
        position_report = (f"Position: {lat_deg_pronunciation} degrees "
                         f"{lat_min_pronunciation} minutes {lat_hem}, "
                         f"{lon_deg_pronunciation} degrees "
                         f"{lon_min_pronunciation} minutes {lon_hem}, "
                         f"{altitude_pronunciation}, heading {heading_pronunciation}")
        
        return position_report

# Testing function
def test_aviation_pronunciation():
    """Test the aviation pronunciation engine"""
    
    engine = AviationPronunciationEngine()
    
    print("=== ICAO Code Pronunciation Tests ===")
    test_icao_codes = ['EIDW', 'EGLL', 'KJFK', 'LFPG', 'ABC123']
    for code in test_icao_codes:
        print(f"{code} -> {engine.pronounce_icao_code(code)}")
    
    print("\n=== Altitude Pronunciation Tests ===")
    test_altitudes = [100, 1500, 3500, 10000, 25000, 35000, 41000]
    for alt in test_altitudes:
        print(f"{alt} ft -> {engine.pronounce_altitude(alt)}")
    
    print("\n=== Heading Pronunciation Tests ===")
    test_headings = [0, 5, 45, 90, 180, 270, 360]
    for hdg in test_headings:
        print(f"{hdg}° -> {engine.pronounce_heading(hdg)}")
    
    print("\n=== Frequency Pronunciation Tests ===")
    test_frequencies = [118.1, 121.5, 132.45, 134.875]
    for freq in test_frequencies:
        print(f"{freq} MHz -> {engine.pronounce_frequency(freq)}")
    
    print("\n=== Wind Pronunciation Tests ===")
    test_winds = [
        (270, 15, None),
        (90, 25, 35),
        ('VRB', 5, None)
    ]
    for direction, speed, gusts in test_winds:
        print(f"Wind {direction}/{speed}G{gusts or 'none'} -> {engine.pronounce_wind(direction, speed, gusts)}")
    
    print("\n=== Traffic Call Test ===")
    traffic_call = engine.format_traffic_call("EI-ABC", "Boeing 737", 5.2, 120, 2000)
    print(f"Traffic call -> {traffic_call}")

if __name__ == "__main__":
    test_aviation_pronunciation()
