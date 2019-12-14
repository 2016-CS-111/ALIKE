from flask import Flask, jsonify, request, render_template, make_response
from flask_restful import Resource, Api
import file_manage
import profile_img_upload
import extract_embeddings
import recognize
import pyodbc
import pickle

app = Flask(__name__, template_folder='template')
api = Api(app)

"""
SQL SERVER
"""
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-6PFGOE5;'
                      'Database=apitestingfyp;'
                      'Trusted_Connection=yes;', autocommit=True)
cursor = conn.cursor()


class Index(Resource):
    def get(self):
        return make_response(render_template('index.html'))


class InsertEmbeds(Resource):
    def get(self):
        return jsonify({'message': 'Get for Uploading'})

    def post(self):
        name = request.form['name']
        file_manage.file_manage1(name)
        data, le, recognizer = extract_embeddings.embeddings(name)

        # # Need to uncomment below lines for code to work
        cursor.execute("""INSERT INTO UsersDataSet(UserId, Embeddings, LabelEncoder, Recognizer) VALUES(?,?,?,?)""",
                       (
                           name,
                           pickle.dumps(data['embeddings']),
                           pickle.dumps(le),
                           pickle.dumps(recognizer)
                       )
                       )
        return make_response(render_template("index.html", var0='A Person having name %s is added to database' % name))


##################################
# Uploading Profile Pic to Database
##################################
class Uploading(Resource):
    def get(self):
        return jsonify({'message': 'Get for Uploading'})

    def post(self):
        name = request.form['name']
        imagePath = file_manage.file_manage3(name)              # Image Path does not contain filename "current.jpg"
        vec1 = profile_img_upload.imageUpload(name)
        # # Need to uncomment below line for code to work
        cursor.execute("""INSERT INTO ProfilePicDataSet(UserId, ProfilePicData, Image) VALUES(?,?,?)""", (name, pickle.dumps(vec1), imagePath))
        return make_response(render_template('index.html', var1="Post Image of {0} to database".format(name)))

###############################
# ADDING PROFILE PIC TO FOLDER
###############################
class AddPic(Resource):
    def get(self):
        return jsonify({'message': 'Get for AddProfilePic'})

    def post(self):
        dirname = request.form['name']
        img = request.files['image']
        file_manage.file_manage2(img, dirname)
        return make_response(render_template('index.html', var2="Post Method Called For ProfilePic Upload"))


###########################################
# Comparing Profile Pic from database(SQL)
###########################################
class Comparing(Resource):
    def get(self):
        return jsonify({'message': 'Get for AddProfilePic'})

    def post(self):
        # param = request.args
        # id = param.get('name')
        user_id = request.form['name']                            #need to have UserId from database as a primary key or something
        dict1 = recognize.recognize(user_id, cursor)
        # print("PROBABILITY: ", dict1["proba"])
        # print("NAME: ", dict1["name"])
        return make_response(render_template("index.html", var3="Comparison_Prediction: {0}".format(dict1)))




##########################
# API's (ROUTING PART)
##########################
api.add_resource(Index, '/')

# /insertembeds?id=name
api.add_resource(InsertEmbeds, '/insertembeds')


api.add_resource(Uploading, '/uploading')

# /addpic?id=name
api.add_resource(AddPic, '/addpic')

# /comparing?id=name
api.add_resource(Comparing, '/comparing')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
