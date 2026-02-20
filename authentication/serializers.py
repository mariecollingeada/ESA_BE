# authentication/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction


try:
    from .models import Profile
    PROFILE_ROLE_CHOICES = Profile.ROLE_CHOICES
except Exception:
    Profile = None
    PROFILE_ROLE_CHOICES = (
        ('REPORTER', 'Reporter'),
        ('TECHNICIAN', 'Technician'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Admin'),
    )


class RegisterSerializer(serializers.ModelSerializer):
    # password fields are write-only
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    # optional non-model field; client may provide role but it's not a User model field
    role = serializers.ChoiceField(choices=PROFILE_ROLE_CHOICES, write_only=True, required=False)

    class Meta:
        model = User
        # NOTE: do NOT include 'role' here because it's not a field on User model
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2', 'role')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, data):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    @transaction.atomic
    def create(self, validated_data):
        # remove fields not on User
        role = validated_data.pop('role', None)
        validated_data.pop('password2', None)
        password = validated_data.pop('password')

        # create user
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # create or update profile if Profile exists
        if Profile is not None:
            # if role provided, set it, otherwise Profile model default applies
            if role:
                # create profile with chosen role
                Profile.objects.update_or_create(user=user, defaults={'role': role})
            else:
                # ensure profile exists (signal may already create it)
                Profile.objects.get_or_create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    # expose role safely
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')

    def get_role(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.role if profile else None
