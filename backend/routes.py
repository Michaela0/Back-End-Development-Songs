from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################

# GET routes
@app.route('/health')
def get_health():
    return jsonify({'status': 'ok'})

@app.route('/count')
def get_count():
    return jsonify({'count': 20})

@app.route('/song', methods=['GET'])
def songs():
    fetched_songs = db.songs.find({})
    songs_list = []
    for song in fetched_songs:
        if 'id' in song:
            song.pop('id')
        # Convert ObjectId to string here
        song['_id'] = str(song['_id'])
        songs_list.append(song)
    return jsonify({'songs': songs_list}), 200


@app.route('/song/<id>', methods=['GET'])
def get_song_by_id(id):
    song = db.songs.find_one({"id": int(id)})
    if not song:
        return jsonify({'message': 'song with id not found'}), 404
    song['_id'] = str(song['_id'])  # convert ObjectId to string
    return jsonify(song), 200

# POST - add new song
@app.route('/song', methods=['POST'])
def create_song():
    song = request.get_json()  # Extract JSON from request body
    
    if not song or 'id' not in song:
        return jsonify({"message": "Invalid song data or missing 'id'"}), 400

    # Check if song with same id already exists
    existing_song = db.songs.find_one({"id": song['id']})
    if existing_song:
        return jsonify({"message": f"song with id {song['id']} already present"}), 302

    # Insert the new song
    result = db.songs.insert_one(song)
    return jsonify({"message": "Song created", "id": str(result.inserted_id)}), 201

# POST - update existing song
@app.route('/song/<int:id>', methods=['PUT'])
def update_song(id):
    # Get JSON data from request
    song = request.get_json()

    # Find existing song by id
    existing_song = db.songs.find_one({'id': id})
    if not existing_song:
        return jsonify({'message': 'song not found'}), 404

    # Update the song document with new data
    db.songs.update_one({'id': id}, {'$set': song})

    # Retrieve the updated song
    updated_song = db.songs.find_one({'id': id})
    updated_song['_id'] = str(updated_song['_id'])  # Convert ObjectId to string for JSON serialization

    # Return updated song as JSON response
    return jsonify(updated_song), 200

# DELETE a song endpoint
@app.route('/song/<int:id>', methods=['DELETE'])
def delete_song(id):
    # Attempt to delete the song with the given id
    result = db.songs.delete_one({'id': id})

    if result.deleted_count == 0:
        # No song found with this id
        return jsonify({'message': 'song not found'}), 404

    # Song deleted successfully, return 204 No Content with empty body
    return '', 204