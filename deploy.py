from flask import Flask, jsonify, request, render_template, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import file_manage
import profile_img_upload
import extract_embeddings
import recognize
import os
import shutil
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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5000/alikeapp'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UsersDataSet(db.Model):
    __tablename__ = "UsersDataSet"
    UserId = db.Column(db.String(50), primary_key=True, nullable=False)
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
    UserId = db.Column(db.String(50), primary_key=True, nullable=False)
    ProfilePicData = db.Column(db.LargeBinary, nullable=False)
    Image = db.Column(db.Text(), nullable=False)

    def __init__(self, UserId, ProfilePicData, Image):
        self.UserId = UserId
        self.ProfilePicData = ProfilePicData
        self.Image = Image


class SimilarPerson(db.Model):
    __tablename__ = "SimilarPerson"
    UserId = db.Column(db.String(50), primary_key=True, nullable=False)
    SimilarPerson = db.Column(db.String(50), nullable=False)

    def __init__(self, UserId, SimilarPerson):
        self.UserId = UserId
        self.SimilarPerson = SimilarPerson


with app.app_context():
    db.create_all()


class Index(Resource):
    def get(self):
        print(jsonify({"message": "Get Method Called"}))
        return make_response(render_template('index.html'))

    def post(self):
        return make_response(render_template('index.html'))


class InsertEmbeds(Resource):
    def get(self):
        return jsonify({'message': 'ERROR: Get for Train, Retry'})

    def post(self):
        name = request.form['name']
        if name:
            file_manage.file_manage1(name)
            data, le, recognizer = extract_embeddings.embeddings(name)
            if db.session.query(UsersDataSet).filter(UsersDataSet.UserId == name).count() == 0:
                db_data = UsersDataSet(name,
                                       pickle.dumps(data['embeddings']),
                                       pickle.dumps(le),
                                       pickle.dumps(recognizer))
                db.session.add(db_data)
                db.session.commit()
                return make_response(render_template("index.html", var0="Model for a Person having name %s is added to database" % name))
            else:
                return make_response(render_template("index.html", var0="ERROR: Same name user found in database while training"))
        else:
            return make_response(render_template("index.html", var0="ERROR: Please Enter Your Name First"))


##################################
# Uploading Profile Pic to Database
##################################
class Uploading(Resource):
    def get(self):
        return jsonify({'message': 'ERROR: Get for Uploading to Database, Retry'})

    def post(self):
        name = request.form['name']
        if name:
            imagePath = file_manage.file_manage3(name)              # Image Path does not contain filename "current.jpg"
            vec1 = profile_img_upload.imageUpload(name)
            # # Need to uncomment below line for code to work
            if db.session.query(ProfilePicDataSet).filter(ProfilePicDataSet.UserId == name).count() == 0:
                db_data = ProfilePicDataSet(name, pickle.dumps(vec1), imagePath)
                db.session.add(db_data)
                db.session.commit()
                return make_response(render_template('index.html', var0="Image of {0} Uploaded to database".format(name)))
            else:
                return make_response(render_template('index.html', var0="ERROR: Same Name while uploading to database!"))
        else:
            return make_response(render_template("index.html", var0="ERROR: Please Enter Your Name First"))


###############################
# ADDING PROFILE PIC TO FOLDER
###############################
class AddPic(Resource):
    def get(self):
        return jsonify({'message': 'ERROR: Get for Upload, Retry'})

    def post(self):
        dirname = request.form['name']
        if dirname:
            img = request.files['image']
            status = file_manage.file_manage2(img, dirname)
            return make_response(render_template('index.html', var0=status))
        else:
            return make_response(render_template("index.html", var0="ERROR: Please Enter Your Name First"))


###########################################
# Comparing Profile Pic from database(SQL)
###########################################
class Comparing(Resource):
    def get(self):
        return jsonify({'message': 'ERROR: Get for Compare, Retry'})

    def post(self):
        # param = request.args
        # id = param.get('name')
        user_id = request.form['name']                            #need to have UserId from database as a primary key or something

        if user_id and not(db.session.query(UsersDataSet).filter_by(UserId=user_id).count() == 0) and not(db.session.query(ProfilePicDataSet).filter_by(UserId=user_id).count() == 0):
            dict1 = recognize.recognize(user_id, db)
            # full_image_path = []
            # for x in dict1.keys():
            #     full_image_path.append(file_manage.file_manage5(x) + "/current.jpg")              # {
            #     # 'katrina': (96.09733319308081, 'C:\\Users\\usama\\Desktop\\Heroku\\App/profile_katrina'),
            #     # 'trisha': (60.28771775012819, 'C:\\Users\\usama\\Desktop\\Heroku\\App/profile_trisha'),
            #     # }

            # dict2 = dict(zip(dict1.keys(), zip(dict1.values(), full_image_path)))
            return make_response(render_template("index.html", data0=dict1))
        else:
            return make_response(render_template("index.html", var0="ERROR: Please make sure you entered your name and pics to input box and database correctly in sequence given", data0={}))


###########################
# Deleting the whole user
###########################
class Deletion(Resource):
    def get(self):
        return jsonify({'message': 'ERROR: Get Method Called for Deletion, Retry'})

    def post(self):
        name = request.form['name']
        if name:
            str1, str2 = file_manage.file_manage4(name)
            if not db.session.query(UsersDataSet).filter_by(UserId=name).count() == 0:
                db_data = UsersDataSet.query.filter_by(UserId=name).one()
                db.session.delete(db_data)
                db.session.commit()
            else:
                return make_response(render_template("index.html", var0="NOT FOUND: Name in Users Database", var1=str1, var2=str2))

            if not db.session.query(ProfilePicDataSet).filter_by(UserId=name).count() == 0:
                db_data = ProfilePicDataSet.query.filter_by(UserId=name).one()
                db.session.delete(db_data)
                db.session.commit()
            else:
                return make_response(render_template("index.html", var0="NOT FOUND: Name in ProfilesPic  Database", var1=str1, var2=str2))

            return make_response(render_template("index.html", var0="User Removed!", var1=str1, var2=str2))

        else:
            return make_response(render_template("index.html", var0="ERROR: Please Enter Your Name First"))


##########################
# API's (ROUTING PART)
##########################
# "https://alikefaceapp.herokuapp.com/"
api.add_resource(Index, '/')

# /insertembeds
# "https://alikefaceapp.herokuapp.com/insertembeds"
api.add_resource(InsertEmbeds, '/insertembeds')

# /uploading
#"https://alikefaceapp.herokuapp.com/uploading"
api.add_resource(Uploading, '/uploading')

# /addpic
#"https://alikefaceapp.herokuapp.com/addpic"
api.add_resource(AddPic, '/addpic')

# /comparing
#"https://alikefaceapp.herokuapp.com/comparing"
api.add_resource(Comparing, '/comparing')

# /deletion
#"https://alikefaceapp.herokuapp.com/deletion"
api.add_resource(Deletion, '/deletion')

if __name__ == '__main__':
    app.run(port=3000)
