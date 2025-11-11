from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from api.models import QueueEntry
from api.serializers import QueueSerializer
from django.utils import timezone
from datetime import date
from api.models import QueueResetLog
from .models import QueueEntry, QueueRepository



class QueueViewSet(viewsets.ModelViewSet):
    queryset = QueueEntry.objects.all().order_by("created_at")
    serializer_class = QueueSerializer

    # ✅ Explicitly allow DELETE (important)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def perform_create(self, serializer):
        last = QueueEntry.objects.order_by("id").last()
        next_num = (int(last.queue_number.split("-")[1]) + 1) if last else 1
        queue_number = f"A-{next_num:03d}"

        # ✅ Save automatically generated number
        serializer.save(queue_number=queue_number)

    def update(self, request, *args, **kwargs):
        entry = self.get_object()

        # ✅ Only update allowed fields
        fields_to_update = ["status", "name", "age", "priority", "notes"]

        for field in fields_to_update:
            if field in request.data:
                setattr(entry, field, request.data[field])

        # ✅ Auto-tag served time
        if request.data.get("status") == "serving":
            entry.served_at = timezone.now()

        entry.save()

        return Response(QueueSerializer(entry).data)

    def destroy(self, request, *args, **kwargs):
        """✅ Allow deleting queue entries properly"""
        entry = self.get_object()
        entry.delete()
        return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    def list(self, request, *args, **kwargs):
        # ✅ Get or create reset log
        log, created = QueueResetLog.objects.get_or_create(id=1)

        # ✅ If a new day → auto-reset queue
        if log.last_reset != date.today():
            QueueEntry.objects.all().delete()
            log.last_reset = date.today()
            log.save()

        return super().list(request, *args, **kwargs)



# ✅ Public QR join (POST only, no auth required)
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
        age=request.data.get("age", None),
        notes=request.data.get("notes", ""),
        status="waiting",
    )

    return Response(QueueSerializer(entry).data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([AllowAny])
def serve_patient(request, pk):
    try:
        entry = QueueEntry.objects.get(pk=pk)
    except QueueEntry.DoesNotExist:
        return Response({"error": "Queue entry not found"}, status=404)

    # ✅ Save to repository (age, notes handled safely)
    QueueRepository.objects.create(
        queue_number=entry.queue_number,
        name=entry.name,
        age=None,            # ✅ QueueEntry has no age
        notes="",            # ✅ QueueEntry has no notes
        priority=entry.priority,
        served_at=timezone.now(),
    )

    # ✅ Delete from QueueEntry AFTER saving history
    entry.delete()

    return Response({"message": "Patient served and moved to repository."})


@api_view(["GET"])
def get_reports(request):
    from api.models import QueueRepository
    data = QueueRepository.objects.all().order_by("-served_at")
    return Response(QueueRepositorySerializer(data, many=True).data)

@api_view(["DELETE"])
def clear_queue(request):
    QueueEntry.objects.all().delete()
    return Response({"message": "All queue entries cleared"}, status=204)
