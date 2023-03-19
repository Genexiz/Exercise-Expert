from kivymd.app import MDApp
import re
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from kivy.core.window import Window
# Add these imports
from kivymd.uix.list import ILeftBodyTouch, ThreeLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.filemanager import MDFileManager

#! IT so ugly T-T
image = ''
list_pose = []
id = 0
# create the following two classes


class ListItemWithCheckbox(ThreeLineAvatarIconListItem):
    '''Custom list item'''

    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk
        self.ids.preview_image.source = str(image)
        time = str(self.tertiary_text)
        time = time.split(' ')
        time = time[1]
        time = time.split(':')
        time = int(time[0])*60 + int(time[1])

        global list_pose
        name = str(self.text)
        match = re.search(r'\[b\](.*?)\[/b\]', name)

        self.No = len(list_pose)

        if match:
            bold_text = match.group(1)
        list_pose.append({
            "name":str(bold_text),
            "image":str(self.secondary_text),
            "time":time
        })

    def delete_item(self, the_list_item):
        '''Delete the task'''
        list_pose.pop(self.No)
        self.parent.remove_widget(the_list_item)


class DialogContent(MDBoxLayout):
    """OPENS A DIALOG BOX THAT GETS THE TASK FROM THE USER"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.pose_text.text = ''

    def show_img_directory(self):
        self.file_manager_obj = MDFileManager(
            select_path=self.select_path,
            exit_manager=self.exit_manager,
            preview=True)
        self.open_file_manager()

    def select_path(self, path):
        self.on_save(value=path)
        self.exit_manager()

    def open_file_manager(self):
        self.file_manager_obj.show(path='/')

    def exit_manager(self):
        self.file_manager_obj.close()

    def on_save(self, value, **kwargs):

        #!change
        self.ids.pose_text.text = str(value)
        global image
        image = str(value)


class MainApp(MDApp):
    task_list_dialog = None  # Here

    def build(self):
        # Setting theme to my favorite theme
        self.theme_cls.primary_palette = "BlueGray"
        Window.size = (600, 600)
        self.title = "ExerciseExpert"
        self.icon = '1.png'
        return
    # Add the below functions
    def show_task_dialog(self):
        if not self.task_list_dialog:
            self.task_list_dialog = MDDialog(
                title="Create Pose",
                type="custom",
                content_cls=DialogContent(),
            )

        self.task_list_dialog.open()

    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()

    def add_task(self, task, task_date, time_text):
        '''Add task to the list of tasks'''

        # print(task.text, task_date)
        if task_date != '':

            self.root.ids['container'].add_widget(ListItemWithCheckbox(
                text='[b]'+task.text+'[/b]', secondary_text=task_date, tertiary_text='time: ' + time_text))
            # set the dialog entry to an empty string(clear the text entry)
            task.text = ''



app = MainApp()
app.run()
print(list_pose)