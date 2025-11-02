from datetime import time, datetime, timedelta
from django.db import transaction
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .models import City, Airline, CityPair, BlockTime, Slot


MAX_SLOTS_PER_AIRLINE = 4
MIN_SLOT_GAP_MINUTES = 30
MAX_SLOTS_PER_HOUR_AT_ORIGIN = 6


def home(request):
	"""Landing page that redirects to the main slot management system"""
	return render(request, 'slots/home.html')


def slot_index(request):
	slots = (
		Slot.objects.select_related('city_pair__from_city', 'city_pair__to_city', 'airline', 'city_pair__block_time')
	)
	cities = City.objects.all()
	airlines = Airline.objects.all()
	context = {
		'slots': [
			{
				'id': s.id,
				'airline': f"{s.airline.name} ({s.airline.code})",
				'from_city': f"{s.city_pair.from_city.name} ({s.city_pair.from_city.airport_code})",
				'to_city': f"{s.city_pair.to_city.name} ({s.city_pair.to_city.airport_code})",
				'slot_time': s.slot_time.strftime('%H:%M:%S'),
				'block_time': s.city_pair.block_time.duration.strftime('%H:%M:%S') if hasattr(s.city_pair, 'block_time') else '',
			}
			for s in slots
		],
		'cities': cities,
		'airlines': airlines,
	}
	return render(request, 'slots/index.html', context)


@require_http_methods(["POST"])
def slot_create(request):
	from_code = request.POST.get('from_city')
	to_code = request.POST.get('to_city')
	airline_code = request.POST.get('airline')
	slot_time_str = request.POST.get('slot_time')
	auto_duration = request.POST.get('auto_duration', '1') == '1'
	manual_block_time_str = request.POST.get('block_time')

	try:
		with transaction.atomic():
			from_city = City.objects.get(airport_code=from_code)
			to_city = City.objects.get(airport_code=to_code)
			airline = Airline.objects.get(code=airline_code)

			city_pair, _ = CityPair.objects.get_or_create(from_city=from_city, to_city=to_city)

			slot_time = datetime.strptime(slot_time_str, '%H:%M').time()

			# Validate rules
			errors = _validate_slot_rules(airline.id, city_pair.id, slot_time)
			if errors:
				raise ValueError("\n".join(errors))

			# Block time
			if auto_duration:
				block_time_val = time(hour=2, minute=10)
				BlockTime.objects.get_or_create(city_pair=city_pair, defaults={'duration': block_time_val})
			else:
				block_time_val = datetime.strptime(manual_block_time_str, '%H:%M').time()
				BlockTime.objects.update_or_create(city_pair=city_pair, defaults={'duration': block_time_val})

			Slot.objects.create(city_pair=city_pair, airline=airline, slot_time=slot_time)

		messages.success(request, 'Slot created successfully')
		return redirect('slots_index')
	except Exception as exc:
		messages.error(request, f'Failed to create slot: {exc}')
		return redirect('slots_index')


@require_http_methods(["POST"])
def slot_update(request, slot_id: int):
	slot = get_object_or_404(Slot, id=slot_id)
	slot_time_str = request.POST.get('slot_time')
	block_time_str = request.POST.get('block_time')

	slot.slot_time = datetime.strptime(slot_time_str, '%H:%M').time()
	slot.save(update_fields=['slot_time'])

	if hasattr(slot.city_pair, 'block_time'):
		slot.city_pair.block_time.duration = datetime.strptime(block_time_str, '%H:%M').time()
		slot.city_pair.block_time.save(update_fields=['duration'])
	else:
		BlockTime.objects.create(city_pair=slot.city_pair, duration=datetime.strptime(block_time_str, '%H:%M').time())

	messages.success(request, 'Slot updated successfully')
	return redirect('slots_index')


@require_http_methods(["POST"])
def slot_delete(request, slot_id: int):
	slot = get_object_or_404(Slot, id=slot_id)
	slot.delete()
	messages.success(request, 'Slot deleted successfully')
	return redirect('slots_index')


def _validate_slot_rules(airline_id: int, city_pair_id: int, slot_time: time) -> list[str]:
	errors: list[str] = []

	# Max slots per airline per city pair
	if Slot.objects.filter(airline_id=airline_id, city_pair_id=city_pair_id).count() >= MAX_SLOTS_PER_AIRLINE:
		errors.append(f"Maximum slots per airline ({MAX_SLOTS_PER_AIRLINE}) reached for this route")

	# Time gap conflicts within city pair
	min_time = (datetime.combine(datetime.today(), slot_time) - timedelta(minutes=MIN_SLOT_GAP_MINUTES)).time()
	max_time = (datetime.combine(datetime.today(), slot_time) + timedelta(minutes=MIN_SLOT_GAP_MINUTES)).time()
	if Slot.objects.filter(city_pair_id=city_pair_id, slot_time__range=(min_time, max_time)).exists():
		errors.append(f"Slot time conflicts with existing slots. Minimum gap required: {MIN_SLOT_GAP_MINUTES} minutes")

	# Max slots per hour at origin airport
	hour_start = time(hour=slot_time.hour, minute=0)
	hour_end = time(hour=slot_time.hour, minute=59, second=59)
	slots_in_hour = Slot.objects.filter(
		city_pair__from_city_id=CityPair.objects.only('from_city_id').get(id=city_pair_id).from_city_id,
		slot_time__range=(hour_start, hour_end)
	).count()
	if slots_in_hour >= MAX_SLOTS_PER_HOUR_AT_ORIGIN:
		errors.append(f"Maximum slots per hour ({MAX_SLOTS_PER_HOUR_AT_ORIGIN}) reached at origin airport")

	return errors

