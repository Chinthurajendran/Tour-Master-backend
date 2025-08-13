from django.urls import path
from .views import*

urlpatterns = [
    path("admin_logout", AdminLogoutView.as_view(), name="admin_logout"),
    path("fetch-users", FetchUsers.as_view(), name="fetch-users"),
    path('upload-banner', BannerUploadView.as_view(), name='upload-banner'),
    path('fetch-banner', Fetchbanner.as_view(), name='fetch-banner'),
    path('delete-banner/<int:id>/', Deletebanner.as_view(), name='delete-banner'),
    path('update-banner/<int:pk>/', BannerUpdateView.as_view(), name='update-banner'),
    path('adding-countries', AddCountryCity.as_view(), name='adding-countries'),
    path('fetch-countries', FetchCountryCity.as_view(), name='fetch-countries'),
    path('update-countries/<uuid:id>/', CountryUpdateView.as_view(), name='update-countries'),
    path('delete-countries/<uuid:id>/', DeleteCountryCity.as_view(), name='delete-countries'),
    path('Add-TourPackage', TourPackageView.as_view(), name='Add-TourPackage'),
    path('admin-tourpackages', TourPackageList.as_view(), name='admin-tourpackages'),
    path('PackageSchedulesadd', PackageSchedulesAdd.as_view(), name='PackageSchedulesadd'),
    path('PackageSchedulesview', PackageSchedulesView.as_view(), name='PackageSchedulesview'),
]