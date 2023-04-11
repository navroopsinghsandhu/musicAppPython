from rest_framework import serializers
from MusicAppBackend.models import Users, Music, UserMusicMappings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=Users 
        fields=('UserId','email','user_name', 'password')

class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model=Music
        fields=('MusicId','title','artist','year', 'web_url', 'image_url')

class UserMusicMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserMusicMappings
        fields=('MappingId','UserId','MusicId')
