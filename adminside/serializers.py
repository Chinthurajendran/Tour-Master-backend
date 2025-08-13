from rest_framework import serializers
from userside.models import *
from .models import*

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'name', 'image']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name']

class CountrySerializer(serializers.ModelSerializer):
    cities = CitySerializer(many = True)
    class Meta:
        model = Country
        fields = ['id','name','cities']

    def create(self, validated_data):
        cities_data = validated_data.pop('cities')
        country  = Country.objects.create(name = validated_data['name'])
        for city_data in cities_data:
            City.objects.create(country = country,**city_data)
        return country
    
    def update(self, instance, validated_data):
        cities_data = validated_data.pop('cities', [])

        # Update country name
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Update cities: 
        # Simplest approach here: delete all existing cities and re-create from input
        instance.cities.all().delete()

        for city_data in cities_data:
            City.objects.create(country=instance, **city_data)

        return instance


class TourPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPhoto
        fields = ['id', 'image']

class TourPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPhoto
        fields = ['image']

class TourPackageSerializer(serializers.ModelSerializer):
    photos = TourPhotoSerializer(many=True, required=False)

    class Meta:
        model = TourPackage
        fields = ['id', 'packagetitle', 'source_country_city', 'destination_country_city', 'description', 'terms_and_conditions', 'photos']

    def create(self, validated_data):
        request = self.context.get('request')
        photos_data = request.FILES.getlist('photos') if request else []
        package = TourPackage.objects.create(**validated_data)
        for photo in photos_data:
            TourPhoto.objects.create(package=package, image=photo)
        return package

class SchedulePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulePhoto
        fields = ['id', 'image']

class ScheduleSerializer(serializers.ModelSerializer):
    photos = SchedulePhotoSerializer(many=True, read_only=True)
    # 'photos' here for read, for writes we handle files separately

    class Meta:
        model = Schedule
        fields = ['id', 'day', 'title', 'description', 'photos']

class PackageScheduleSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True, read_only=True)
    # package = TourPackageSerializer(source='TourPackage', read_only=True)
    tour_package  = TourPackageSerializer(read_only=True)  # field name = FK field name  
    
    class Meta:
        model = PackageSchedule
        fields = ['id', 'schedule_title','from_date', 'to_date', 'amount', 'schedules','tour_package']