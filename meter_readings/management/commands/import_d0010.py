from django.core.management.base import BaseCommand
from django.db import transaction

from meter_readings.models import FlowFile, MeterPoint, Meter, Reading
from meter_readings.parser import parse_d0010_file


class Command(BaseCommand):
    help = "Import one or more D0010 flow files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "filepaths",
            nargs="+",
            type=str,
            help="Path(s) to D0010 flow file(s)",
        )

    def handle(self, *args, **options):
        for filepath in options["filepaths"]:
            try:
                self.import_file(filepath)
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Failed to import {filepath}: {e}")
                )

    def import_file(self, filepath: str):
        """Parse and import a single D0010 file."""
        self.stdout.write(f"Importing {filepath}...")

        parsed = parse_d0010_file(filepath)

        reading_count = 0

        with transaction.atomic():
            flow_file = FlowFile.objects.create(
                filename=parsed.filename,
                file_header_id=parsed.file_header_id,
            )

            for mp_data in parsed.meter_points:
                meter_point = MeterPoint.objects.create(
                    flow_file=flow_file,
                    mpan=mp_data.mpan,
                    validation_status=mp_data.validation_status,
                )

                for meter_data in mp_data.meters:
                    meter = Meter.objects.create(
                        meter_point=meter_point,
                        serial_number=meter_data.serial_number,
                        meter_type=meter_data.meter_type,
                    )

                    for reading_data in meter_data.readings:
                        Reading.objects.create(
                            meter=meter,
                            register_id=reading_data.register_id,
                            reading_date=reading_data.reading_date,
                            value=reading_data.value,
                            reading_type=reading_data.reading_type,
                            is_estimated=reading_data.is_estimated,
                        )
                        reading_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(parsed.meter_points)} meter points "
                f"with {reading_count} readings from {parsed.filename}"
            )
        )