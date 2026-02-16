from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass, field


# dataclasses to hold parsed data before saving to db

@dataclass
class ReadingData:
    register_id: str
    reading_date: datetime
    value: str
    reading_type: str
    is_estimated: bool


@dataclass
class MeterData:
    serial_number: str
    meter_type: str
    readings: list[ReadingData] = field(default_factory=list)


@dataclass
class MeterPointData:
    mpan: str
    validation_status: str
    meters: list[MeterData] = field(default_factory=list)


@dataclass
class FlowFileData:
    filename: str
    file_header_id: str
    meter_points: list[MeterPointData] = field(default_factory=list)


def parse_date(date_string: str) -> datetime:
    """Parse YYYYMMDDHHMMSS format used in D0010 files."""
    return datetime.strptime(date_string, "%Y%m%d%H%M%S")


def parse_d0010_file(filepath: str) -> FlowFileData:
    """Parse a D0010 flow file and return structured data.
    Uses a state machine approach - tracks which meter point and meter
    we're currently inside so readings get attached to the right parent."""
    import os
    filename = os.path.basename(filepath)

    flow_file = None
    current_meter_point = None
    current_meter = None

    with open(filepath, "r") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            fields = line.split("|")
            row_type = fields[0].strip()

            if row_type == "ZHV":
                # file header - grab the sequence id
                file_header_id = fields[1].strip()
                flow_file = FlowFileData(
                    filename=filename,
                    file_header_id=file_header_id,
                )

            elif row_type == "026":
                # new meter point - reset current meter
                if flow_file is None:
                    raise ValueError(f"Line {line_number}: Found 026 row before ZHV header")
                mpan = fields[1].strip()
                validation_status = fields[2].strip()
                current_meter_point = MeterPointData(
                    mpan=mpan,
                    validation_status=validation_status,
                )
                flow_file.meter_points.append(current_meter_point)
                current_meter = None  # important - new meter point means no meter yet

            elif row_type == "028":
                # physical meter under current meter point
                if current_meter_point is None:
                    raise ValueError(f"Line {line_number}: Found 028 row before any 026 row")
                serial_number = fields[1].strip()
                meter_type = fields[2].strip()
                current_meter = MeterData(
                    serial_number=serial_number,
                    meter_type=meter_type,
                )
                current_meter_point.meters.append(current_meter)

            elif row_type == "030":
                # reading - attach to whatever meter is current
                # multiple 030s in a row = multiple registers on same meter
                if current_meter is None:
                    raise ValueError(f"Line {line_number}: Found 030 row before any 028 row")
                register_id = fields[1].strip()
                reading_date = parse_date(fields[2].strip())
                value = fields[3].strip()
                reading_type = fields[6].strip() if len(fields) > 6 else ""
                is_estimated = fields[7].strip() == "E" if len(fields) > 7 else False
                reading = ReadingData(
                    register_id=register_id,
                    reading_date=reading_date,
                    value=value,
                    reading_type=reading_type,
                    is_estimated=is_estimated,
                )
                current_meter.readings.append(reading)

            elif row_type == "ZPT":
                pass  # footer - nothing useful here

    if flow_file is None:
        raise ValueError("No ZHV header found in file")

    return flow_file