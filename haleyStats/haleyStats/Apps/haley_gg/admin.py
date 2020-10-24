from django.contrib import admin

from .Models.maps import Map
from .Models.users import User
from .Models.stats import Match, Player

# Register your models here.
admin.site.register(User)
admin.site.register(Map)
admin.site.register(Match)
admin.site.register(Player)
