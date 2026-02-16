from django.contrib import admin

from meter_readings.models import FlowFile, MeterPoint, Meter, Reading


@admin.register(FlowFile)
class FlowFileAdmin(admin.ModelAdmin):
    list_display = ("filename", "file_header_id", "imported_at")


@admin.register(MeterPoint)
class MeterPointAdmin(admin.ModelAdmin):
    list_display = ("mpan", "validation_status", "flow_file")
    search_fields = ("mpan",)


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "meter_type", "meter_point")
    search_fields = ("serial_number",)


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    """Main admin view for support staff. Lets them search by MPAN or
    meter serial number and see which file the reading came from."""
    list_display = (
        "get_mpan",
        "get_serial_number",
        "register_id",
        "reading_date",
        "value",
        "reading_type",
        "is_estimated",
        "get_filename",
    )
    # double underscores follow the FK chain: Reading -> Meter -> MeterPoint -> mpan
    search_fields = (
        "meter__meter_point__mpan",
        "meter__serial_number",
    )
    # joins everything in one query instead of hitting the db per row
    list_select_related = ("meter__meter_point__flow_file",)
    list_filter = ("reading_date", "is_estimated")

    @admin.display(description="MPAN")
    def get_mpan(self, obj):
        return obj.meter.meter_point.mpan

    @admin.display(description="Meter Serial")
    def get_serial_number(self, obj):
        return obj.meter.serial_number

    @admin.display(description="Source File")
    def get_filename(self, obj):
        return obj.meter.meter_point.flow_file.filename