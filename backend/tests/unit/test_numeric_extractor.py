import pytest
from app.services.nlp.numeric_extractor import NumericExtractor, NumericValue
from app.services.nlp.unit_normalizer import UnitNormalizer

def test_numeric_extraction_basic():
    extractor = NumericExtractor()
    text = "Температура 65 °C, давление 2 bar, pH 4.5"
    results = extractor.extract(text)

    assert len(results) == 3
    # Temp
    assert results[0].property_name == "temperature"
    assert results[0].value == 65.0
    assert results[0].unit == "°C"

    # Press
    assert results[1].property_name == "pressure"
    assert results[1].value == 2.0
    assert results[1].unit == "bar"

    # pH
    assert results[2].property_name == "ph"
    assert results[2].value == 4.5
    assert results[2].unit == ""

def test_numeric_extraction_english():
    extractor = NumericExtractor()
    text = "Temperature: 100 C, Pressure: 101.3 kPa, Flow velocity 0.5 m/s"
    results = extractor.extract(text)

    assert len(results) == 3
    assert results[0].property_name == "temperature"
    assert results[0].value == 100.0
    assert results[0].unit == "C"

    assert results[1].property_name == "pressure"
    assert results[1].value == 101.3
    assert results[1].unit == "kPa"

def test_numeric_extraction_comma_decimal():
    extractor = NumericExtractor()
    text = "Концентрация 5,5 %"
    results = extractor.extract(text)

    assert len(results) == 1
    assert results[0].value == 5.5

def test_unit_normalization_temperature():
    normalizer = UnitNormalizer()

    # Celsius to Kelvin
    val, unit = normalizer.normalize(65.0, "°C")
    assert val == pytest.approx(338.15)
    assert unit == "K"

    # Fahrenheit to Kelvin
    val, unit = normalizer.normalize(100.0, "°F")
    assert val == pytest.approx((100 - 32) * 5/9 + 273.15)
    assert unit == "K"

def test_unit_normalization_pressure():
    normalizer = UnitNormalizer()

    # bar to Pa
    val, unit = normalizer.normalize(2.0, "bar")
    assert val == 200000.0
    assert unit == "Pa"

    # atm to Pa
    val, unit = normalizer.normalize(1.0, "atm")
    assert val == 101325.0
    assert unit == "Pa"

def test_unit_normalization_velocity():
    normalizer = UnitNormalizer()

    # m/s to m/s (already SI)
    val, unit = normalizer.normalize(0.5, "m/s")
    assert val == 0.5
    assert unit == "m/s"

def test_unit_normalization_unknown():
    normalizer = UnitNormalizer()
    # Should return as-is if unknown
    val, unit = normalizer.normalize(10.0, "unknown_unit")
    assert val == 10.0
    assert unit == "unknown_unit"
