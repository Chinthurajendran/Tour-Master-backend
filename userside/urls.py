from django.urls import path
from .views import*

urlpatterns = [
    path('verify-email', EmailVerification.as_view(), name='verify-email'),
    path('OTPVerification', OTPVerification.as_view(), name='OTPVerification'),
    path('ResendOTPVerification', ResendOTPVerification.as_view(), name='ResendOTPVerification'),
    path('Register', Register.as_view(), name='Register'),
    path('LoginView', LoginView.as_view(), name='LoginView'),
    path("user_logout", UserLogoutView.as_view(), name="user_logout"),
    path('PackageDetails/<uuid:pkgID>/', PackageDetails.as_view(), name='PackageDetails'),
    path("Customerenquire", CustomerenquireAPIView.as_view(), name="Customerenquire"),
    path("CustomerenquireView", CustomerenquireView.as_view(), name="CustomerenquireView"),
]