from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import date

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
        # Only update allowed fields present in your model
        fields_to_update = ["status", "name", "priority"]

        for field in fields_to_update:
            if field in request.data:
                setattr(entry, field, request.data[field])

        # Auto-tag served time when status becomes serving
        if request.data.get("status") == "serving":
            entry.served_at = timezone.now()

        entry.save()
        return Response(QueueSerializer(entry).data)

    def destroy(self, request, *args, **kwargs):
        entry = self.get_object()
        entry.delete()
        return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        # Auto-reset queue once per day
        log, created = QueueResetLog.objects.get_or_create(id=1)
        if log.last_reset != date.today():
            QueueEntry.objects.all().delete()
            log.last_reset = date.today()
            log.save()
        return super().list(request, *args, **kwargs)


# Public QR join (POST only, no auth required)
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


# This endpoint is called when admin clicks "Done".
# It expects the entry already to have status == "serving".
@api_view(["POST"])
@permission_classes([AllowAny])
def serve_patient(request, pk):
    try:
        entry = QueueEntry.objects.get(pk=pk)
    except QueueEntry.DoesNotExist:
        return Response({"error": "Queue entry not found"}, status=404)

    # Ensure it is in serving status first
    if entry.status != "serving":
        return Response(
            {"error": "Patient must be in 'serving' status before marking done."},
            status=400,
        )

    # Save to repository (age/notes not present on QueueEntry in your models)
    QueueRepository.objects.create(
        queue_number=entry.queue_number,
        name=entry.name,
        age=None,
        notes="",
        priority=entry.priority,
        served_at=timezone.now(),
    )

    # Delete from active queue
    entry.delete()

    return Response({"message": "Patient completed and moved to repository."})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_reports(request):
    data = QueueRepository.objects.all().order_by("-served_at")
    return Response(QueueRepositorySerializer(data, many=True).data)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def clear_queue(request):
    QueueEntry.objects.all().delete()
    return Response({"message": "All queue entries cleared"}, status=status.HTTP_204_NO_CONTENT)
