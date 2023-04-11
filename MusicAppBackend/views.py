from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
import boto3
import re
from boto3.dynamodb.conditions import Key
from django.http import HttpResponse
from botocore.exceptions import ClientError

@csrf_exempt
def userRegistrationApi(request,id=0):
    if request.method=='POST':
        user_data=JSONParser().parse(request)
        validityString = validPassword(user_data['password'])
        if(validityString != "password is valid") :
            return JsonResponse(validityString,safe=False)

        # email check
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if not re.fullmatch(regex, user_data['email'].strip()):
            return JsonResponse("Please enter a valid email id",safe=False)
        
        email = user_data["email"]
        user_name = user_data["user_name"]
        password = user_data["password"]
        respone = register_user(email, user_name, password)
     
        return JsonResponse(respone,safe=False)

@csrf_exempt
def userLoginApi(request):
    data = JSONParser().parse(request)
    email = data["email"]
    password = data["password"]

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')

    response = table.query(
         KeyConditionExpression=Key('email').eq(email)
    )

    responeItems =  len(response["Items"])

    message = "Login Successfull"
    if(responeItems == 0):
        message = "User does not exist"
        return JsonResponse({"message" : message, "token" : "",  "UserName" : ""}, safe=False)

    responsePassword = response["Items"][0]['password']

    if(password != responsePassword):
        message = "Password is incorrect"
        return JsonResponse({"message" : message, "token" : "",  "UserName" : ""}, safe=False)

    return JsonResponse({"message" : message, "token" : response["Items"][0]["email"],  "UserName" : response["Items"][0]["user_name"]}, safe=False)
    

# get all existing songs from DynamoDB
@csrf_exempt
def allMusicApi(request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('music')
    if request.method=='GET':
        items = table.scan()
        songs = items["Items"]
        return HttpResponse(songs, content_type="application/json")
    
    elif request.method=='POST':
        mapping_data=JSONParser().parse(request)
        title = mapping_data["title"]
        artist = mapping_data["artist"]
        year = mapping_data["year"]
        email = mapping_data["email"]
        dataArrayMusic = []

        if(year != '' and not year.isnumeric()):
            return JsonResponse(dataArrayMusic, safe=False)

        subscibedMusicTitles = []
        if(email != None):
            table = dynamodb.Table('usersubscribedmusic')
            items = table.scan()
            subscribedMusic = items["Items"]
            for music in subscribedMusic:
                subscibedMusicTitles.append(music["music_title"])
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('music')
        items = table.scan()
        songs = items["Items"]
        howManyTrue = 0
        filteredSongs = []
        if(title == '' and artist == '' and year == ''):
            howManyTrue = 3
            filteredSongs = songs
        
        if(title != '' and artist != '' and year != ''):
            howManyTrue = 3
        elif((title != '' and artist != '') or  (title != '' and year != '') or (artist != '' and year != '')):
            howManyTrue = 2
        else:
            howManyTrue = 1
        
        for song in songs:
            if((title != '' and title == song["title"]) and (artist != '' and artist == song["artist"]) and (year != '' and year == song["year"]) and howManyTrue == 3):
                filteredSongs.append(song)
            elif((title != '' and title == song["title"]) and (artist != '' and artist == song["artist"]) and howManyTrue == 2):
                filteredSongs.append(song)
            elif((title != '' and title == song["title"]) and (year != '' and year == song["year"]) and howManyTrue == 2):
                filteredSongs.append(song)
            elif((artist != '' and artist == song["artist"]) and (year != '' and year == song["year"]) and howManyTrue == 2):
                filteredSongs.append(song)
            elif(artist != '' and artist == song["artist"] and howManyTrue == 1):
                filteredSongs.append(song)
            elif(title != '' and title == song["title"] and howManyTrue == 1):
                filteredSongs.append(song)
            elif(year != '' and year == song["year"] and howManyTrue == 1):
                filteredSongs.append(song)
        finalResultSet = []
        for music in  filteredSongs:
            title = music["title"]
            if title in subscibedMusicTitles:
                continue
            finalResultSet.append(music)
            
            # retreiving the url from aws S3 for displaying the image on front end
            s3 = boto3.client('s3', endpoint_url='https://s3.us-east-1.amazonaws.com')
            url = s3.generate_presigned_url('get_object',
                                Params={'Bucket': "application-storage-images", 'Key': title},
                                ExpiresIn=3600,
                                HttpMethod='GET'
                                )
            music["img_url"] = url
        return JsonResponse(finalResultSet, safe=False)

@csrf_exempt
def subscribedMusicApi(request):
    if request.method=='POST':
        mapping_data=JSONParser().parse(request)
        email = mapping_data["email"]
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('usersubscribedmusic')
        response = table.query(
            KeyConditionExpression=Key('user_email').eq(email)
        )

        subscribedMusic = []
        for song in response["Items"]:
            table = dynamodb.Table('music')
            response = table.query(
                KeyConditionExpression=Key('title').eq(song["music_title"])
            )
            subscribedMusic.append(response["Items"][0])

        return JsonResponse(subscribedMusic,safe=False)


@csrf_exempt
def userMusicMapApi(request):
    # get each mapped(subscribed) music for the given user token which is each user's unique email id
    mapping_data=JSONParser().parse(request)
    email = mapping_data["email"]
    title = mapping_data["title"]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('usersubscribedmusic')
    if request.method=='POST':
        response = table.put_item(
            Item={
                'user_email': email,
                'music_title': title
            },
        )
        return JsonResponse("Song subscribed",safe=False)
    if request.method=='DELETE':
        try:
            response = table.delete_item(
                Key={
                    'user_email': email,
                    'music_title': title
                },
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise 
        else:
            return JsonResponse("Song unsubscribed",safe=False)
        

def validPassword(string) :
    if(len(string)  < 7) :
        return "Password length should be of atleast 7 characters"
    if(len(string)  > 14) :
        return "Password length should be not be greater than 14 characters"
    elif(string.isalnum()) :
        return "Password should contain atleast one special character"
    elif(not any(char.isdigit() for char in string)) :
        return "Password should cannot atleast one number"
    return "password is valid"

def register_user(email, user_name, password, dynamodb=None):
    if not dynamodb:
         dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')

    allItems = table.scan()

    for item in allItems['Items']:
        if(email == item['email']):
            return "The email already exists"
    
    response = table.put_item(
        Item={
                'email': email,
                'user_name': user_name,
                'password' : password
        },
    )

    return "Registration successfull"

    