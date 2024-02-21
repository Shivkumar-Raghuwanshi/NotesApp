from rest_framework import serializers
from .models import Note, NoteHistory
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class NoteSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    shared_with = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'created_at', 'updated_at', 'owner', 'shared_with')

    def get_owner(self, obj):
        user = obj.owner
        return user.get_full_name() or user.username

    def get_shared_with(self, obj):
        users = obj.shared_with.all()
        return [user.get_full_name() or user.username for user in users]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = self.get_owner(instance)
        representation['shared_with'] = self.get_shared_with(instance)
        return representation
    def is_valid(self, raise_exception=False):
        valid = super().is_valid(raise_exception=raise_exception)
        if not valid:
            print(f"Serializer errors: {self.errors}")
        return valid

class NoteHistorySerializer(serializers.ModelSerializer):
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = NoteHistory
        fields = ['id', 'note', 'line_numbers', 'old_content', 'new_content', 'operation', 'updated_at', 'updated_by', 'updated_by_name']

    def get_updated_by_name(self, obj):
        user = User.objects.get(id=obj.updated_by.id)
        return user.username