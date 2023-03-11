# Import necessary modules
import os
import cv2
import numpy as np
import mysql.connector
import webbrowser

# Get the absolute path of the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Set variables for database connection, temp is for the youtube link selected from database
temp = 1
db_host = "localhost"
db_user = "root"
db_password = "Sanky@Sanjay3"
db_name = "homeworksix"

# Connect to the database
db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

# Create a cursor object for executing SQL commands
cursor = db.cursor()

#plays the best song in existence
def get_rick_rolled():
    # Call a stored procedure in the database to add a row to the PythonTriggers table, which in turn actives the trigger, running another stored procedure that adds a link to the PythonOutput Table
    cursor.callproc('PythonCheck')
    db.commit()
    #We select that link added previously here
    cursor.execute("SELECT * FROM pythonoutput")
    #Assign that output to myresult
    myresult = cursor.fetchall()
    # Get the YouTube link from the output and open it in a web browser
    youtube_link = myresult[0][0]
    webbrowser.open(youtube_link)
    # Delete the output and trigger data from the database
    cursor.execute("DELETE FROM pythonoutput")
    cursor.execute("DELETE FROM pythontriggers")


# Define a function to draw a circle around a detected object
def draw_circle():
    global temp
    global circles
    # Convert the circle center coordinates and radius to integers
    circles = np.round(circles[0, :]).astype("int")
    # Draw a green circle around the detected object
    for (x, y, r) in circles:
        cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        # Draw a blue rectangle around the circle's center
        cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        # Execute the stored procedure to play a random YouTube video
    # Play Never Gonna Give you up if the circle has been drawn twice
    temp = temp + 1
    if temp < 3:
        get_rick_rolled()

# Define a function to detect circles in an image frame
def find_circle():
    global output, gray, circles
    # Make a copy of the original image
    output = frame.copy()
    # Convert the image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Apply a Gaussian blur to the grayscale image
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # Apply a median blur to the grayscale image
    gray = cv2.medianBlur(gray, 5)
    # Apply an adaptive threshold to the grayscale image
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                 cv2.THRESH_BINARY, 11, 3.5)
    kernel = np.ones((3, 3), np.uint8)
    # Apply erosion and dilation operations to the thresholded image
    gray = cv2.erode(gray, kernel, iterations=1)
    gray = cv2.dilate(gray, kernel, iterations=1)
    # Detect circles in the thresholded image using the Hough circle transform
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 200, param1=30, param2=45, minRadius=145, maxRadius=290)


# Define the path to the video file
image_file_name = "videos/IMG_7834.MOV"
full_image_path = os.path.join(basedir, image_file_name)
# Check if the video file exists
if not os.path.exists(full_image_path):
    print("cannot find image")
    exit(-1)

# Open the video file
cap = cv2.VideoCapture(full_image_path)

# Process the video frames until the user quits
while True:
    ret, frame = cap.read()
    if not ret:
        exit(-1)
    # Find the circle in the frame
    find_circle()

    if circles is not None:
        # If a circle is found, draw circles around
        draw_circle()

        cv2.imshow('gray', gray)
    cv2.imshow('frame', output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#Exit once video ends
cap.release()
db.close()
cv2.destroyAllWindows()
