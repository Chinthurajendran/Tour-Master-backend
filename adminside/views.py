from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import permissions, status
from userside.models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction
import json
from .models import *


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        return Response({"message": "Admin logged out successfully."}, status=status.HTTP_200_OK)


class FetchUsers(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response({"users": serializer.data}, status=status.HTTP_200_OK)


class BannerUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Banner uploaded successfully", "banner": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Fetchbanner(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = Banner.objects.all()
        serializer = BannerSerializer(users, many=True)
        return Response({"users": serializer.data}, status=status.HTTP_200_OK)


class BannerUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # This tells DRF how to read request.data.
    # MultiPartParser → handles multipart form-data (used for file uploads).
    # FormParser → handles normal form submissions.
    # This is needed because banners often include images.
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, pk):
        # is a shortcut helper from Django.
        # Fetches the banner from the database.
        # If the banner doesn’t exist → 404 Not Found
        banner = get_object_or_404(Banner, pk=pk)
        # With partial=True
        # You can send only the fields you want to change.
        # Missing fields will keep their existing values in the database.
        serializer = BannerSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Deletebanner(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, id):
        try:
            notes = Banner.objects.filter(id=id)
            notes.delete()
            return Response(status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class AddCountryCity(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = CountrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Country & cities added successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FetchCountryCity(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        country = Country.objects.all()
        serializer = CountrySerializer(country, many=True)
        return Response({"country": serializer.data}, status=status.HTTP_200_OK)


class CountryUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def put(self, request, id):
        country = get_object_or_404(Country, pk=id)

        serializer = CountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Country updated successfully", "country": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCountryCity(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, id):
        try:
            country_city = Country.objects.filter(id=id)
            country_city.delete()
            return Response(status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"detail": "country_city not found"}, status=status.HTTP_404_NOT_FOUND)


class TourPackageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # context is an optional dictionary you can pass to the serializer.
        # It’s available inside the serializer via self.context.
        # Why pass the request?
        # Useful if your serializer needs request-specific info.
        # Example: Building full image URLs (request.build_absolute_uri()), or accessing request.user.
        # Some DRF features (like HyperlinkedModelSerializer) require the request in the context to generate proper hyperlinks.
        serializer = TourPackageSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Tour Package uploaded successfully",
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TourPackageList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        packages = TourPackage.objects.all()
        serializer = TourPackageSerializer(packages, many=True)
        return Response({"Package": serializer.data}, status=status.HTTP_200_OK)


class PackageSchedulesAdd(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            package_id = request.data.get('package')
            if not package_id:
                return Response({"error": "Package ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            package = get_object_or_404(TourPackage, id=package_id)
            from_date = request.data.get('from_date')
            to_date = request.data.get('to_date')
            amount = request.data.get('amount')

            # Parse schedules JSON string (sent from frontend)
            schedules_json = request.data.get('schedules')
            if not schedules_json:
                return Response({"error": "Schedules data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            schedules_data = json.loads(schedules_json)

            # Create PackageSchedule
            package_schedule = PackageSchedule.objects.create(
                tour_package=package,
                schedule_title = package,
                from_date=from_date,
                to_date=to_date,
                amount=amount,
            )

            temp_id_map = {}

            for day_obj in schedules_data:
                day = day_obj.get('day')
                for sched in day_obj.get('schedules', []):
                    temp_id = sched.get('id')  # temp ID from frontend

                    schedule_instance = Schedule.objects.create(
                        day=str(day),
                        title=sched.get('title', ''),
                        description=sched.get('description', ''),
                        package_schedule=package_schedule
                    )

                    temp_id_map[temp_id] = schedule_instance

            for file_key in request.FILES:
                # file_key example: '1754924032807vuobchp1i_0'
                temp_id = file_key.split('_')[0]
                file_obj = request.FILES[file_key]

                schedule_instance = temp_id_map.get(temp_id)
                if schedule_instance:
                    SchedulePhoto.objects.create(schedule=schedule_instance, image=file_obj)



            return Response({"message": "Package schedule saved successfully"}, status=status.HTTP_201_CREATED)
        

        # DRF already automatically parses the raw JSON request body into request.data before your view runs.
        # That means request.data is already a Python dict, so you’re skipping the serializer and just:
        # Extracting values manually with .get()
        # Manually creating model objects with .objects.create()
        # The only place you manually do JSON parsing is here:

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PackageSchedulesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        package = PackageSchedule.objects.all()
        serializer = PackageScheduleSerializer(package, many=True)
        return Response({"package": serializer.data}, status=status.HTTP_200_OK)