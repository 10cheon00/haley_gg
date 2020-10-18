from django.contrib import admin

from .Models.maps import Map
from .Models.users import User


# Register your models here.
admin.site.register(User)
admin.site.register(Map)
