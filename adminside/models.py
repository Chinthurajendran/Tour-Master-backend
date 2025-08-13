# banners/models.py

from django.db import models
import uuid

class Banner(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')

    def __str__(self):
        return self.name


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name}, {self.country.name}"

    
class TourPackage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    packagetitle = models.CharField(max_length=255)
    source_country_city = models.CharField(max_length=255)   
    destination_country_city = models.CharField(max_length=255)
    description = models.TextField()
    terms_and_conditions = models.TextField()              

    def __str__(self):
        return self.packagetitle

class TourPhoto(models.Model):
    package = models.ForeignKey(TourPackage, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tour_photos/')

    def __str__(self):
        return f"Photo for package: {self.package.packagetitle}"


class PackageSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule_title = models.CharField(max_length=255)
    from_date = models.CharField(max_length=255)   # Ideally use DateField if possible
    to_date = models.CharField(max_length=255)
    amount = models.TextField()
    tour_package = models.ForeignKey(TourPackage,on_delete=models.CASCADE,related_name="schedules")

    def __str__(self):
        return self.schedule_title


class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day = models.CharField(max_length=255)  # Could be IntegerField or DateField depending on usage
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    package_schedule = models.ForeignKey(PackageSchedule, related_name='schedules', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} (Day {self.day})"


class SchedulePhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(Schedule, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tour_photos/')

    def __str__(self):
        return f"Photo for schedule: {self.schedule.title}"
