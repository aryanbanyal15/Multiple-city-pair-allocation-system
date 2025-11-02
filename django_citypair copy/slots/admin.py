from django.contrib import admin
from .models import City, Airline, CityPair, BlockTime, Slot


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
	list_display = ('name', 'airport_code')
	search_fields = ('name', 'airport_code')


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')
	search_fields = ('name', 'code')


@admin.register(CityPair)
class CityPairAdmin(admin.ModelAdmin):
	list_display = ('from_city', 'to_city')
	search_fields = ('from_city__name', 'to_city__name', 'from_city__airport_code', 'to_city__airport_code')


@admin.register(BlockTime)
class BlockTimeAdmin(admin.ModelAdmin):
	list_display = ('city_pair', 'duration')


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
	list_display = ('city_pair', 'airline', 'slot_time')
	list_filter = ('airline', 'city_pair__from_city', 'city_pair__to_city')

