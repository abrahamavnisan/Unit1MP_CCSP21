from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

import requests
import pandas as pd

from PIL import Image, ImageOps
import imghdr

import os

# /////////////////////////
# PARAMS //////////////////
# /////////////////////////

spreadsheetID = '1PsFwKs18p0OEqpQ3WnuvwErIi55Zp9sVBPOXiHvH3qA' # Gallery Submission Response Sheet
savedSheetName = 'MicroProjectGallery/unit1MicroProjects.csv'
downloadCSV = False
downloadImages = False
verbose = True

# /////////////////////////
# DEFS ////////////////////
# /////////////////////////

def download_file_from_google_drive(id, destination):
    
    # https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def cropImage(image, path):
    print("cropping image with path: " + path)
    width, height = image.size
    # print("width: " + str(width) + " height: " + str(height))
    diff = abs(height - width)

    if width < height:
        top = round(diff/2)
        bottom = height - round(diff/2)
        crop_rectangle = (0, top, width, bottom) # left, top, right, bottom
        cropped_im = image.crop(crop_rectangle)
        cropped_im.save(path)
    else:
        left = round(diff/2)
        right = width - round(diff/2)
        crop_rectangle = (left, 0, right, height) # left, top, right, bottom
        cropped_im = im.crop(crop_rectangle)
        cropped_im.save(path)

def getRelativeImagePathFromAbsolute(path):
    components = path.split("/")
    return components[8] + "/" + components[9]

def getImageTypeAndCheckForErrors(imagePath, df, index):
    imgtype = imghdr.what(imagePath)
    if imgtype is None:
        print("imgtype is NONE, trying .png extension for path: " + imagePath)
        imgtype = ".png"
        df.at[index, 'Issue Detected'] = "true"
    return imgtype

# /////////////////////////
# MAIN ////////////////////
# /////////////////////////

print("*******************************************************************************************")
print("running microprojectgallery.py with CWD: " + os.getcwd())

if downloadCSV:
    
    # grab CSV from gdrive
    # --------------------

    # authenticate
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    drive = GoogleDrive(gauth)

    # Create GoogleDriveFile instance with file id of file1.
    sheet = drive.CreateFile({'id': spreadsheetID})
    print('title: %s, exportLink: %s' % (sheet['title'], sheet['exportLinks']['text/csv']))
    # print(sheet.GetContentString())

    downloadCSVURL = sheet['exportLinks']['text/csv']
    r = requests.get(downloadCSVURL, allow_redirects=True)
    open(savedSheetName, 'wb').write(r.content)

    imageTest = drive.CreateFile({'id': "1hAcgM_VgLbkZgloqu0iC5V2-nVTyWe2J"})

# load dataframe
df = pd.read_csv(savedSheetName)

# add new columns to dataframe with placeholder values
df['Image Path Absolute'] = "Image Path Absolute TBD"
df['Image Path Relative'] = "Image Path Relative TBD"
df['Sketch ID'] = "Sketch ID TBD"
df['p5 Username'] = "P5 Username TBD"
df['Issue Detected'] = "false"

# sort dataframe
print("sorting df by first and last name")
df.sort_values(by=["First Name", "Last Name"], inplace=True)

# declare array to save our image paths
imagePaths = []

# if images are already downloaded, we'll need this index var
imagePathIndex = 0

# if images are downloaded, create sortedImagePaths list
if not downloadImages:
    for f in os.listdir(os.getcwd() + '/MicroProjectGallery/posterImages'):
        if f != ".DS_Store":
            imagePaths.append(os.getcwd() + '/MicroProjectGallery/posterImages/' + f)
    sortedImagePaths = sorted(imagePaths)

for row in df.itertuples():
    
    if verbose:
        print('iterating over row with index ' + str(row.Index) + ' firstName: ' + row[3] + ' lastName: ' + row[4])

    # extract Sketch ID
    sketchID = row[6].split("/")[-1]

    # add sketch ID to spreadsheet
    df.at[row.Index, 'Sketch ID'] = sketchID

    # extract p5 username
    username = row[6].split("/")[-3]

    # add sketch ID to spreadsheet
    df.at[row.Index, 'p5 Username'] = username

    if downloadImages:

        # extract imageID
        imageID = row[7].split("=")[1] 

        # create path
        imagePath = os.getcwd() + "/MicroProjectGallery/posterImages/" + row[3] + "_" + row[4]
        
        # save image using imageID and path
        print("Saving image to path: %s | with imageID: %s" % (imagePath, imageID))
        download_file_from_google_drive(imageID, imagePath)    

        # detect image type and rename with extension 
        imgtype = getImageTypeAndCheckForErrors(imagePath, df, row.Index)
        # if imgtype is None:
        #     print("imgtype is NONE, trying .png extension for path: " + imagePath)
        #     imgtype = ".png"
        #     df.at[row.Index, 'Issue Detected'] = "true"
        newImagePath = imagePath + "." + imgtype
        print("updating image path to: " + newImagePath)
        os.rename(imagePath, newImagePath)
        
        # add new image path to spreadsheet
        df.at[row.Index, 'Image Path Absolute'] = newImagePath 
        
        # add relative image path to spreadsheet 
        relImagePath = getRelativeImagePathFromAbsolute(newImagePath)
        df.at[row.Index, 'Image Path Relative'] = relImagePath 

    else:
        # Images are already downloaded but we still need to  
        # save absolute and relative image paths to the dataframe  
        
        newImagePath = sortedImagePaths[imagePathIndex]
        if verbose:
            print("row " + str(row.Index) + " | adding new image path: " + newImagePath)
        
        # this will log image issues in our dataframe
        getImageTypeAndCheckForErrors(newImagePath, df, row.Index) 

        # save absolute image path
        df.at[row.Index, 'Image Path Absolute'] = newImagePath 

        # add relative image path to spreadsheet 
        relImagePath = getRelativeImagePathFromAbsolute(newImagePath)
        df.at[row.Index, 'Image Path Relative'] = relImagePath 

        imagePathIndex += 1

# Iterate over image paths and crop to square if needed
for path in imagePaths:
    im = Image.open(path)
    width, height = im.size
    if height < width - 1 or height > width + 1: # accounts for rounding 
        cropImage(im, path)

# Save our updated CSV
print("saving data frame to unit1MicroProjects_updated.csv")
df.to_csv('MicroProjectGallery/unit1MicroProjects_updated.csv', index = False)   