from flask import Flask, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId

import json, hashlib, jwt, datetime, uuid

# client = MongoClient("mongodb+srv://Naga12031998:hurricane13@instacardb-qlyyy.mongodb.net/test?retryWrites=true&w=majority")
# db = client.get_database('instaCar')
# users = db.users
# hashTags = db.hashTags

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb+srv://Naga12031998:hurricane13@instacardb-qlyyy.mongodb.net/test?retryWrites=true&w=majority"
# app.config["MONGO_URI"] = "mongodb://localhost:27017/instaCar"
mongo = PyMongo(app)

# SIGN UP
@app.route('/auth/signup', methods = ['POST'])
def register():
    name = request.json['name']
    userName = request.json['userName']
    email = request.json['email']
    passwordHash = request.json['password']
    passwordHash = md5_hash(passwordHash)

    checkUser = mongo.db.users.find({'email' : email, 'userName' : userName}).count()

    if checkUser == 0:
        mongo.db.users.insert_one({'userName' : userName, 'email' : email, 'passwordHash' : passwordHash, 'name' : name, 'picture' : '', 'coverPicture' : '', 'bio' : '', 'location' : '', 'webSite' : '', 'birthDate' : '', 'followers' : [], 'following' : [], 'tweets' : [], 'whatsHappening' : [], 'hashTagTweets' : []})
        return {"status": 'User created successfully'}
    else:
        return {"status" : 'email already taken' }

# LOGIN
@app.route('/auth/login', methods = ['POST'])
def signin():
    email = request.json['email']
    password = request.json['password']
    check = md5_hash(password)

    checkUser = mongo.db.users.find({"email" : email, "passwordHash" : check}).count()

    if checkUser == 0:
        return {"status" : 401}
    else:
        encode_data = jwt.encode({'email' : email}, 'naga' , algorithm='HS256').decode('utf-8')
        return {"status": str(encode_data)} 

# HASHING
def md5_hash(string):
    hash = hashlib.md5()
    hash.update(string.encode('utf-8'))
    hash.hexdigest()
    return hash.hexdigest()

# SETTING UP PROFILE PIC
@app.route('/updateprofilepic', methods = ['PATCH'])
def updateProfilepicture():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    image = request.files['image']
    location = "static/img/" + image.filename
    image.save(location)
    imgLocation = location

    mongo.db.users.update({"email": decoded_data['email']}, {"$set": {'picture' : location}})
    return {"Status": 200 }

# UPDATE USER DETAILS
@app.route('/updateuserdeatils', methods=['PATCH'])
def updateUserDetails():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    bio = request.json['bio']
    location = request.json['location']
    webSite = request.json['webSite']
    birthDate = request.json['birthDate']

    mongo.db.users.update({"email": decoded_data['email']}, {"$set": {'bio' : bio, 'location' : location, 'birthDate' : birthDate, 'webSite' : webSite}})
    return {'status' : 200}

# TWEET
@app.route('/tweet', methods=['POST'])
def tweet():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')
    getUserName = mongo.db.users.find({'email' : decoded_data['email']})

    x = datetime.datetime.now()
    day = int(x.strftime('%d'))
    month = str(x.strftime('%b'))
    year = int(x.strftime('%Y'))

    id = uuid.uuid1()
    tweetId = id.hex
    tweet = request.headers.get('tweet')
    image = request.files['image']
    location = "static/img/" + image.filename
    image.save(location)
    imgLocation = location

    mongo.db.users.update({'email' : decoded_data['email']}, {'$push' :{'tweets' : {'tweetId' : tweetId, 'tweet' : tweet, 'picture' : imgLocation, 'day' : day, 'month' : month, 'year' : year, 'postedBy' : getUserName[0]['name']}}})
    return {'status' : 200}

# WHATS HAPPENING
@app.route('/whatshappening', methods=['POST'])
def whatsHappening():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    x = datetime.datetime.now()
    day = int(x.strftime('%d'))
    month = str(x.strftime('%b'))
    year = int(x.strftime('%Y'))

    id = uuid.uuid1()
    whatId = id.hex
    what = request.json['what']

    mongo.db.users.update({'email' : decoded_data['email']}, {'$push' :{'whatsHappening' : {'whatId' : whatId,'what' : what, 'day' : day, 'month' : month, 'year' : year}}})
    return {'status' : 200}

# HASH TAG TWEETS
@app.route('/hashtagtweets', methods=['POST'])
def hashTagTweets():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    getUserName = mongo.db.users.find({'email' : decoded_data['email']})

    x = datetime.datetime.now()
    day = int(x.strftime('%d'))
    month = str(x.strftime('%b'))
    year = int(x.strftime('%Y'))

    id = uuid.uuid1()
    tweetId = id.hex
    hashTag = request.headers.get('hashTag')
    tweet = request.headers.get('tweet')
    image = request.files['image']
    location = "static/img/" + image.filename
    image.save(location)
    imgLocation = location

    mongo.db.users.update({'email' : decoded_data['email']}, {'$push' : {'hashTagTweets' : {'hashTag' : hashTag, 'tweetId' : tweetId, 'tweet' : tweet,'picture' : imgLocation, 'day' : day, 'month' : month, 'year' : year}}})

    getHashTag = mongo.db.hashTags.find({'hashTag' : hashTag}).count()

    if getHashTag == 0:
        mongo.db.hashTags.insert_one({'hashTag' : hashTag, 'hashTagTweets' : [{ 'tweetId' : tweetId,'tweet' : tweet, 'name' : getUserName[0]['name'], 'picture' : imgLocation, 'day' : day, 'month' : month, 'year' : year}]})
    else:
        mongo.db.hashTags.update({'hashTag': hashTag}, {'$push' : {'hashTagTweets' : {'tweetId' : tweetId, 'tweet' : tweet, 'name' : getUserName[0]['name'], 'picture' : imgLocation, 'day' : day, 'month' : month, 'year' : year}}})

    return {'status' : 200}

