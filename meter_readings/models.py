from django.db import models


class FlowFile(models.Model):
    """Represents an imported D0010 flow file."""
    filename = models.CharField(max_length=255)
    file_header_id = models.CharField(max_length=20)  # from ZHV header row
    imported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class MeterPoint(models.Model):
    """A point of electricity consumption at a property, identified by MPAN.
    Not a physical device - the MPAN stays the same even if the meter is replaced."""
    flow_file = models.ForeignKey(
        FlowFile, on_delete=models.CASCADE, related_name='meter_points'
    )
    mpan = models.CharField(max_length=13)  # 13-digit meter point admin number
    validation_status = models.CharField(max_length=1)

    def __str__(self):
        return self.mpan


class Meter(models.Model):
    """Physical meter installed at a property."""
    meter_point = models.ForeignKey(
        MeterPoint, on_delete=models.CASCADE, related_name='meters'
    )
    serial_number = models.CharField(max_length=20)
    meter_type = models.CharField(max_length=1)  # C = current, D = disconnected

    def __str__(self):
        return self.serial_number


class Reading(models.Model):
    """Single reading from a meter register at a point in time.
    A meter can have multiple registers (e.g. economy7 has day + night)."""
    meter = models.ForeignKey(
        Meter, on_delete=models.CASCADE, related_name='readings'
    )
    register_id = models.CharField(max_length=5)  # 01 = day, 02 = night
    reading_date = models.DateTimeField()
    value = models.DecimalField(max_digits=10, decimal_places=1)
    reading_type = models.CharField(max_length=1, blank=True)
    is_estimated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.meter.serial_number} - {self.value} on {self.reading_date}"