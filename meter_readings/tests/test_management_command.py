import os
from django.test import TestCase
from django.core.management import call_command

from meter_readings.models import FlowFile, MeterPoint, Meter, Reading


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestImportCommand(TestCase):

    def test_imports_file_successfully(self):
        filepath = os.path.join(FIXTURES_DIR, "sample.uff")
        call_command("import_d0010", filepath)

        self.assertEqual(FlowFile.objects.count(), 1)
        self.assertEqual(MeterPoint.objects.count(), 2)
        self.assertEqual(Meter.objects.count(), 2)
        self.assertEqual(Reading.objects.count(), 3)

    def test_imported_data_is_correct(self):
        filepath = os.path.join(FIXTURES_DIR, "sample.uff")
        call_command("import_d0010", filepath)

        flow_file = FlowFile.objects.first()
        self.assertEqual(flow_file.filename, "sample.uff")

        meter_point = MeterPoint.objects.get(mpan="1200023305967")
        self.assertEqual(meter_point.flow_file, flow_file)

        meter = Meter.objects.get(serial_number="F75A 00802")
        self.assertEqual(meter.meter_point, meter_point)

    def test_handles_invalid_file_gracefully(self):
        # Should not raise an exception, just print an error
        call_command("import_d0010", "/nonexistent/file.uff")
        self.assertEqual(FlowFile.objects.count(), 0)