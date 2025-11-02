from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

#User = get_user_model()

class CustomAdminSite(AdminSite):
    site_header = _("Womb & Wonder CMS")
    site_title = _("Womb & Wonder Admin")
    index_title = _("Welcome to the Womb & Wonder Management Portal")

    def has_permission(self, request):
        """
        Control who can access the admin site.
        - Superusers → full access
        - Owners and Supervisors → limited admin access
        - Staff → UI-only (cannot access CMS)
        """
        user = request.user

        if not user.is_authenticated:
            return False  # Must be logged in

        if not user.is_active:
            return False  # Must be active

        # ✅ Superuser: full access
        if user.is_superuser or user.role == "superuser":
            return True

        # ✅ Owners and Supervisors: access to admin site
        if user.role in ["owner", "supervisor"]:
            return True

        # 🚫 Staff or other roles: no access to Django CMS
        return False


custom_admin_site = CustomAdminSite(name="custom_admin")
