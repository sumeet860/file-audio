from flask import Flask, Response, request, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql.cursors
import json
import bson


app = Flask(__name__)


connection = pymysql.connect
try:
    sql = pymysql.Connect(
        host="localhost",
        user="root",
        password="Sumeet@024",
        database="audio",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    db=sql.autocommit()
    print("Database Connection Successful")
except Exception as e:
    print(e)
    print("Database Connection Failed")



@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,PATCH,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


# Read Audio

@app.route("/audio/read/<audioFileType>/<audioFileID>", methods=["GET"])
def read_file(filetype, id):
    try:
        if(id == 'empty'):
            data = list(db.audiofiles.find({'type': filetype}))
        else:
            data = list(db.audiofiles.find(
                {'_id': bson.ObjectId(oid=str(id)), 'type': filetype}))

        for file in data:
            file["_id"] = str(file["_id"])

        if(json.dumps(data) == '[]'):
            return Response(
                response=json.dumps(
                    {"message": "File not found.Please check the it's id and type"}),
                status=200,
                mimetype="application/json")

        else:
            return Response(
                response=json.dumps(data),
                status=200,
                mimetype="application/json"
            )
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "File not found. Please check it's id and type."}),
            status=500,
            mimetype="application/json")


# Create Audio

@app.route("/audio/create", methods=["POST"])
def AudioFile():
    audiofile = json.loads(request.data.decode())
    print(type(audiofile), audiofile)
    try:
        dbResponse = db.audiofiles.insert_one(audiofile)
        return Response(
            response=json.dumps(
                {"message": "File added successfully.",
                 "id": f"{dbResponse.inserted_id}"
                 }),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        print(e)
        return e


# Update Audio

@app.route("/audio/updateData/<audioFileType>/<audioFileID>", methods=["PATCH"])
def update_file(filetype, id):

    try:
        data = json.loads(request.data.decode())
        newdata = {}
        del data['ID']
        currentdata = (db.audiofiles.find_one(
            {'type': filetype, '_id': bson.ObjectId(oid=str(id))}))
        currentdata = currentdata['metaData']
        for audio in currentdata:
            print("JSON DATA:", data[audio])
            if(data[audio] == ''):
                print("in if")
                newdata[audio] = currentdata[audio]
            else:
                newdata[audio] = data[audio]
        print(newdata)

        dbResponse = db.audiofiles.update_one({'type': filetype, '_id': bson.ObjectId(oid=str(id))}, {'$set': {'metaData': newdata
                                                                                                                   }})
        if(dbResponse.modified_count == 1):
            return Response(
                response=json.dumps({'message': 'Updated', "status": 200}),
                status=200
            )
        else:
            return Response(
                response=json.dumps({"message": "Update cannot be completed. Please check it's ID and Type."}),
                status=200,
                headers="application/json"
            )

    except Exception as e:
        print(e)
        return Response(
            response=json.dumps(
                {"message": "Updation failed.Check it's id and Type.", "status": 500}),
            status=500,  # Internal Server status 500
            mimetype="application/json"
        )



# Delete Audio

@app.route("/audio/delete/<audioFileType>/<audioFileID>", methods=["DELETE"])
def delete_some_file(filetype, id):
    print(id, filetype)
    try:
        dbResponse = db.audiofiles.delete_one(
            {'_id': bson.ObjectId(oid=str(id)), 'type': filetype})
        print(dbResponse.deleted_count)
        if(dbResponse.deleted_count == 0):
            return Response(
                response=json.dumps(
                    {"message": "File does not exist.Unable to delete it.",
                     "id": id,
                     "type": filetype
                     }),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps(
                    {"message": "file deleted successfully.",
                     "id": id,
                     "type": filetype
                     }),
                status=200,
                mimetype="application/json"
            )

    except Exception as e:
        print(e)
        return Response(
            response=json.dumps(
                {"message": "Error.File cannot be deleted.",
                 "id": id,
                 "type": filetype,
                 "status": 500
                 }),
            status=200,
            mimetype="application/json"
        )


if(__name__ == "__main__"):
    app.run(port=80, debug=True)
