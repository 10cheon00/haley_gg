from django.contrib import admin

from .Models.maps import Map
from .Models.users import User
from .Models.league_names import LeagueName


# Register your models here.
admin.site.register(User)
admin.site.register(Map)
admin.site.register(LeagueName)
