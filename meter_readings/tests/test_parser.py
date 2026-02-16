import os
from datetime import datetime

from django.test import TestCase

from meter_readings.parser import parse_d0010_file


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestParser(TestCase):
    """Tests for the D0010 file parser using the sample fixture."""

    def get_fixture_path(self, filename):
        return os.path.join(FIXTURES_DIR, filename)

    def test_parses_file_header(self):
        # check ZHV row is read correctly
        result = parse_d0010_file(self.get_fixture_path("sample.uff"))
        self.assertEqual(result.filename, "sample.uff")
        self.assertEqual(result.file_header_id, "0000475656")

    def test_parses_correct_number_of_meter_points(self):
        # sample has 2 x 026 rows so should find 2 meter points
        result = parse_d0010_file(self.get_fixture_path("sample.uff"))
        self.assertEqual(len(result.meter_points), 2)

    def test_parses_mpan(self):
        # check both MPANs extracted from 026 rows
        result = parse_d0010_file(self.get_fixture_path("sample.uff"))
        self.assertEqual(result.meter_points[0].mpan, "1200023305967")
        self.assertEqual(result.meter_points[1].mpan, "2200031930792")

    def test_parses_meter_serial_number(self):
        # check 028 row fields
        result = parse_d0010_file(self.get_fixture_path("sample.uff"))
        meter = result.meter_points[0].meters[0]
        self.assertEqual(meter.serial_number, "F75A 00802")
        self.assertEqual(meter.meter_type, "D")

    def test_parses_reading_value(self):
        # check 030 row value and register
        result = parse_d0010_file(self.get_fixture_path("sample.uff"))
        reading = result.meter_points[0].meters[0].readings[0]
        self.assertEqual(reading.value, "56311.0")
        self.assertEqual(reading.register_id, "S")

    def test_parses_reading_date(self):
        # 20160222000000 should become 22 Feb 2016
        result = parse_d0010_file(self.get_fixture_path("sample.uff"))
        reading = result.meter_points[0].meters[0].readings[0]
        self.assertEqual(reading.reading_date, datetime(2016, 2, 22, 0, 0, 0))

    def test_meter_with_multiple_readings(self):
        # economy7 meter has 2 registers (day + night), both should attach to same meter
        result = parse_d0010_file(self.get_fixture_path("sample.uff"))
        readings = result.meter_points[1].meters[0].readings
        self.assertEqual(len(readings), 2)
        self.assertEqual(readings[0].register_id, "01")
        self.assertEqual(readings[1].register_id, "02")

    def test_empty_file_raises_error(self):
        # parser should throw ValueError not fail silently
        empty_path = self.get_fixture_path("empty.uff")
        with open(empty_path, "w") as f:
            f.write("")
        with self.assertRaises(ValueError):
            parse_d0010_file(empty_path)
        os.remove(empty_path)