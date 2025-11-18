from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import date, datetime, timedelta

from api.models import QueueEntry, QueueRepository, QueueResetLog
from api.serializers import QueueSerializer, QueueRepositorySerializer


class QueueViewSet(viewsets.ModelViewSet):
    queryset = QueueEntry.objects.all().order_by("created_at")
    serializer_class = QueueSerializer

    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def perform_create(self, serializer):
        last = QueueEntry.objects.order_by("id").last()
        next_num = (int(last.queue_number.split("-")[1]) + 1) if last else 1
        queue_number = f"A-{next_num:03d}"
        serializer.save(queue_number=queue_number)

    def update(self, request, *args, **kwargs):
        entry = self.get_object()

        # allowed fields
        fields_to_update = ["status", "name", "priority", "selected_service", "age", "notes"]

        for field in fields_to_update:
            if field in request.data:
                setattr(entry, field, request.data[field])

        # auto-set served time
        if request.data.get("status") == "serving":
            entry.served_at = timezone.now()

        entry.save()
        return Response(QueueSerializer(entry).data)

    def destroy(self, request, *args, **kwargs):
        entry = self.get_object()
        entry.delete()
        return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        # auto reset per day
        log, created = QueueResetLog.objects.get_or_create(id=1)
        if log.last_reset != date.today():
            QueueEntry.objects.all().delete()
            log.last_reset = date.today()
            log.save()
        return super().list(request, *args, **kwargs)


# Public QR join
@api_view(["POST"])
@permission_classes([AllowAny])
def join_queue(request):
    last = QueueEntry.objects.order_by("id").last()
    next_num = (int(last.queue_number.split("-")[1]) + 1) if last else 1
    queue_number = f"A-{next_num:03d}"

    entry = QueueEntry.objects.create(
        queue_number=queue_number,
        priority="regular",
        name=request.data.get("name", "Guest"),
        status="waiting",
    )
    return Response(QueueSerializer(entry).data, status=status.HTTP_201_CREATED)


# DONE → move to repository
@api_view(["POST"])
@permission_classes([AllowAny])
def serve_patient(request, pk):
    try:
        entry = QueueEntry.objects.get(pk=pk)
    except QueueEntry.DoesNotExist:
        return Response({"error": "Queue entry not found"}, status=404)

    if entry.status != "serving":
        return Response(
            {"error": "Patient must be in 'serving' status before marking done."},
            status=400,
        )

    QueueRepository.objects.create(
        queue_number=entry.queue_number,
        name=entry.name,
        age=None,
        notes="",
        priority=entry.priority,
        selected_service=entry.selected_service,
        served_at=timezone.now(),
    )

    entry.delete()
    return Response({"message": "Patient completed and moved to repository."})


# 🔥 UPDATED — FILTER + SORT + RANGE for Queue Reports
@api_view(["GET"])
@permission_classes([AllowAny])
def get_reports(request):
    """
    Query params:
      - date= today | yesterday | this_week | this_month
      - from=YYYY-MM-DD & to=YYYY-MM-DD
      - sort= served_at | -served_at | queue_number | -queue_number | name | -name
    """

    qs = QueueRepository.objects.all()

    # ============================
    # 1️⃣ Check custom range first
    # ============================
    date_from = request.query_params.get("from")
    date_to = request.query_params.get("to")

    try:
        if date_from:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        else:
            dt_from = None

        if date_to:
            dt_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        else:
            dt_to = None
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    if dt_from or dt_to:
        # if only one is provided, use same for both
        if dt_from and not dt_to:
            dt_to = dt_from
        if dt_to and not dt_from:
            dt_from = dt_to

        start_dt = timezone.make_aware(datetime.combine(dt_from, datetime.min.time()))
        end_dt = timezone.make_aware(datetime.combine(dt_to, datetime.max.time()))

        qs = qs.filter(served_at__range=(start_dt, end_dt))

    else:
        # ============================
        # 2️⃣ Keyword presets
        # ============================
        date_key = request.query_params.get("date", "today")
        today = timezone.localdate()

        if date_key == "today":
            start = today
            end = today

        elif date_key == "yesterday":
            start = today - timedelta(days=1)
            end = today - timedelta(days=1)

        elif date_key == "this_week":
            start = today - timedelta(days=today.weekday())   # Monday
            end = start + timedelta(days=6)

        elif date_key == "this_month":
            start = today.replace(day=1)
            if start.month == 12:
                next_month = start.replace(year=start.year + 1, month=1, day=1)
            else:
                next_month = start.replace(month=start.month + 1, day=1)
            end = next_month - timedelta(days=1)

        else:
            start = today
            end = today

        start_dt = timezone.make_aware(datetime.combine(start, datetime.min.time()))
        end_dt = timezone.make_aware(datetime.combine(end, datetime.max.time()))

        qs = qs.filter(served_at__range=(start_dt, end_dt))

    # ============================
    # 3️⃣ Sorting
    # ============================
    sort = request.query_params.get("sort")
    allowed_sort = {
        "served_at", "-served_at",
        "queue_number", "-queue_number",
        "name", "-name",
    }

    if sort in allowed_sort:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by("-served_at")  # default

    # Return result
    return Response(QueueRepositorySerializer(qs, many=True).data)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def clear_queue(request):
    QueueEntry.objects.all().delete()
    return Response({"message": "All queue entries cleared"}, status=status.HTTP_204_NO_CONTENT)
