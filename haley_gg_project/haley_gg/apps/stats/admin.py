from django.contrib import admin

from haley_gg.apps.stats.models import Result, Map, League, Player, ProleagueTeam

# Register your models here.
admin.site.register(Result)
admin.site.register(Map)
admin.site.register(League)
admin.site.register(Player)
admin.site.register(ProleagueTeam)
