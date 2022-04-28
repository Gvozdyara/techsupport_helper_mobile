from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import time
from datetime import datetime
import pickle
import yadsk


class AskYesNo(BoxLayout):
    def __init__(self, text):
        super(AskYesNo, self).__init__(orientation="vertical")
        self.text = text
        self.label = Label(text=self.text)
        self.btn_layout = BoxLayout(orientation="horizontal")
        self.yes_btn = Button(text="Yes")
        self.yes_btn.bind(on_press=self.yes)
        self.no_btn = Button(text="No")
        self.no_btn.bind(on_press=self.no)

        # app.main_layout.add_widget(self)
        self.add_widget(self.label)
        self.add_widget(self.btn_layout)
        self.btn_layout.add_widget(self.yes_btn)
        self.btn_layout.add_widget(self.no_btn)

    def yes(self, event):
        self.remove_widget(self)
        return True


    def no(self, event):
        self.remove_widget(self)
        return False

class SynchSelector(CheckBox):
    global app, Data_base_file
    def __init__(self):
        super().__init__(active=False)
        self.bind(active=app.change_sync_mode)
        self.bind(on_press=self.synchronize)

    def synchronize(self, *args):
        global Data_base_file
        # check synch status
        if app.synch_mode_var:
            #   check if the disk is more fresh
            #  the same if no file on the disk to compare
            if yadsk.is_cloud_more_fresh(app.synch_mode_var):
                #  select the option
                if AskYesNo(
"The base from the cloud is more fresh. Update from the cloud (Yes) or update the cloud (No)?"):
                    #  try to download from the cloud
                    if yadsk.download():
                        #  after download successfull open the file
                        with open(Data_base_file, "rb") as f:
                            Data_base = pickle.load(f)
                    #  if couldn't download the file show error
                    else:
                        AskYesNo("Couldn't download from the cloud")
                         # open section offline
                #  if update the cloud from the disk selected
                else:
                    try:
                        #  try upload the file to the cloud
                        yadsk.upload()
                        with open(Data_base_file, "rb") as f:
                            Data_base = pickle.load(f)
                    #  if file not found on the disk create a new empty one
                    except FileNotFoundError:
                        Data_base = dict()
                        Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                        Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                        with open(Data_base_file, "wb") as f:
                            pickle.dump(Data_base, f)
            #  if disk is more fresh or no file in the cloud
            else:
                try:
                     #  try upload to the cloud
                     yadsk.upload()
                     with open(Data_base_file, "rb") as f:
                         Data_base = pickle.load(f)
                #  if no file on the disk create the new one
                except FileNotFoundError:
                    print("filenotfound")
                    Data_base = dict()
                    Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                    Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                    with open(Data_base_file, "wb") as f:
                        pickle.dump(Data_base, f)
                except:
                    print("connection error probably")
                    AskYesNo("Connection error porobably")
                    try:
                        with open(Data_base_file, "rb") as f:
                            Data_base = pickle.load(f)
                    except EOFError:
                        print("EOFError")
                        Data_base = dict()
                        Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                        Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                        with open(Data_base_file, "wb") as f:
                            pickle.dump(Data_base, f)
                    except FileNotFoundError:
                        print("FileNotFoundError")
                        Data_base = dict()
                        Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                        Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                        with open(Data_base_file, "wb") as f:
                            pickle.dump(Data_base, f)



