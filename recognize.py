# USAGE
# python recognize.py --detector face_detection_model \
#	--embedding-model openface_nn4.small2.v1.t7 \
#	--recognizer output/recognizer.pickle \
#	--le output/le.pickle --image images/adrian.jpg

# import the necessary packages
import deploy
import numpy as np
import pickle
import time


def recognize(dirname, db):
    listUsersIds = []
    list_dic = []                           #List To make (<class 'sqlalchemy.util._collections.result'>) type to Bytes
    similarList = []
    i_list = bytes(0)

    # # Query for list of UserId's in a list
    query_ids = db.session.query(deploy.ProfilePicDataSet.UserId)
    for row in query_ids:
        listUsersIds.append(row[0])

    # # Query for certain Person for the Comparison
    query_pic = db.session.query(deploy.ProfilePicDataSet.ProfilePicData).filter_by(UserId=dirname)
    for i in query_pic:
        i_list = i[0]

    list_dic.append(i_list)
    # # vectors for Profile Image to compare to the rest
    vec = pickle.loads(list_dic[0])
    list_dic.clear()

    list_name = []
    list_proba = []
    start = time.time()
    for j in range(len(listUsersIds)):
        # # Query for Loading the Models for every User
        query = db.session.query(deploy.UsersDataSet.Recognizer, deploy.UsersDataSet.LabelEncoder).filter_by(UserId=listUsersIds[j])
        reco = query[0][0]
        lble = query[0][1]
        # load the actual face recognition model along with the label encoder
        recognizer = pickle.loads(reco)
        le = pickle.loads(lble)
        # preds = recognizer.predict_proba(vec)[0]
        preds = recognizer.predict_proba(vec)[0]
        j = np.argmax(preds)
        proba = preds[j]
        name = le.classes_[j]
        # if name != "unknown" and name != dirname:
        #     similarList.append(name)
        #     cursor.execute("""INSERT INTO SimilarPerson(UserId, SimilarPerson) VALUES(?,?)""", (dirname, name))
            # cursor.commit()
        # print(proba)

        if name != "unknown" and name != dirname:
            list_name.append(name)
            list_proba.append(proba*100)
    end = time.time()
    # print(end - start)
    # dict1 = {"name": list_name, "proba": list_proba}
    dict1 = dict(zip(list_name, list_proba))
    return dict1
