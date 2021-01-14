# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
import cv2
import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import uuid

#Azure storage connection string
m_str_Connect_str = ''

print ("Open camera")
cap = cv2.VideoCapture(0)
print ("Opened")

print ("Init")
ret, frame = cap.read()
print ("Done init")

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        # define behavior for receiving an input message on input1
        async def input1_listener(module_client):
            while True:
                input_message = await module_client.receive_message_on_input("input1")  # blocking call
                print("the data in the message received on input1 was ")
                print(input_message.data)
                print("custom properties are")
                print(input_message.custom_properties)
                print("forwarding mesage to output1")
                await module_client.send_message_to_output(input_message, "output1")

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    print("TakePicture")
                    (grabbed, frame) = cap.read()
                    print("Took")

                    strFilename = str(uuid.uuid4()) + ".png";
                    print("write: " + strFilename)
                    cv2.imwrite(strFilename, frame)
                    print("wrote")

                    #print("Release")
                    #cap.release()
                    #print("Released")

                    print("Upload: " + strFilename)                    
                    blob_service_client = BlobServiceClient.from_connection_string(m_str_Connect_str)
                    container_name = "powerplant"
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=strFilename)
    
                    with open(strFilename, "rb") as data:
                        blob_client.upload_blob(data, overwrite=True)

                    print("Uploaded")
                    
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except Exception as ex:
                    print('Exception:')
                    print(ex)
                    time.sleep(10)

        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client))

        print ( "The sample is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()
                
        def TakePicture():
            print ( "TakePicture")
            (grabbed, frame) = cap.read()
            showimg = frame
            image = 'capture.png'

            print ( "write")

            cv2.imwrite(image, frame)
            cap.release()

            #This is the connection string to azure
            connect_str = 'DefaultEndpointsProtocol=https;AccountName=bikeshop;AccountKey=VO0d/Iwxm86o7WOhfAOTWdp8U46b7eNrYMkpZtgy081AKVIZJ9YbGpxDQc7MyImm8WsVXpSeKCSZwxkjN7mguw==;EndpointSuffix=core.windows.net'
        
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            
            container_name = "powerplant"
            
            # Create the container
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=image)

            print("\nUploading to Azure Storage as blob:\n\t" + image)

            # Upload the created file
            with open(image, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            return image
        
    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())