class MainApp(App):

    def __init__(self):
        super().__init__()
        self.synch_mode_var = False

    def build(self):
        global Data_base_file
        self.main_layout = BoxLayout(orientation="vertical")

        self.top_menu_layout = BoxLayout(orientation="horizontal",
                                         size_hint=(1, 0.05))

        self.top_dot_menu_btn = Button(text="...",
                                       size_hint=(.1, 1))

        self.synch_layout = BoxLayout(orientation="horizontal",
                                      size_hint=(0.9, 1))
        self.synch_mode_var = True
        self.synch_btn = SynchSelector()
        self.synch_btn.synchronize()

        # self.synch_btn = CheckBox(size_hint=(0.5, 1),
        #                                pos_hint={'center_x': .1, 'center_y': .5})
        self.synch_label = Label(text="Synchronization",
                                 size_hint=(0.5, 1))

        self.search_layout = BoxLayout(orientation="horizontal",
                                       size_hint=(1, 0.1),
                                       padding=(2, 10))
        self.search_textinput = TextInput(multiline=False,
                                               readonly=False,
                                               halign="left",
                                               font_size=50,
                                               size_hint=(.7, 1)
                                          )

        self.search_name_btn = Button(text="Find\nname",
                                      size_hint=(0.15, 1))
        self.search_note_btn = Button(text="Find\nnote",
                                      size_hint=(0.15, 1))

        self.add_notebook_layout = BoxLayout(orientation="horizontal",
                                             size_hint=(1, 0.1),
                                             padding=(2, 0, 2, 10))
        self.add_notebook_textinput = TextInput(multiline=False,
                                               readonly=False,
                                               halign="left",
                                               font_size=50,
                                               size_hint=(.7, 1))
        self.add_notebook_btn = Button(text="Add notebook",
                                              size_hint=(.3, 1),
                                              pos_hint={'center_x': .8, 'center_y': .5})

        self.notebooks_layout = BoxLayout(orientation="vertical",
                                          size_hint=(1, 0.8))
        self.notebooks_header_layout = BoxLayout(orientation="horizontal",
                                                 size_hint=(1, 0.05))
        self.back_btn = Button(text="Back",
                               size_hint=(0.25, 1))
        self.directory_label = Label(text="directory/notebook",
                                     size_hint=(0.5, 1))
        self.edit_btn = Button(text="Edit",
                               size_hint=(0.25, 1))
        self.noteboooks_and_inner_lvl_layout = BoxLayout(orientation="horizontal",
                 size_hint=(1, 1),
                 padding=(0,10,0,0))

        self.notebooks_list_layout = GridLayout(size_hint_y=None,
            cols=1,
            row_default_height=150,
            row_force_default=True)
        self.notebooks_list_layout.bind(minimum_height=self.notebooks_list_layout.setter('height'))

        self.inner_lvl_label = Label(text="Some\nmultiline\ntext\n\n\n\n\nof the inner\ncontext")
        for i in range(20):
            self.i = Button(text=f'Button {i}',
                                      size_hint=(1,1),
                                      )
            self.notebooks_list_layout.add_widget(self.i)
        self.notebook_btn = Button(text="Notebook 1",
                                   size=(1, 50),
                                   size_hint=(0.5, None))
        self.root = ScrollView()

        self.main_layout.add_widget(self.top_menu_layout)
        self.top_menu_layout.add_widget(self.top_dot_menu_btn)
        self.top_menu_layout.add_widget(self.synch_layout)
        self.synch_layout.add_widget(self.synch_btn)
        self.synch_layout.add_widget(self.synch_label)
        self.main_layout.add_widget(self.search_layout)
        self.search_layout.add_widget(self.search_textinput)
        self.search_layout.add_widget(self.search_name_btn)
        self.search_layout.add_widget(self.search_note_btn)
        self.main_layout.add_widget(self.add_notebook_layout)

        self.add_notebook_layout.add_widget(self.add_notebook_textinput)
        self.add_notebook_layout.add_widget(self.add_notebook_btn)
        self.main_layout.add_widget(self.notebooks_layout)
        self.notebooks_layout.add_widget(self.notebooks_header_layout)
        self.notebooks_header_layout.add_widget(self.back_btn)
        self.notebooks_header_layout.add_widget(self.edit_btn)
        self.notebooks_header_layout.add_widget(self.directory_label)

        self.notebooks_layout.add_widget(self.noteboooks_and_inner_lvl_layout)
        self.noteboooks_and_inner_lvl_layout.add_widget(self.root)
        self.root.add_widget(self.notebooks_list_layout)
        self.noteboooks_and_inner_lvl_layout.add_widget(self.inner_lvl_label)

        return self.main_layout

    def change_sync_mode(self, checkbox, value):
        self.synch_mode_var = value
        print("synch_mode_var", self.synch_mode_var)
















if __name__ == '__main__':
    Data_base_file = "techsupport_base"
    app = MainApp()
    app.run()