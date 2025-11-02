from django.db import models


class City(models.Model):
	name = models.CharField(max_length=255)
	airport_code = models.CharField(max_length=10, unique=True)

	def __str__(self) -> str:
		return f"{self.name} ({self.airport_code})"


class Airline(models.Model):
	name = models.CharField(max_length=255)
	code = models.CharField(max_length=10, unique=True)

	def __str__(self) -> str:
		return f"{self.name} ({self.code})"


class CityPair(models.Model):
	from_city = models.ForeignKey(City, related_name='routes_from', on_delete=models.CASCADE)
	to_city = models.ForeignKey(City, related_name='routes_to', on_delete=models.CASCADE)

	class Meta:
		unique_together = ('from_city', 'to_city')

	def __str__(self) -> str:
		return f"{self.from_city.airport_code} -> {self.to_city.airport_code}"


class BlockTime(models.Model):
	city_pair = models.OneToOneField(CityPair, related_name='block_time', on_delete=models.CASCADE)
	duration = models.TimeField()

	def __str__(self) -> str:
		return f"{self.city_pair}: {self.duration}"


class Slot(models.Model):
	city_pair = models.ForeignKey(CityPair, related_name='slots', on_delete=models.CASCADE)
	airline = models.ForeignKey(Airline, related_name='slots', on_delete=models.CASCADE)
	slot_time = models.TimeField()

	def __str__(self) -> str:
		return f"{self.airline} @ {self.slot_time} on {self.city_pair}"

