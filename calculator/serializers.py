from rest_framework import serializers
from .models import RainfallData

class RainfallCalculationRequestSerializer(serializers.Serializer):
    district_name = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Name of the district"
    )
    length = serializers.FloatField(
        min_value=0.1,
        required=True,
        help_text="Rooftop length in meters"
    )
    width = serializers.FloatField(
        min_value=0.1,
        required=True,
        help_text="Rooftop width in meters"
    )

    def validate_district_name(self, value):
        """Validate that district exists in database"""
        if not RainfallData.objects.filter(
            district_name__iexact=value.strip()
        ).exists():
            raise serializers.ValidationError(
                f"District '{value}' not found in our database."
            )
        return value.strip()

class RainfallCalculationResponseSerializer(serializers.Serializer):
    district_name = serializers.CharField()
    state = serializers.CharField()
    annual_rainfall_mm = serializers.FloatField()
    roof_area_sqm = serializers.FloatField()
    water_harvested_liters = serializers.FloatField()
    water_harvested_gallons = serializers.FloatField()
    runoff_coefficient = serializers.FloatField()
    recommendation = serializers.CharField()
    
class RainfallDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RainfallData
        fields = ['district_name', 'annual_rainfall_mm', 'state']
