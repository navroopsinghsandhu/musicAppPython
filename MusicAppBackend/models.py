from django.db import models

class Users(models.Model):
    class Meta:
        db_table = 'users'
    UserId = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=500)
    user_name = models.CharField(max_length=500)
    password = models.CharField(max_length=500)

class Music(models.Model):
    class Meta:
        db_table = 'music'
    MusicId = models.AutoField(primary_key=True)
    title = models.CharField(unique=True, max_length=500)
    artist = models.CharField(unique=True, max_length=500)
    year = models.IntegerField()
    web_url = models.CharField(unique=True, max_length=500)
    image_url = models.CharField(unique=True, max_length=500)

class UserMusicMappings(models.Model):
    class Meta:
        db_table = 'user_music_mappings'
    MappingId = models.AutoField(primary_key=True)
    UserId = models.IntegerField()
    MusicId = models.IntegerField()

