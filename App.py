import os
import string
import cv2
import mediapipe as mp
import numpy as np
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from jj import SplashScreen

import scanAngle as scan

'''
Constant value
'''
INCORRECT = (0, 0, 255)
CORRECT = (0, 255, 0)

VERIFY_TIME = 5  # * เมื่อไหร่ที่ user ทำครบเวลานี้จะทำการเริ่มจับเวลา


'''
find file
'''


def find_file(file_name, search_path):
    for root, dir_names, file_names in os.walk(search_path):
        if file_name in file_names:
            return os.path.join(root, file_name)
    return None

time_exercise = None

'''
use kivy structure
'''
parentFolder = os.path.abspath('')
kv_structure = find_file('App.kv', parentFolder)
Builder.load_file(kv_structure)


'''find image'''
img_dir = find_file("JesusPose_1.png", parentFolder)
img = cv2.imread(img_dir)
angle_ref = None


List_Of_Pose = None
indexCurrent = 0

class ScreenApp(Screen):
    def __init__(self, **kwargs):
        super(ScreenApp, self).__init__(**kwargs)

        self.add_widget(yApp())


class ScreenManager(ScreenManager):
    pass


class yApp(Widget):
    def __init__(self, **kwargs):
        super(yApp, self).__init__(**kwargs)

        self.pop_up = None
        # Setup the mediapipe pose detection
        self.pose = mp.solutions.pose.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # define web_cam
        self.cap = cv2.VideoCapture(0)

        # * ตัวจับเวลาออกกำลังกาย
        self.countdown_event = None

        # * ตัวจับเวลาการเตรียมท่า
        self.verify = VERIFY_TIME
        self.verify_event = None

        # * ดูว่าท่านี้ทำเสร็จไปแล้วหรือยัง
        self.is_finished = False

        self.ids.countdown_verify.text = str(VERIFY_TIME)

        # self.ids.img_ref.text = "+\nAdd your image here"
        self.ids.img_ref.source = List_Of_Pose[indexCurrent]['image']
        global angle_ref
        angle_ref = scan.scanAngle(cv2.imread(self.ids.img_ref.source))
        
        global time_exercise
        time_exercise = List_Of_Pose[indexCurrent]['time']
        self.countdown = int(time_exercise)
        self.ids.countdown_label.text = str("{:02d}:{:02d}".format(
            self.countdown // 60, self.countdown % 60))
        self.ids.name_pos.text = List_Of_Pose[indexCurrent]['name']

        # Schedule the update function to run every frame
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def reset_everything(self):
        self.verify = VERIFY_TIME
        self.ids.countdown_verify.text = str(VERIFY_TIME)
        self.countdown = time_exercise
        self.ids.countdown_label.text = str("{:02d}:{:02d}".format(
            self.countdown // 60, self.countdown % 60))
        if self.verify_event != None:
            self.verify_event.cancel()
        self.verify_event = None
        if self.countdown_event != None:
            self.countdown_event.cancel()
        self.countdown_event = None
        self.is_finished = False

    def reset_verify(self):
        self.verify = VERIFY_TIME
        self.ids.countdown_verify.text = str(VERIFY_TIME)
        self.verify_event.cancel()
        self.verify_event = None
        self.countdown_event = None

    def start_verify(self):
        if self.verify_event == None:
            self.verify = VERIFY_TIME
            self.verify_event = Clock.schedule_interval(
                self.update_verify, 1)

    def update_verify(self, dt):
        self.verify -= 1
        self.ids.countdown_verify.text = str(self.verify)
        if self.verify == 0:
            self.stop_verify()

    def stop_verify(self):
        if self.verify_event:
            self.verify_event.cancel()
            self.start_countdown()
        self.verify_event = None

    '''เมื่อทำตามจนครบเวลา VERIFY_TIME เรียกใช้'''

    def start_countdown(self):
        if self.countdown_event == None:
            # self.countdown = self.ids.countdown_label.text.split(":")
            # self.countdown = int(
            #     self.countdown[0]) * 60 + int(self.countdown[1])
            global time_exercise
            self.countdown = time_exercise
            self.countdown_event = Clock.schedule_interval(
                self.update_countdown, 1)

    def update_countdown(self, dt):
        self.countdown -= 1
        self.ids.countdown_label.text = "{:02d}:{:02d}".format(
            self.countdown // 60, self.countdown % 60)
        if self.countdown == 0:
            self.stop_countdown()

    def stop_countdown(self):
        if self.countdown_event:
            self.countdown_event.cancel()
            self.is_finished = True
        self.countdown_event = None
        global indexCurrent
        if indexCurrent < len(List_Of_Pose) - 1:
            self.next_btn()
        else:
            print("success")

    def update(self, dt):
        # Read frame from video stream
        ret, frame = self.cap.read()

        '''กระบวนการแสกนแต่ละส่วนของร่างกาย'''
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)

        '''--->วาด ข้อต่อ (ไม่ต้องวาดก็ได้)'''
        image.flags.writeable = True
        mp.solutions.drawing_utils.draw_landmarks(
            image, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

        '''กระบวนการหามุมตามอวัยวะต่าง ๆ'''
        try:
            # เอาค่า x y visibility ของแต่ละอวัยวะ
            landmarks = results.pose_landmarks.landmark
            angle_user = scan.initialAngle(landmarks=landmarks)

            error_list = scan.compareAngle(ref=angle_ref, user=angle_user)
            scan.draw_circle(landmarks=landmarks,
                             error_list=error_list, image=image)

            if scan.check_verify(error_list):
                self.ids.is_ok.text = "Your Pose Is OK"
                self.ids.is_ok.background_color = 173/255, 255/255, 159/255, 1
            else:
                self.ids.is_ok.text = "Your Pose Is Not OK"
                self.ids.is_ok.background_color = 246/255, 113/255, 113/255, 1

            if self.is_finished == False:
                if scan.check_verify(error_list):
                    if self.verify_event is None and self.countdown_event is None:
                        self.start_verify()
                else:
                    if self.countdown_event == None:
                        self.reset_verify()

        except:
            pass

        '''กระบวนการเอารูปี่ได้จากกล้องไปแสดงผล'''
        # Flip ให้เข้าที่เข้าทาง
        image = cv2.flip(image, 0)
        # Convert the image to a texture and display it on the image widget
        buf = image.tostring()
        texture = Texture.create(
            size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        texture.blit_buffer(image.tobytes(order=None),
                            colorfmt='rgb', bufferfmt='ubyte')
        self.ids.web_cam.texture = texture

    def previous_btn(self):
        global indexCurrent
        if indexCurrent > 0:
            self.reset_everything()
            indexCurrent -= 1
            self.ids.name_pos.text = List_Of_Pose[indexCurrent]['name']
            self.ids.img_ref.source = List_Of_Pose[indexCurrent]['image']
            global angle_ref
            check = scan.scanAngle(cv2.imread(self.ids.img_ref.source))
            angle_ref = check
            global time_exercise
            time_exercise = List_Of_Pose[indexCurrent]['time']
            self.countdown = time_exercise
            self.ids.countdown_label.text = str("{:02d}:{:02d}".format(
            self.countdown // 60, self.countdown % 60))
            
    def next_btn(self):
        global indexCurrent
        if indexCurrent < len(List_Of_Pose) - 1:
            self.reset_everything()
            indexCurrent+=1
            self.ids.name_pos.text = List_Of_Pose[indexCurrent]['name']
            self.ids.img_ref.source = List_Of_Pose[indexCurrent]['image']
            global angle_ref
            check = scan.scanAngle(cv2.imread(self.ids.img_ref.source))
            angle_ref = check
            global time_exercise
            time_exercise = List_Of_Pose[indexCurrent]['time']
            self.countdown = time_exercise
            self.ids.countdown_label.text = str("{:02d}:{:02d}".format(
            self.countdown // 60, self.countdown % 60))



class CoolApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (Window.width, Window.height)
        self.icon = '1.png'
        Window.maximize()
        return ScreenManager()

    def on_start(self):
        self.title = 'ExerciseExpert'

from main import list_pose
List_Of_Pose = list_pose
if __name__=="__main__":
    if len(List_Of_Pose) != 0:
        SplashScreen().run()
        CoolApp().run()
