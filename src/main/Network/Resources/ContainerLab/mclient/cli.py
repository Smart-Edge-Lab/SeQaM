import sys
import requests
import time

def upload_image(url, image_path):
    try:
        files = {'image': open(image_path, 'rb')}
        start_time=time.time()
        response = requests.post(url, files=files)

        if response.status_code == 200:

            print("Image uploaded successfully")
            end_time=time.time()
            delay=(end_time-start_time)
            #send_message(delay) #used to send data to the collector machine
            print ("delay  ",delay )
            file1 = open('myfile.txt', 'a')
            #fdata=start_time,end_time, "\n" 
            file1.write(str(delay)+ '\n')
        else:
            print("Failed to upload image:", response.status_code)
    except Exception as e:
        print("Error:", e)

def send_message(message):
    msg2=str(message)
    url = 'http://172.22.174.198:8080'
    data = {'message': message}
    response = requests.post(url, data=msg2.encode('utf-8'))
    if response.status_code == 200:
        print('Message sent successfully.')
    else:
        print('Failed to send message.')

 
if __name__ == "__main__":
    img = sys.argv[1]
    count1=sys.argv[2]
    count=int(count1)
    timeout = count
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
    #for x in range(count):
    #while True:
        server_url = 'http://192.168.5.2:8080'  # Replace this with your server URL
        #image_path = 'sm.jpg'  # Replace this with the path to your image
        image_path = img
        upload_image(server_url, image_path)
        time.sleep(0.100)
