# Kraken D0010 Flow File Importer

**Author: Charles Clayton**

A Django application that imports D0010 meter reading flow files and provides a searchable admin interface for support staff.

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python3 manage.py migrate
```

4. Create a superuser:
```bash
python3 manage.py createsuperuser
```

## Importing D0010 Files

Import one or more D0010 flow files using the management command:
```bash
python3 manage.py import_d0010 path/to/file.uff
```

Multiple files can be imported at once:
```bash
python3 manage.py import_d0010 file1.uff file2.uff file3.uff
```

## Browsing Data

Start the development server:
```bash
python3 manage.py runserver
```

Visit http://127.0.0.1:8000/admin/ and log in. Click on "Readings" to search by MPAN or meter serial number. The source filename is displayed for each reading.

## Running Tests
```bash
python3 manage.py test
```

## Assumptions

- The D0010 file structure follows the pattern: ZHV (header), 026 (meter point), 028 (meter), 030 (reading), ZPT (footer)
- Fields are pipe-delimited with the row type as the first field
- Each 026 row contains one meter point, each 028 row contains one meter, and each 030 row contains one reading
- Reading dates are in YYYYMMDDHHMMSS format
- Importing the same file twice will create duplicate records

## Future Improvements

- REST API endpoint for uploading files via the web
- Duplicate detection to prevent re-importing the same file
- Bulk create for improved import performance on large files
- Pagination and filtering in the admin for large datasets
- CSV export functionality for support staff