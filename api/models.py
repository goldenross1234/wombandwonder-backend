from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

# ----------------------------------
# 🩷 SERVICES
# ----------------------------------
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.SET_NULL, null=True, related_name="services"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ----------------------------------
# 📍 LOCATIONS
# ----------------------------------
class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact = models.CharField(max_length=100)
    hours = models.CharField(max_length=100)
    map_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


# ----------------------------------
# 🎁 PROMOS
# ----------------------------------
class Promo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to="promos/", blank=True, null=True)
    active = models.BooleanField(default=True)

    @property
    def is_active_now(self):
        return self.active and self.start_date <= date.today() <= self.end_date

    def __str__(self):
        return self.title


# ----------------------------------
# 🖼️ HOME BANNERS
# ----------------------------------
class HomeBanner(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Home Banners"

    def clean(self):
        if self.active and HomeBanner.objects.filter(active=True).exclude(id=self.id).count() >= 5:
            raise ValidationError("You can only have up to 5 active banners at a time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or f"Banner {self.pk}"


# ----------------------------------
# 💖 HERO SECTION
# ----------------------------------
class HeroSection(models.Model):
    title = models.CharField(max_length=200, default="Healthcare for women, by women.")
    subtitle = models.TextField(
        default="Compassionate, comprehensive care — designed by women, for women. Experience a clinic that understands your journey."
    )
    button_text = models.CharField(max_length=50, default="Explore Our Services")
    image = models.ImageField(upload_to='hero/', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Hero Section - {self.title[:30]}"


# ----------------------------------
# 💝 ABOUT PAGE
# ----------------------------------
class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About Womb & Wonder")
    content = models.TextField()
    image = models.ImageField(upload_to="about/", blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, default="about-us")

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AboutSection(models.Model):
    about_page = models.ForeignKey(
        'AboutPage',
        on_delete=models.CASCADE,
        related_name='sections'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.FileField(upload_to='about/sections/', blank=True, null=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Section {self.pk}"


# ----------------------------------
# 📰 BLOG POSTS
# ----------------------------------
class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    content = models.TextField(help_text="Write using Markdown for formatting.")
    cover_image = models.ImageField(upload_to="blog/covers/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ----------------------------------
# 👥 CUSTOM USER MODEL
# ----------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ("superuser", "Superuser"),
        ("owner", "Owner"),
        ("supervisor", "Supervisor"),
        ("staff", "Staff"),
        ("patient", "Patient"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")

    def __str__(self):
        return f"{self.username} ({self.role})"

    def has_admin_privileges(self):
        return self.role in ["superuser", "owner", "supervisor"]


# ----------------------------------
# 🩺 PATIENT MANAGEMENT
# ----------------------------------
# Inside Patient model
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    full_name = models.CharField(max_length=255, blank=True, null=True)  # ✅ Make it optional for now
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    blood_type = models.CharField(max_length=5, blank=True)
    medical_history = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="patients/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # ✅ Add null=True
    updated_at = models.DateTimeField(auto_now=True, null=True)      # ✅ Add null=True

    def __str__(self):
        return f"{self.full_name or self.user.username}"



# ----------------------------------
# 🔔 NOTIFICATION SYSTEM
# ----------------------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


# ----------------------------------
# 🩺 APPOINTMENTS (with auto notifications + email)
# ----------------------------------
class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    time = models.TimeField()
    service = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_appointments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.user.username} - {self.service} on {self.date}"

    def send_notification(self, message):
        Notification.objects.create(user=self.patient.user, message=message)
        send_mail(
            subject="Womb & Wonder Appointment Update",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.patient.user.email],
            fail_silently=True,
        )

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None
        if not is_new:
            old_status = Appointment.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if is_new:
            self.send_notification(
                f"Your appointment for {self.service} on {self.date} has been received and is pending confirmation."
            )
        elif old_status != self.status:
            self.send_notification(
                f"Your appointment for {self.service} on {self.date} was updated to '{self.status}'."
            )


# ----------------------------------
# 📅 BUSINESS CALENDAR
# ----------------------------------
class BusinessDay(models.Model):
    date = models.DateField(unique=True)
    is_open = models.BooleanField(default=True)
    note = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.date} - {'Open' if self.is_open else 'Closed'}"

# ----------------------------------
# 📅 LIVE QUEUEING
# ----------------------------------
class QueueEntry(models.Model):
    PRIORITY_CHOICES = [
        ("regular", "Regular"),
        ("priority", "Priority"),
    ]
    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("serving", "Serving"),
        ("done", "Done"),
        ("no_show", "No Show"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    queue_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, default="Guest")
    age = models.IntegerField(null=True, blank=True)  # ← you already had this in form
    notes = models.TextField(blank=True, null=True)   # ← optional notes
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="regular")
    selected_service = models.CharField(max_length=200, blank=True, null=True)  # ✅ NEW
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="waiting")
    created_at = models.DateTimeField(default=timezone.now)
    served_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.queue_number} - {self.get_status_display()}"
    
class QueueResetLog(models.Model):
    last_reset = models.DateField(auto_now_add=True)

class QueueRepository(models.Model):
    queue_number = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    priority = models.CharField(max_length=20)
    selected_service = models.CharField(max_length=200, blank=True, null=True)  # ✅ NEW
    served_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.queue_number} - {self.name}"