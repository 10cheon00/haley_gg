from django.contrib import admin

from .models import Match
from .models import Map
from .models import User
from .models import League
from .models import Player


# Register your models here.
admin.site.register(User)
admin.site.register(Map)
admin.site.register(Match)
admin.site.register(Player)
admin.site.register(League)
