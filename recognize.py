# USAGE
# python recognize.py --detector face_detection_model \
#	--embedding-model openface_nn4.small2.v1.t7 \
#	--recognizer output/recognizer.pickle \
#	--le output/le.pickle --image images/adrian.jpg

# import the necessary packages
# import imutils
import numpy as np
import pickle
import time


def recognize(dirname, cursor):
    listUsersIds = []
    similarList = []

    # # Need to change the query because at that time we had not had primary key(UserId) to take so we used the concept of subquery
    query0 = cursor.execute("SELECT UsersDataSet.UserId, "
                                  "(SELECT ProfilePicData From ProfilePicDataSet WHERE ProfilePicDataSet.UserId = '"+dirname+"')"
                              "FROM UsersDataSet").fetchall()
    for row in query0:
        listUsersIds.append(row[0])

    vecdat = query0[0][1]                                #query0 = [('adrian', b'\x80\x03K\x00.'), ('bradly', b'\x80\x03K\x00.'), ('cobie', b'\x80\x03K\x00.'), ('heritik', b'\x80\x03K\x00.'), ('katrina', b'\x80\x03K\x00.'), ('shivay', b'\x80\x03K\x00.'), ('trisha', b'\x80\x03K\x00.'), ('usama', b'\x80\x03K\x00.')]
    vec = pickle.loads(vecdat)

    list_name = []
    list_proba = []
    start = time.time()
    for j in range(len(listUsersIds)):
        query = cursor.execute("SELECT Recognizer, LabelEncoder FROM UsersDataSet WHERE UserId = '"+listUsersIds[j]+"'").fetchall()
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
    dict1 = {"name": list_name, "proba": list_proba}
    return dict1
