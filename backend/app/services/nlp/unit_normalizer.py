"""Service for normalizing technical units to SI equivalents."""

from typing import Dict, Optional, Tuple
import math


class UnitNormalizer:
    """
    Handles conversion of various technical units to SI base units.
    Following the SDD requirement for deterministic normalization.
    """

    # Mapping of unit symbols/names to (multiplier, offset, target_unit)
    # For temperature, we use a lambda or special handling since it's not just multiplier
    CONVERSIONS = {
        # Pressure: Target Pa
        "pa": (1.0, 0, "Pa"),
        "kpa": (1000.0, 0, "Pa"),
        "mpa": (1000000.0, 0, "Pa"),
        "bar": (100000.0, 0, "Pa"),
        "atm": (101325.0, 0, "Pa"),

        # Concentration/Ratio: Target decimal (fraction)
        "%": (0.01, 0, "decimal"),
        "ppm": (1e-6, 0, "decimal"),

        # Flow Velocity: Target m/s
        "m/s": (1.0, 0, "m/s"),
        "cm/s": (0.01, 0, "m/s"),
        "mm/s": (0.001, 0, "m/s"),

        # Productivity: Target kg/s (simplified for MVP)
        "kg/h": (1 / 3600.0, 0, "kg/s"),
        "t/year": (1000.0 / (365 * 24 * 3600), 0, "kg/s"),

        # pH is already a log scale and usually doesn't change unit
        "ph": (1.0, 0, "pH"),
    }

    @staticmethod
    def normalize_temperature(value: float, unit: str) -> Tuple[float, str]:
        """
        Special handling for temperature conversions to Kelvin.
        """
        unit = unit.lower().strip()
        if unit in ("c", "°c", "celsius"):
            return value + 273.15, "K"
        elif unit in ("f", "°f", "fahrenheit"):
            return (value - 32) * 5 / 9 + 273.15, "K"
        elif unit in ("k", "kelvin"):
            return value, "K"
        return value, unit

    def normalize(self, value: float, unit: str) -> Tuple[float, str]:
        """
        Normalizes a given value and unit to SI.
        Returns (normalized_value, normalized_unit).
        """
        u_lower = unit.lower().strip()

        # 1. Handle Temperature first as it's non-linear
        if u_lower in ("c", "°c", "celsius", "f", "°f", "fahrenheit", "k", "kelvin"):
            return self.normalize_temperature(value, u_lower)

        # 2. Handle linear conversions from mapping
        if u_lower in self.CONVERSIONS:
            multiplier, offset, target_unit = self.CONVERSIONS[u_lower]
            return (value * multiplier) + offset, target_unit

        # 3. Return as-is if unit is unknown or already SI
        return value, unit
