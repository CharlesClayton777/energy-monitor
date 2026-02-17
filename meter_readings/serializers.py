from rest_framework import serializers
from meter_readings.models import FlowFile, MeterPoint, Meter, Reading


class ReadingSerializer(serializers.ModelSerializer):
    mpan = serializers.CharField(source='meter.meter_point.mpan')
    serial_number = serializers.CharField(source='meter.serial_number')
    filename = serializers.CharField(source='meter.meter_point.flow_file.filename')

    class Meta:
        model = Reading
        fields = ['id', 'mpan', 'serial_number', 'register_id', 'reading_date', 'value', 'reading_type', 'is_estimated', 'filename']


class MeterSerializer(serializers.ModelSerializer):
    reading_count = serializers.SerializerMethodField()

    class Meta:
        model = Meter
        fields = ['id', 'serial_number', 'meter_type', 'reading_count']

    def get_reading_count(self, obj):
        return obj.readings.count()


class MeterPointListSerializer(serializers.ModelSerializer):
    meter_count = serializers.IntegerField(read_only=True)
    reading_count = serializers.IntegerField(read_only=True)
    filename = serializers.CharField(source='flow_file.filename')

    class Meta:
        model = MeterPoint
        fields = ['id', 'mpan', 'validation_status', 'meter_count', 'reading_count', 'filename']


class MeterPointDetailSerializer(serializers.ModelSerializer):
    meters = MeterSerializer(many=True)
    filename = serializers.CharField(source='flow_file.filename')

    class Meta:
        model = MeterPoint
        fields = ['id', 'mpan', 'validation_status', 'filename', 'meters']


class FlowFileSerializer(serializers.ModelSerializer):
    meter_point_count = serializers.IntegerField(read_only=True)
    reading_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = FlowFile
        fields = ['id', 'filename', 'file_header_id', 'imported_at', 'meter_point_count', 'reading_count']


class StatsSerializer(serializers.Serializer):
    total_readings = serializers.IntegerField()
    total_meter_points = serializers.IntegerField()
    total_meters = serializers.IntegerField()
    total_files = serializers.IntegerField()
    estimated_readings = serializers.IntegerField()
    actual_readings = serializers.IntegerField()
    current_meters = serializers.IntegerField()
    disconnected_meters = serializers.IntegerField()