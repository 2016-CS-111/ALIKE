from os import path
import shutil
import time
import os
import random
# import werkzeug

# Path for the main file location
WORKING_PATH = os.getcwd()

################
# Insert Embeds
################
def file_manage1(dirname):
    path_dataset = WORKING_PATH + '/dataset_' + dirname
    list_of_files = os.listdir(path_dataset)
    if len(list_of_files) < 6:
        print("Please Add 7 Pic at least!")
    return 0

#############################
# Add Profile Pic to Folder
#############################
def file_manage2(img, dirname):
    path_profile = WORKING_PATH + '/profile_' + dirname
    path_dataset = WORKING_PATH + '/dataset_' + dirname

    if not path.isdir(path_dataset):
        os.mkdir(path_dataset)

    if not path.isdir(path_profile):
        os.mkdir(path_profile)
    list_of_files = os.listdir(path_dataset)
    # full_path_profile = [path_profile + '/{0}'.format(x) for x in os.listdir(path_profile)]
    full_path_dataset = [path_dataset + '/{0}'.format(x) for x in list_of_files]
    # if len(list_of_files) <= 6:
    #     print("Please Add 7 Pics at least!")

    if img:
        # if len(os.listdir(path_profile)) > 1:
        #     old_profile = min(full_path_profile, key=os.path.getctime)
        #     os.remove(old_profile)

        ### img_name = secure_filename(img.filename)
        # img_name = werkzeug.secure_filename(img.filename)
        # filename, ext = os.path.splitext(img_name)
        img.filename = 'current.jpg'

        # Renaming in Moving file to dataset from profile image
        # List to keep track of available name files for countering the error caused by os.rename
        repeated_files = []
        for files1 in list_of_files:
            filename, extension = path.splitext(files1)
            repeated_files.append(filename)                     # ['current', 'IMG_022', 'IMG_033', 'IMG_067', 'IMG_090', 'IMG_095']

        for files in list_of_files:
            rand = random.randint(1, 100000)
            filename, extension = os.path.splitext(files)  # filenam = current , extention = .jpg
            if files == (img.filename) or files == (x for x in list_of_files) and (filename not in repeated_files):
                try:
                    os.rename(path_dataset + '/' + files, path_dataset + '/IMG_' + str(rand).zfill(6) + extension)
                except:
                    return "ERROR: in Renaming pic. Please try Again"

        # if Path File is available or not in first time adding profile pic
        if path.isfile(path_profile) and (not path.isfile(path_dataset)):  # Condition for empty dataset folder
            shutil.copy(path_profile + '/' + img.filename, path_dataset)
            img.save(path_profile + "/" + img.filename)
        else:
            img.save(path_profile + "/" + img.filename)
            shutil.copy(path_profile + '/' + img.filename, path_dataset)

        ## Removal of Old Files in Dataset And Renaming them all
        if len(list_of_files) >= 6:
            oldest_file = min(full_path_dataset, key=os.path.getctime)
            os.remove(oldest_file)
    else:
        return "NOT FOUND: Image not selected"

    return "ProfilePic Upload to Folder"

####################################
# Uploading Profile Pic to Database
####################################
def file_manage3(dirname):
    path_profile = WORKING_PATH + '/profile_' + dirname
    return path_profile

###########################
# Deletion of User Profile
###########################
def file_manage4(name):
    path_profile = WORKING_PATH + '/profile_' + name
    path_dataset = WORKING_PATH + '/dataset_' + name
    profile = ''
    dataset = ''
    if os.path.isdir(path_profile):
        shutil.rmtree(path_profile)
        profile = "Profile Directory Removed!"
    else:
        profile = "NOT FOUND: Profile directory not found"
    if os.path.isdir(path_dataset):
        shutil.rmtree(path_dataset)
        dataset = "Dataset Directory Removed!"
    else:
        dataset = "NOT FOUND: Dataset directory not found"
    return profile, dataset

############################
# Comparing Returning Image
############################
def file_manage5(dirname):
    file_image = WORKING_PATH + "\\profile_" + dirname
    return file_image