# DELETE TWEETS
@app.route('/deletetweets/<_id>', methods=['DELETE'])
def deleteTweets(_id):
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    mongo.db.users.update({'email' : decoded_data['email']}, { '$pull': {'tweets': {'tweetId' : _id} }})
    return {'status' : 200}

# DELETE WHATSHAPPENING
@app.route('/deletewhatshappening/<_id>', methods=['DELETE'])
def deleteWhatsHappening(_id):
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    mongo.db.users.update({'email' : decoded_data['email']}, { '$pull': {'whatsHappening': {'whatId' : _id} }})
    return {'status' : 200}

# DELETE HASHTAGTWEETS
@app.route('/deletehashtagtweets/<_id>', methods=['DELETE'])
def deleteHashTagTweets(_id):
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    mongo.db.users.update({'email' : decoded_data['email']}, { '$pull': {'hashTagTweets': {'tweetId' : _id} }})
    mongo.db.hashTags.update({ }, { '$pull': {'hashTagTweets': {'tweetId' : _id} }})
    return {'status' : 200}

# GET LOGGED IN USER
@app.route('/getuser')
def getUser():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    user = mongo.db.users.find({'email' : decoded_data['email']})

    return dumps(user)

# GET ALL USERS[EXPECT LOGGED IN USER AND FOLLOWING USERS]:
@app.route('/getalluser/expect/loggedin/followinguser')
def getAllusersELAF():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    arr = []
    getLoggedInUser = mongo.db.users.find({'email' : decoded_data['email']})
    getAllusers = mongo.db.users.find()
    array = getLoggedInUser[0]['following']
    for i in getAllusers:
        if i['name'] not in array and i['name'] != getLoggedInUser[0]['name']:
            arr.append(i)

    return dumps(arr)

# FOLLOW USER
@app.route('/followusers/<name>', methods = ['PATCH'])
def followUsers(name):
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    getUserData = mongo.db.users.find({'email' : decoded_data['email']}) 

    mongo.db.users.update({'email' : decoded_data['email']}, {'$push' : {'following' : name}})
    mongo.db.users.update({'name' : name}, {'$push' : {'followers' : getUserData[0]['name']}})
    return {'status' : 200}

# GET ALL FOLLOWING USER[EXPECT LOGGED IN USER]:
@app.route('/getalluser/followinguser/expect/loggedin')
def getAllusersFEL():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    arr = []
    getLoggedInUser = mongo.db.users.find({'email' : decoded_data['email']})
    for j in getLoggedInUser[0]['following']:
        arr.append(j)
            
    return dumps(arr)

# GET ALL FOLLOWERS
@app.route('/getallfollowers')
def getAllFollowers():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    arr = []
    getLoggedInUser = mongo.db.users.find({'email' : decoded_data['email']})
    for j in getLoggedInUser[0]['followers']:
        arr.append(j)
            
    return dumps(arr)

# UNFOLLOW USERS
@app.route('/unfollowusers/<name>', methods=['PATCH'])
def unfollowUsers(name):
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    getUserData = mongo.db.users.find({'email' : decoded_data['email']}) 

    mongo.db.users.update({'email' : decoded_data['email']}, {'$pull' : {'following' : name}})
    mongo.db.users.update({'name' : name}, {'$pull' : {'followers' : getUserData[0]['name']}})
    return {'status' : 200}

# GET ALL HASHTAGS
@app.route('/getallhastags')
def getAllHashtags():
    getAll= mongo.db.hashTags.find()
    return dumps(getAll)

# SEARCH HASTAG TWEETS
@app.route('/searchhashtag/<hashtag>')
def seatchHashTag(hashtag):
    getData = mongo.db.hashTags.find({'hashTag' : hashtag})
    return dumps(getData)

# GET ALL TWEETS OF FOLLOWING USER
@app.route('/getdata/followinguser')
def getDataOfFollowingUser():
    auth_header = request.headers.get('Authorization')
    token_encoded = auth_header.split(' ')[1]
    decoded_data = jwt.decode(token_encoded, 'naga', algorithm='HS256')

    getUserData = mongo.db.users.find({'email' : decoded_data['email']})
    array = getUserData[0]['following'] 
    getTweets = []
    getAllusers = mongo.db.users.find()

    for i in getAllusers:
        if i['name'] in array:
            getTweets.append(i['tweets'])
    return dumps(getTweets)