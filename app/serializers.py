import django
from django.db import IntegrityError
from rest_framework import serializers
from django.core import exceptions

from app.models import User, Match


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=68, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class MatchSerializer(serializers.ModelSerializer):
    from_user = serializers.ReadOnlyField(source='from_user.username')
    liked_user = serializers.ReadOnlyField(source='liked_user.pk')

    class Meta:
        model = Match
        fields = ('from_user', 'liked_user', 'created_at')

    def create(self, validated_data):
        validated_data['from_user'] = self.context['request'].user
        validated_data['liked_user_id'] = self.context['liked_user_id']
        # print(f'Validated data: {validated_data}')
        # print(validated_data['from_user'])
        # print(validated_data['liked_user_id'])
        try:
            liked_user = User.objects.get(pk=validated_data['liked_user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError({'name': 'Please enter a valid user id'})
        else:
            if liked_user.pk == validated_data['from_user'].pk:
                raise serializers.ValidationError({'error': 'You can\'t create a match with yourself'})
            if Match.objects.filter(from_user=validated_data['from_user'],
                                    liked_user_id=validated_data['liked_user_id']).exists():
                raise serializers.ValidationError({'error': 'You have already liked this user'})
            match = Match.objects.create(
                from_user=validated_data['from_user'],
                liked_user_id=validated_data['liked_user_id'],
            )
            return match
