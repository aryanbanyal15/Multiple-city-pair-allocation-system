from django.core.management.base import BaseCommand
from datetime import time

from slots.models import City, Airline, CityPair, BlockTime, Slot


class Command(BaseCommand):
	help = 'Seed sample data (cities, airlines, pairs, block times, slots)'

	def handle(self, *args, **options):
		cities = [
			{'airport_code': 'DEL', 'name': 'Delhi'},
			{'airport_code': 'BOM', 'name': 'Mumbai'},
			{'airport_code': 'BLR', 'name': 'Bangalore'},
			{'airport_code': 'MAA', 'name': 'Chennai'},
			{'airport_code': 'HYD', 'name': 'Hyderabad'},
			{'airport_code': 'CCU', 'name': 'Kolkata'},
			{'airport_code': 'COK', 'name': 'Kochi'},
			{'airport_code': 'PNQ', 'name': 'Pune'},
			{'airport_code': 'GOI', 'name': 'Goa'},
			{'airport_code': 'AMD', 'name': 'Ahmedabad'},
		]
		for c in cities:
			City.objects.get_or_create(airport_code=c['airport_code'], defaults={'name': c['name']})

		airlines = [
			{'name': 'IndiGo', 'code': '6E'},
			{'name': 'Air India', 'code': 'AI'},
			{'name': 'Vistara', 'code': 'UK'},
			{'name': 'SpiceJet', 'code': 'SG'},
			{'name': 'AirAsia India', 'code': 'I5'},
			{'name': 'Go First', 'code': 'G8'},
		]
		for a in airlines:
			Airline.objects.get_or_create(code=a['code'], defaults={'name': a['name']})

		pairs = [
			{'from': 'DEL', 'to': 'BOM', 'duration': time(2, 10)},
			{'from': 'DEL', 'to': 'BLR', 'duration': time(2, 45)},
			{'from': 'DEL', 'to': 'MAA', 'duration': time(2, 30)},
			{'from': 'BOM', 'to': 'BLR', 'duration': time(1, 45)},
			{'from': 'BOM', 'to': 'MAA', 'duration': time(1, 50)},
			{'from': 'BLR', 'to': 'HYD', 'duration': time(1, 15)},
			{'from': 'DEL', 'to': 'HYD', 'duration': time(2, 0)},
			{'from': 'BOM', 'to': 'HYD', 'duration': time(1, 30)},
		]
		for p in pairs:
			from_city = City.objects.get(airport_code=p['from'])
			to_city = City.objects.get(airport_code=p['to'])
			city_pair, _ = CityPair.objects.get_or_create(from_city=from_city, to_city=to_city)
			BlockTime.objects.get_or_create(city_pair=city_pair, defaults={'duration': p['duration']})

		airline_6e = Airline.objects.filter(code='6E').first()
		if airline_6e:
			cp = CityPair.objects.filter(from_city__airport_code='DEL', to_city__airport_code='BOM').first()
			if cp and not Slot.objects.filter(city_pair=cp, airline=airline_6e, slot_time=time(9, 30)).exists():
				Slot.objects.create(city_pair=cp, airline=airline_6e, slot_time=time(9, 30))

		self.stdout.write(self.style.SUCCESS('Seeded sample data.'))

