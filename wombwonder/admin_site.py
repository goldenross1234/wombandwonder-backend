from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class CustomAdminSite(AdminSite):
    site_header = _("Womb & Wonder CMS")
    site_title = _("Womb & Wonder Admin")
    index_title = _("Welcome to the Womb & Wonder Management Portal")

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff


custom_admin_site = CustomAdminSite(name="custom_admin")
