# chatbot/utils.py
def harvest_water_cubic_meters(roof_area_m2: float, annual_rainfall_mm: float, runoff_coeff: float) -> float:
    """Calculate annual rainwater harvesting potential in cubic meters."""
    rainfall_m = annual_rainfall_mm / 1000.0
    return roof_area_m2 * rainfall_m * runoff_coeff

def recommend_tank_size(roof_area_m2: float, annual_rainfall_mm: float, runoff_coeff: float, storage_months: int = 2) -> float:
    """Recommend tank size for given storage duration in months."""
    annual_harvest = harvest_water_cubic_meters(roof_area_m2, annual_rainfall_mm, runoff_coeff)
    monthly = annual_harvest / 12.0
    return monthly * storage_months

def plausible_check(value: float):
    """Validate that input values are within plausible ranges."""
    if value < 0 or value > 1e6:
        raise ValueError(f"Value {value} is outside plausible range (0 to 1,000,000)")
    return True
