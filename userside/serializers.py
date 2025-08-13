from rest_framework import serializers
from .models import *



class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password','is_staff','password']
    
class CustomerenquireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customerenquire
        fields = ['name', 'email', 'phone','message']

