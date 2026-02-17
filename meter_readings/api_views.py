from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from meter_readings.models import FlowFile, MeterPoint, Meter, Reading
from meter_readings.serializers import (
    ReadingSerializer,
    MeterPointListSerializer,
    MeterPointDetailSerializer,
    FlowFileSerializer,
    StatsSerializer,
)
from meter_readings.parser import parse_d0010_file


class ReadingListView(generics.ListAPIView):
    """Search readings by MPAN or serial number."""
    serializer_class = ReadingSerializer
    queryset = Reading.objects.select_related('meter__meter_point__flow_file').all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['meter__meter_point__mpan', 'meter__serial_number']


class ReadingsByDateView(APIView):
    """Readings grouped by date for charts."""
    def get(self, request):
        data = (
            Reading.objects
            .annotate(date=TruncDate('reading_date'))
            .values('date')
            .annotate(count=Count('id'), avg_value=Avg('value'))
            .order_by('date')
        )
        return Response(list(data))


class MeterPointListView(generics.ListAPIView):
    """List all meter points with counts."""
    serializer_class = MeterPointListSerializer
    queryset = (
        MeterPoint.objects
        .select_related('flow_file')
        .annotate(
            meter_count=Count('meters', distinct=True),
            reading_count=Count('meters__readings', distinct=True),
        )
    )
    filter_backends = [filters.SearchFilter]
    search_fields = ['mpan']


class MeterPointDetailView(generics.RetrieveAPIView):
    """Detail view for a single meter point."""
    serializer_class = MeterPointDetailSerializer
    queryset = MeterPoint.objects.select_related('flow_file').prefetch_related('meters__readings')
    lookup_field = 'mpan'

    def get_object(self):
        mpan = self.kwargs['mpan']
        return self.get_queryset().filter(mpan=mpan).first()


class FlowFileListView(generics.ListAPIView):
    """List imported files."""
    serializer_class = FlowFileSerializer
    queryset = (
        FlowFile.objects
        .annotate(
            meter_point_count=Count('meter_points', distinct=True),
            reading_count=Count('meter_points__meters__readings', distinct=True),
        )
        .order_by('-imported_at')
    )


class StatsView(APIView):
    """Dashboard summary stats."""
    def get(self, request):
        data = {
            'total_readings': Reading.objects.count(),
            'total_meter_points': MeterPoint.objects.count(),
            'total_meters': Meter.objects.count(),
            'total_files': FlowFile.objects.count(),
            'estimated_readings': Reading.objects.filter(is_estimated=True).count(),
            'actual_readings': Reading.objects.filter(is_estimated=False).count(),
            'current_meters': Meter.objects.filter(meter_type='C').count(),
            'disconnected_meters': Meter.objects.filter(meter_type='D').count(),
        }
        serializer = StatsSerializer(data)
        return Response(serializer.data)


class FileUploadView(APIView):
    """Upload a D0010 file via the web."""
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)

        import tempfile
        import os
        from django.db import transaction

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.uff') as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            parsed = parse_d0010_file(tmp_path)
            parsed.filename = file.name

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

            return Response({
                'message': f'Imported {len(parsed.meter_points)} meter points with {reading_count} readings',
                'filename': parsed.filename,
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        finally:
            os.unlink(tmp_path)


class LoginView(APIView):
    """Log in with username and password."""
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'username': user.username})
        return Response({'error': 'Invalid credentials'}, status=401)


class LogoutView(APIView):
    """Log out the current user."""
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out'})


class CurrentUserView(APIView):
    """Check if user is logged in."""
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'username': request.user.username})
        return Response({'username': None}, status=401)