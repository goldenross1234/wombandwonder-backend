from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Patient, Appointment, Notification, BusinessDay
from .serializers import PatientSerializer, AppointmentSerializer, NotificationSerializer, BusinessDaySerializer


# 🩷 Patients
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 🩺 Appointments
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "patient_profile"):
            return Appointment.objects.filter(patient=user.patient_profile)
        elif user.has_admin_privileges():
            return Appointment.objects.all()
        return Appointment.objects.none()

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient_profile)


# 🔔 Notifications
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


# 📅 Calendar
class BusinessDayViewSet(viewsets.ModelViewSet):
    queryset = BusinessDay.objects.all().order_by("date")
    serializer_class = BusinessDaySerializer
    permission_classes = [permissions.AllowAny]
