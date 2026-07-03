"""Service for deterministic extraction of numeric parameters using regex."""

import re
from typing import List, NamedTuple, Optional, Dict
from dataclasses import dataclass

@dataclass
class NumericValue:
    """Represents a numeric value extracted from text."""
    property_name: str
    value: float
    unit: str
    raw_text: str
    start: int
    end: int

class NumericExtractor:
    """
    Extracts numeric conditions (temperature, pH, pressure, etc.) using regular expressions.
    Supports both Russian and English terminology.
    """

    def __init__(self):
        # Define patterns for various properties
        # Each pattern is a tuple of (property_name, regex)
        # Regexes handle:
        # - Numbers: integers or decimals with . or , as decimal separator
        # - Optional spaces between number and unit
        # - Russian/English keywords

        self.number_pattern = r"(-?\d+(?:[\.,]\d+)?)"

        self.patterns = [
            ("temperature", re.compile(
                rf"(?:температура|temperature|temp)\s*[:=]?\s*{self.number_pattern}\s*(°?C|°?F|K|Celsius|Fahrenheit|Kelvin)",
                re.IGNORECASE
            )),
            ("ph", re.compile(
                rf"(?:pH|рН)\s*[:=]?\s*{self.number_pattern}",
                re.IGNORECASE
            )),
            ("pressure", re.compile(
                rf"(?:давление|pressure|press)\s*[:=]?\s*{self.number_pattern}\s*(bar|atm|kPa|MPa|Pa)",
                re.IGNORECASE
            )),
            ("concentration", re.compile(
                rf"(?:концентрация|concentration|conc)\s*[:=]?\s*{self.number_pattern}\s*(%|ppm|mol/l)",
                re.IGNORECASE
            )),
            ("flow_velocity", re.compile(
                rf"(?:скорость потока|flow velocity|velocity)\s*[:=]?\s*{self.number_pattern}\s*(m/s|cm/s|mm/s|l/min)",
                re.IGNORECASE
            )),
            ("productivity", re.compile(
                rf"(?:производительность|productivity)\s*[:=]?\s*{self.number_pattern}\s*(t/year|kg/h|t/month)",
                re.IGNORECASE
            )),
            ("recovery", re.compile(
                rf"(?:извлечение|recovery)\s*[:=]?\s*{self.number_pattern}\s*%",
                re.IGNORECASE
            )),
            ("year", re.compile(
                rf"(?:год|year)\s*[:=]?\s*{self.number_pattern}",
                re.IGNORECASE
            )),
        ]

    def _parse_float(self, value_str: str) -> float:
        """Convert string to float, handling comma as decimal separator."""
        return float(value_str.replace(",", "."))

    def extract(self, text: str) -> List[NumericValue]:
        """
        Scans text for numeric parameters and returns a list of extracted values.
        """
        if not text:
            return []

        results = []
        for prop_name, pattern in self.patterns:
            for match in pattern.finditer(text):
                groups = match.groups()
                # The first group is always the numeric value
                val_str = groups[0]
                value = self._parse_float(val_str)

                # For pH and Year, there might be no unit group in the regex
                unit = ""
                if len(groups) > 1:
                    unit = groups[1] if groups[1] else ""

                results.append(NumericValue(
                    property_name=prop_name,
                    value=value,
                    unit=unit,
                    raw_text=match.group(0),
                    start=match.start(),
                    end=match.end()
                ))

        # Sort by starting position in text
        return sorted(results, key=lambda x: x.start)
