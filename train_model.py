# USAGE
# python train_model.py --embeddings output/embeddings.pickle \
#	--recognizer output/recognizer.pickle --le output/le.pickle

# import the necessary packages
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
# from extract_embeddings import embeddings
import pyodbc
import pickle
import time

# """
# SQL SERVER
# """
# conn = pyodbc.connect('Driver={SQL Server};'
#                       'Server=DESKTOP-6PFGOE5;'
#                       'Database=testdb;'
#                       'Trusted_Connection=yes;', autocommit=True)
# cursor = conn.cursor()


def trainModel(data):

    # load the face embeddings
    print("[INFO] loading face embeddings...")

    # encode the labels
    print("[INFO] encoding labels...")
    le = LabelEncoder()
    labels = le.fit_transform(data["names"])

    start = time.time()
    # train the model used to accept the 128-d embeddings of the face and
    # then produce the actual face recognition
    print("[INFO] training model...")
    recognizer = SVC(C=1.0, kernel="linear", probability=True)
    # recognizer = SVC(C=1.0, kernel="poly", degree=8, gamma="auto", probability=True)
    recognizer.fit(data["embeddings"], labels)
    # cursor.execute("""INSERT INTO users(Embedding, LabelEncoder, Recognizer) VALUES(?,?,?)""",
    #                        (pickle.dumps(data['embeddings']),
    #                         pickle.dumps(le),
    #                         pickle.dumps(recognizer)
    #                         )
    #                        )

    end = time.time()
    # print(end - start)
    return data, le, recognizer