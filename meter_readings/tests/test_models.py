from datetime import datetime

from django.test import TestCase

from meter_readings.models import FlowFile, MeterPoint, Meter, Reading


class TestFlowFileModel(TestCase):

    def test_str(self):
        flow_file = FlowFile.objects.create(
            filename="test.uff", file_header_id="123"
        )
        self.assertEqual(str(flow_file), "test.uff")


class TestMeterPointModel(TestCase):

    def test_str(self):
        flow_file = FlowFile.objects.create(
            filename="test.uff", file_header_id="123"
        )
        meter_point = MeterPoint.objects.create(
            flow_file=flow_file, mpan="1234567890123", validation_status="V"
        )
        self.assertEqual(str(meter_point), "1234567890123")


class TestMeterModel(TestCase):

    def test_str(self):
        flow_file = FlowFile.objects.create(
            filename="test.uff", file_header_id="123"
        )
        meter_point = MeterPoint.objects.create(
            flow_file=flow_file, mpan="1234567890123", validation_status="V"
        )
        meter = Meter.objects.create(
            meter_point=meter_point, serial_number="ABC123", meter_type="C"
        )
        self.assertEqual(str(meter), "ABC123")


class TestReadingModel(TestCase):

    def test_str(self):
        # need to create the full chain since each model depends on its parent
        flow_file = FlowFile.objects.create(
            filename="test.uff", file_header_id="123"
        )
        meter_point = MeterPoint.objects.create(
            flow_file=flow_file, mpan="1234567890123", validation_status="V"
        )
        meter = Meter.objects.create(
            meter_point=meter_point, serial_number="ABC123", meter_type="C"
        )
        reading = Reading.objects.create(
            meter=meter,
            register_id="S",
            reading_date=datetime(2016, 2, 22),
            value=56311.0,
            reading_type="T",
            is_estimated=False,
        )
        self.assertIn("ABC123", str(reading))