from flask import Flask, jsonify, request, render_template, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import file_manage
import profile_img_upload
import extract_embeddings
import recognize
# import pyodbc
import pickle

app = Flask(__name__, template_folder='template')
api = Api(app)

"""
FLASK SQLALCHEMY
"""

# # change to dev or prod for development and production respectively
ENV = 'prod'
if ENV == 'prod':
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hsgcsagngxnthk:93a627e4a44e8f1e7b6cedbc7dac1046df54b23ae1411bc12306f54c969be094@ec2-174-129-255-7.compute-1.amazonaws.com:5432/dduu961c9ahm1g'
else:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/alikeapp'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UsersDataSet(db.Model):
    __tablename__ = "UsersDataSet"
    UserId = db.Column(db.String(50), primary_key=True)
    Embeddings = db.Column(db.LargeBinary, nullable=False)
    LabelEncoder = db.Column(db.LargeBinary, nullable=False)
    Recognizer = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, UserId, Embeddings, LabelEncoder, Recognizer):
        self.UserId = UserId
        self.Embeddings = Embeddings
        self.LabelEncoder = LabelEncoder
        self.Recognizer = Recognizer

class ProfilePicDataSet(db.Model):
    __tablename__ = "ProfilePicDataSet"
    UserId = db.Column(db.String(50), primary_key=True)
    ProfilePicData = db.Column(db.LargeBinary, nullable=False)
    Image = db.Column(db.Text(), nullable=False)

    def __init__(self, UserId, ProfilePicData, Image):
        self.UserId = UserId
        self.ProfilePicData = ProfilePicData
        self.Image = Image

class SimilarPerson(db.Model):
    __tablename__ = "SimilarPerson"
    UserId = db.Column(db.String(50), primary_key=True)
    SimilarPerson = db.Column(db.String(50), nullable=False)

    def __init__(self, UserId, SimilarPerson):
        self.UserId = UserId
        self.SimilarPerson = SimilarPerson

with app.app_context():
    db.create_all()

"""
SQL SERVER
"""
# conn = pyodbc.connect('Driver={SQL Server};'
#                       'Server=DESKTOP-6PFGOE5;'
#                       'Database=apitestingfyp;'
#                       'Trusted_Connection=yes;', autocommit=True)
# cursor = conn.cursor()


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

        # Need to uncomment below lines for code to work
        # cursor.execute("""INSERT INTO UsersDataSet(UserId, Embeddings, LabelEncoder, Recognizer) VALUES(?,?,?,?)""",
        #                (
        #                    name,
        #                    pickle.dumps(data['embeddings']),
        #                    pickle.dumps(le),
        #                    pickle.dumps(recognizer)
        #                )
        #                )
        if db.session.query(UsersDataSet).filter(UsersDataSet.UserId == name).count() == 0:
            db_data = UsersDataSet(name,
                                   pickle.dumps(data['embeddings']),
                                   pickle.dumps(le),
                                   pickle.dumps(recognizer))
            db.session.add(db_data)
            db.session.commit()
            return make_response(render_template("index.html", var0='Model for a Person having name %s is added to database' % name))
        else:
            return make_response(render_template("index.html"))


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
        if db.session.query(ProfilePicDataSet).filter(ProfilePicDataSet.UserId == name).count() == 0:
            db_data = ProfilePicDataSet(name, pickle.dumps(vec1), imagePath)
            db.session.add(db_data)
            db.session.commit()
        # cursor.execute("""INSERT INTO ProfilePicDataSet(UserId, ProfilePicData, Image) VALUES(?,?,?)""", (name, pickle.dumps(vec1), imagePath))
            return make_response(render_template('index.html', var1="Image of {0} Uploaded to database".format(name)))
        else:
            return make_response(render_template('index.html')), "Error In Uploading!"

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
        return make_response(render_template('index.html', var2="ProfilePic Upload to Folder"))


###########################################
# Comparing Profile Pic from database(SQL)
###########################################
class Comparing(Resource):
    def get(self):
        return jsonify({'message': 'Get Method Called for AddProfilePic'})

    def post(self):
        # param = request.args
        # id = param.get('name')
        user_id = request.form['name']                            #need to have UserId from database as a primary key or something
        dict1 = recognize.recognize(user_id, db)
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
    app.run(port=3000)
