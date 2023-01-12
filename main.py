from flask import Flask, Response, render_template, request, jsonify, session
import requests
import json
import time
import os
import cv2
import mediapipe as mp
from os.path import exists

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
	return "Hi"

def deleteData(video_path, file_path):
	if os.path.exists(video_path):
		os.remove(video_path)
	if os.path.exists(file_path):
		os.remove(file_path)

def getPoseData(video_path, file_path):
	frame = 0
	cap = cv2.VideoCapture(video_path)
	mp_pose = mp.solutions.pose

	text_result = ""

	with mp_pose.Pose(
			min_detection_confidence=0.5,
			min_tracking_confidence=0.5) as pose:

		file1=open(file_path,"a")
		while cap.isOpened():

			success, image = cap.read()
			if not success:

				#print("Ignoring empty camera frame.")
				# If loading a video, use 'break' instead of 'continue'.
				print('Ended on frame', frame)
				break

			# Flip the image horizontally for a later selfie-view display, and convert
			# the BGR image to RGB.
			image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
			# To improve performance, optionally mark the image as not writeable to
			# pass by reference.
			image.flags.writeable = False
			results = pose.process(image)

			if results.pose_landmarks != None:
				for i in range (33):
					x = results.pose_landmarks.landmark[i].x
					y = results.pose_landmarks.landmark[i].y
					z = results.pose_landmarks.landmark[i].z
					line = '%d,%d,%f,%f,%f\n' % (frame,i,x,y,z)
					text_result = text_result + line

					file1.write(line) 

			frame += 1
			if frame % 25 == 0:
				print("frame no.", frame)
		file1.close()
		print('done looping?')
	cap.release()
	print('getPoseData')
	return text_result

@app.route('/process', methods=['POST'])
def process():
	print("process")
	if request.method == 'POST':
		request.get_data()
		data = request.get_data()

		timestamp = int(time.time())

		video_path = str(timestamp) + ".mp4"
		file_path = str(timestamp)+ '.txt'

		with open(video_path, "wb") as file:
			file.write(data)


		result = getPoseData(video_path, file_path)
		deleteData(video_path, file_path)
		return result


	
if __name__ == '__main__':
	app.run('0.0.0.0')
