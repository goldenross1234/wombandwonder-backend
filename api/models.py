from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from datetime import date
from django.contrib.auth import get_user_model

#User = get_user_model()
from django.conf import settings


# 🩷 SERVICES
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


# 📍 LOCATIONS
class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact = models.CharField(max_length=100)
    hours = models.CharField(max_length=100)
    map_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


# 🎁 PROMOS
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
        """Returns True if the promo is currently active."""
        return self.active and self.start_date <= date.today() <= self.end_date

    def __str__(self):
        return self.title


# 🖼️ HOME BANNERS
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
        """Allow only 5 active banners at a time."""
        if self.active and HomeBanner.objects.filter(active=True).exclude(id=self.id).count() >= 5:
            raise ValidationError("You can only have up to 5 active banners at a time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or f"Banner {self.pk}"


# 💖 HERO SECTION
class HeroSection(models.Model):
    title = models.CharField(max_length=200, default="Healthcare for women, by women.")
    subtitle = models.TextField(
        default="Compassionate, comprehensive care — designed by women, for women. Experience a clinic that understands your journey."
    )
    button_text = models.CharField(max_length=50, default="Explore Our Services")
    image = models.ImageField(upload_to='hero/', blank=True, null=True)
    active = models.BooleanField(default=True)

    # def clean(self):
    #     """Ensure only one active hero section."""
    #     if self.active and HeroSection.objects.filter(active=True).exclude(id=self.id).exists():
    #         raise ValidationError("Only one active Hero Section is allowed at a time.")

    def __str__(self):
        return f"Hero Section - {self.title[:30]}"


# 💝 ABOUT PAGE
class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About Womb & Wonder")
    content = models.TextField()
    image = models.ImageField(upload_to="about/", blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, default="about-us")

    class Meta:
        ordering = ["id"]  # ✅ required by adminsortable2 to define a sort order

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    
# 🌷 Add this model for multiple sections/images
class AboutSection(models.Model):
    about_page = models.ForeignKey(
        'AboutPage',
        on_delete=models.CASCADE,
        related_name='sections'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='about/sections/', blank=True, null=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Section {self.pk}"



# 📰 BLOG POSTS
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
    video_url = models.URLField(blank=True, null=True, help_text="Optional YouTube or MP4 link")
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


# 👥 CUSTOM USER MODEL
class User(AbstractUser):
    ROLE_CHOICES = [
        ("superuser", "Superuser"),
        ("owner", "Owner"),
        ("supervisor", "Supervisor"),
        ("staff", "Staff"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_owner(self):
        return self.role == "owner"

    @property
    def is_supervisor(self):
        return self.role == "supervisor"

    @property
    def is_staff_member(self):
        return self.role == "staff"

    def has_admin_privileges(self):
        return self.role in ["superuser", "owner", "supervisor"]

#For Patients
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    blood_type = models.CharField(max_length=5, blank=True)
    medical_history = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="patients/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name or self.user.username}"
    
# 🩷 1️⃣ Patient Profile
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} (Patient)"


# 🩺 2️⃣ Appointment Management
class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Confirmation"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    time = models.TimeField()
    service = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_appointments")

    def __str__(self):
        return f"{self.patient.user.username} - {self.service} on {self.date}"


# 🔔 3️⃣ Notification System
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


# 📅 4️⃣ Business Calendar
class BusinessDay(models.Model):
    date = models.DateField(unique=True)
    is_open = models.BooleanField(default=True)
    note = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.date} - {'Open' if self.is_open else 'Closed'}"