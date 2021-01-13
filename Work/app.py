import cv2
import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

cap = cv2.VideoCapture(0)
ret, frame = cap.read()

def takePicture():
    (grabbed, frame) = cap.read()
    showimg = frame

    image = 'capture.png'
    cv2.imwrite(image, frame)
    cap.release()

    #This is the connection string to azure
    connect_str = ''
  
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    
    container_name = "powerplant"
    
    # Create the container
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=image)

    print("\nUploading to Azure Storage as blob:\n\t" + image)

    # Upload the created file
    with open(image, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    return image

print(takePicture())









