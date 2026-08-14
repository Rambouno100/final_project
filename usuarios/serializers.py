from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'password', 'dni', 'telefono', 'area', 'is_active',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': True, 'min_length': 8},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'is_active': {'read_only': True},
        }

    def validate_dni(self, value):
        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError('El DNI debe ser numerico y tener 8 digitos.')
        return value

    def validate_email(self, value):
        # AbstractUser no obliga a que el correo sea unico, lo validamos aqui.
        consulta = get_user_model().objects.filter(email__iexact=value)
        if self.instance:
            consulta = consulta.exclude(pk=self.instance.pk)
        if consulta.exists():
            raise serializers.ValidationError('Ya existe un usuario registrado con ese correo.')
        return value.lower()

    def validate(self, attrs):
        password = attrs.get('password')
        username = attrs.get('username') or getattr(self.instance, 'username', '')
        if password and username and username.lower() in password.lower():
            raise serializers.ValidationError(
                {'password': 'La contrasena no puede contener el nombre de usuario.'}
            )
        return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        usuario = super().update(instance, validated_data)
        if password:
            usuario.set_password(password)
            usuario.save()
        return usuario


class LoginSerializer(TokenObtainPairSerializer):
    """Agrega datos del usuario dentro del access token."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['nombre'] = user.get_full_name()
        token['area'] = user.area
        return token
