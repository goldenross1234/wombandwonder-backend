from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from wombwonder.admin_site import custom_admin_site  # ✅ our custom admin

urlpatterns = [
    path('admin/', custom_admin_site.urls),  # ✅ Womb & Wonder CMS Admin
    path('api/', include('api.urls')),       # ✅ API routes
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
