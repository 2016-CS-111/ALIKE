from os import path
import shutil
import time
import os
import random

#Path for the main file location
WORKING_PATH = os.getcwd()

#Insert Embeds
def file_manage1(dirname):
    path_dataset = WORKING_PATH + '/dataset_' + dirname
    list_of_files = os.listdir(path_dataset)
    if len(list_of_files) < 6:
        print("Please Add 7 Pic at least!")
    return 0



# Add Profile Pic to Folder
def file_manage2(img, dirname):
    path_profile = WORKING_PATH + '/profile_' + dirname
    path_dataset = WORKING_PATH + '/dataset_' + dirname

    if not path.isdir(path_dataset):
        os.mkdir(path_dataset)

    if not path.isdir(path_profile):
        os.mkdir(path_profile)
    list_of_files = os.listdir(path_dataset)
    full_path = [path_dataset + '/{0}'.format(x) for x in list_of_files]
    if len(list_of_files) <= 6:
        print("Please Add 7 Pics at least!")

    if img:
        ### img_name = secure_filename(img.filename)
        img.filename = 'current.jpg'

        #Renaming in Moving file to dataset from profile image
        #List to keep track of available name files for countering the error caused by os.rename
        repeated_files=[]
        var = ""
        for files1 in list_of_files:
            filename, extension = os.path.splitext(files1)
            repeated_files.append(files1[: -len(extension)])
            if 'current' in repeated_files:
                repeated_files.remove('current')

        #for loop for Renaming the files in dataset folder
        for files in list_of_files:
            rand = random.randint(1, 100)
            filename, extension = os.path.splitext(files)   #filenam = current , extention = .jpg
            if files == (img.filename) or files == (x for x in list_of_files) and (filename not in repeated_files):
                os.rename(path_dataset + '/' + files, path_dataset + '/IMG_' + str(rand).zfill(3) + extension)

        #if Path File is available or not in first time adding profile pic
        if path.isfile(path_profile) and (not path.isfile(path_dataset)):       #Condition for empty dataset folder
            shutil.copy(path_profile + '/' + img.filename, path_dataset)
            img.save(path_profile + "/" + img.filename)
        else:
            img.save(path_profile + "/" + img.filename)
            shutil.copy(path_profile + '/' + img.filename, path_dataset)


        ## Removal of Old Files in Dataset And Renaming them all
        if len(list_of_files) >= 6:
            oldest_file = min(full_path, key=os.path.getctime)
            # print(oldest_file)
            os.remove(oldest_file)

    return 0


#Uploading Profile Pic to Database
def file_manage3(dirname):
    path_profile = WORKING_PATH + '/profile_' + dirname
    return path_profile
