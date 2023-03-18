import cv2
import mediapipe as mp
import numpy as np
import math

'''เรียกใช้ model ของ mediapipe pose'''
mp_pose = mp.solutions.pose

'''Constant value'''
INCORRECT = (255, 0, 0)
CORRECT = (0, 255, 0)

ORGAN_FOR_CAL = [
    # (18, 16, 14),#right_wrist
    (16, 14, 12),#right_elbow
    (14, 12, 24),#right_shoulder

    # (13, 15, 17),#left_wrist
    (11, 13, 15),#left_elbow
    (13, 11, 23),#left_shoulder

    (12, 24, 26),#right_hip
    (28, 26, 24),#right_knee

    (11, 23, 25),#left_hip
    (23, 25, 27)#left_knee
    ]

ERROR = 10 #ค่า error ที่ยังพอรับค่าได้

def makeCircle(image, pos, color):

    window_height = image.shape[0]
    window_width = image.shape[1]

    image = cv2.circle(image, tuple(np.multiply(
        pos, [window_width, window_height]).astype(int)), 20, color, 2)

'''Calculate angle from coordinate value using trigeometry'''
def calculate_angle(a, b, c):

    # ! array index[0] is x, array index[1] is y

    '''old => stable'''
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1] - b[1], a[0]-b[0])
    
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

'''use with reference image not have landmarks'''
def scanAngle(image):

    '''กระบวนการหา landmarks ของ reference image'''
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Initialize Mediapipe Pose model
    pose = mp_pose.Pose(static_image_mode=True)

    # Detect pose landmarks in the image
    results = pose.process(image)

    '''ถ้ารูปๆ นั้นไม่สามารถหา landmarks ได้ก็แปลว่าหา angles ไม่ได้'''
    if not results.pose_landmarks:
        return []
    
    landmarks = results.pose_landmarks.landmark

    angles = initialAngle(landmarks)
    
    return angles

'''use with image from web cam (have landmarks)'''
def initialAngle(landmarks):

    '''สร้าง array เก็บค่าตำแหน่ง x y ของอวัยวะแต่ละอัน'''
    organ_posi = np.array([[landmarks[l].x, landmarks[l].y] for l in mp_pose.PoseLandmark])

    '''เอาเฉพาะมุมที่สนใจ ORGAN_FOR_CAL'''
    angles = [calculate_angle(organ_posi[i], organ_posi[j], organ_posi[k]) for i, j, k in ORGAN_FOR_CAL]

    return angles

'''เอาไว้หาความแตกต่างกันของ angle_ref กับ angle_user'''
def compareAngle(ref, user):
    error = []
    for aR, aU in zip(ref, user):
        error.append(aR - aU)
    error = np.absolute(error)
    
    return error

def draw_circle(landmarks,error_list, image):
    organ_posi = np.array([[landmarks[l].x, landmarks[l].y] for l in mp_pose.PoseLandmark])

    for error, organ in zip(error_list, ORGAN_FOR_CAL):
        if error < ERROR:
            makeCircle(image=image, pos=organ_posi[organ[1]], color=CORRECT)
        else:
            makeCircle(image=image, pos=organ_posi[organ[1]], color=INCORRECT)

'''เอาไว้เช็คว่าพร้อมรึยัง'''
def check_verify(error_list):
    for error in error_list:
        if error > ERROR:
            return False
    return True