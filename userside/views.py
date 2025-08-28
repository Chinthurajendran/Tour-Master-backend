from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import permissions, status
from .serializers import *
from .models import *
from rest_framework.exceptions import AuthenticationFailed, ParseError
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
import random
from django.core.mail import send_mail
from .user_auth import RefreshTokenAuth
from adminside.serializers import *

class EmailVerification(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Check if email already registered
            if CustomUser.objects.filter(email=email).exists():
                return Response({"error": "This email is already registered. Please use a different email."},
                                status=status.HTTP_403_FORBIDDEN)

            # Generate 4-digit OTP
            otp = str(random.randint(100000, 999999))

            # Save OTP to database (user=None for now)
            otpdata = CustomUserOTP.objects.create(
                email=email,
                otp=otp
            )
            otpdata.save()

            # Send OTP via email
            subject = "Your Registration OTP"
            message = f"Hello, your OTP for registration is: {otp}"
            from_email = 'chinthurajendran1512@gmail.com'
            recipient_list = [email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                return Response({
                    "message": "OTP sent to your email. Please verify to complete registration.",
                    "otp": otp,
                    "email": email
                    }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": f"Failed to send email. Error: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerification(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            entered_otp = serializer.validated_data['otp']

            try:
                otp_entry = CustomUserOTP.objects.get(email=email)
    

                if str(otp_entry.otp) == str(entered_otp):
                    return Response({"message": "OTP verified successfully!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

            except CustomUserOTP.DoesNotExist:
                return Response({"error": "No OTP found for this email."}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPVerification(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Check if email already registered
            if CustomUser.objects.filter(email=email).exists():
                return Response({"error": "This email is already registered. Please use a different email."},
                                status=status.HTTP_403_FORBIDDEN)

            # Generate 4-digit OTP
            otp = str(random.randint(100000, 999999))

            # Save OTP to database (user=None for now)
            otpdata = CustomUserOTP.objects.create(
                email=email,
                otp=otp
            )
            otpdata.save()

            # Send OTP via email
            subject = "Your Registration OTP"
            message = f"Hello, your OTP for registration is: {otp}"
            from_email = 'chinthurajendran1512@gmail.com'
            recipient_list = [email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                return Response({
                    "message": "OTP sent to your email. Please verify to complete registration.",
                    "otp": otp,
                    "email": email
                    }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": f"Failed to send email. Error: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Register(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            if CustomUser.objects.filter(email=serializer.validated_data['email']).exists():
                return Response({"error": "This email is already registered. Please use a different email."},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                user = CustomUser.objects.create(
                    email=serializer.validated_data['email'],
                    username=serializer.validated_data['username'],
                )
                user.set_password(serializer.validated_data['password'])
                user.save()

                return Response({"message": "Registration successful! Welcome aboard!"},
                                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Admin Login
        if email == "admin@gmail.com" and password == "admin" and CustomUser.objects.filter(email=email).exists():
            user = authenticate(request, username=email, password=password)
            if user is None:
                raise AuthenticationFailed('Invalid Password')

            login(request, user)
            refresh = RefreshToken.for_user(user)
            refresh['username'] = str(user.username)

            content = {
                'admin_access_token': str(refresh.access_token),
                'admin_refresh_token': str(refresh),
                'admin_username': 'Admin',
                'admin_role': 'admin'
            }

            return Response({
                "message": "Login successful",
                **content
            }, status=status.HTTP_200_OK)

        # Normal User Login
        if not CustomUser.objects.filter(email=email).exists():
            raise AuthenticationFailed('Invalid Email Address')

        user = authenticate(request, username=email, password=password)
        if user is None:
            raise AuthenticationFailed('Invalid Password')

        login(request, user)
        refresh = RefreshToken.for_user(user)
        refresh['username'] = str(user.username)

        content = {
            'user_access_token': str(refresh.access_token),
            'user_refresh_token': str(refresh),
            "user_id": str(user.id),
            "user_name": str(user.username),
            'user_role': 'user',
        }

        return Response({
            "message": "Login successful",
            **content
        }, status=status.HTTP_200_OK)

class UserRefreshTokenView(APIView):

    authentication_classes = [RefreshTokenAuth] 
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        refresh_token = request.auth            
        new_access   = refresh_token.access_token
        return Response({"access_token": str(new_access)})



class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)

class PackageDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            country_city = Country.objects.filter(id=id)
            country_city.delete()
            return Response(status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"detail": "country_city not found"}, status=status.HTTP_404_NOT_FOUND)


class PackageDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pkgID):
        package_schedules = PackageSchedule.objects.filter(tour_package__id=pkgID)
        serializer = PackageScheduleSerializer(package_schedules, many=True)
        return Response({"package": serializer.data}, status=status.HTTP_200_OK)


class CustomerenquireAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CustomerenquireSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Customerenquire submitted successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerenquireView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customerdata = Customerenquire.objects.all()
        serializer = CustomerenquireSerializer(customerdata, many=True)
        return Response({"customerdata": serializer.data}, status=status.HTTP_200_OK)
