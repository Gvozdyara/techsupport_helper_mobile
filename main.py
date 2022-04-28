from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
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
        self.yes_btn.bind(on_release=self.yes)
        self.no_btn = Button(text="No")
        self.no_btn.bind(on_release=self.no)

        app.main_layout.add_widget(self)
        self.add_widget(self.label)
        self.add_widget(self.btn_layout)
        self.btn_layout.add_widget(self.yes_btn)
        self.btn_layout.add_widget(self.no_btn)

    def yes(self, event):
        app.main_layout.remove_widget(self)
        print("restored")
        return True


    def no(self, event):
        self.remove_widget(self)
        return False

class SynchSelector(CheckBox):
    global app, Data_base_file, Data_base
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


class NewSectionEntry(TextInput):
    def __init__(self, current_table):
        super().__init__(multiline=False,
                       readonly=False,
                       halign="left",
                       font_size=50,
                       size_hint=(.7, 1))
        self.add_notebook_btn = Button(text="Add notebook",
                                    size_hint=(.3, 1),
                                    pos_hint={'center_x': .8, 'center_y': .5})
        self.add_notebook_btn.bind(on_release=self.add_section)

        self.current_table = current_table

    def set_current_table(self, new_current_table):
        self.current_table = new_current_table

    def add_section(self):
        global Data_base_file
        section_title = self.text
        print(section_title, "section_title")
        if app.synch_mode_var:
            if yadsk.is_cloud_more_fresh(app.synch_mode_var):
                yadsk.download()
                with open(Data_base_file, "rb") as f:
                    Data_base = pickle.load(f)
        else:
            pass
        if section_title != "":
            self.text = ""
            # if not section_title in existing_sections:
        try:
            Data_base[section_title]
            print(f"{section_title} already exists")
        except KeyError:
            self.add_table_to_tbls_list()
            # new_section_btn = Button(section_frame, section_title, open_section, current_table)
            # else:
            #     messagebox.showinfo("Ошибка", "Такая запись уже существует")
        else:
            pass

    def add_table_to_tbls_list(self):
        Data_base[self.section_title] = ["Empty", self.current_table, datetime.now(), datetime.now()]
        with open(Data_base_file, "wb") as f:
            pickle.dump(Data_base, f)
        if self.synch_mode_var.get():
            yadsk.upload()


class SectionBtn(Button):
    def __init__(self, section, current_table):
        super().__init__(text=section, size_hint=(1,1))
        self.current_table = current_table
        self.section = section
        self.bind(on_release=self.click_command)
        self.bind(on_press=self.show_inner_lvl)

    def click_command(self, *args):
        app.open_section(self.current_table, self.section)

    def show_inner_lvl(self, *args):

        self.description = Data_base[self.section][0]
        self.to_layout_sections = list()
        for i in Data_base:
            if Data_base[i][1] == self.section:
                self.to_layout_sections.append(i)

        self.created_edited_time = Data_base[self.section][2:]
        app.inner_lvl_label

        SectionInnerLvlLabel(section_inner_lvl_frame, to_layout_sections,
                             description, created_edited_time)

        return

class MainApp(App):

    def __init__(self):
        super().__init__()
        self.synch_mode_var = False
        inner_lvl_text = StringProperty()

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
        self.add_notebook_textinput = NewSectionEntry("main")

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

        self.inner_lvl_label = Label(text=self.inner_lvl_text)
        # for i in range(20):
        #     self.i = Button(text=f'Button {i}',
        #                               size_hint=(1,1),
        #                               )
        #     self.notebooks_list_layout.add_widget(self.i)
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
        self.add_notebook_layout.add_widget(self.add_notebook_textinput.add_notebook_btn)
        self.main_layout.add_widget(self.notebooks_layout)
        self.notebooks_layout.add_widget(self.notebooks_header_layout)
        self.notebooks_header_layout.add_widget(self.back_btn)
        self.notebooks_header_layout.add_widget(self.edit_btn)
        self.notebooks_header_layout.add_widget(self.directory_label)

        self.notebooks_layout.add_widget(self.noteboooks_and_inner_lvl_layout)
        self.noteboooks_and_inner_lvl_layout.add_widget(self.root)
        self.root.add_widget(self.notebooks_list_layout)
        self.noteboooks_and_inner_lvl_layout.add_widget(self.inner_lvl_label)

        self.open_section("TSH", "main")

        return self.main_layout

    def change_inner_lvl_text(self, to_layout, description, date):
        to_layout.insert(0, "Содержание")
        if len(to_layout) < 2:
            to_layout.insert(1, "Здесь пока пусто")
        tbl_of_cntns = "\n".join(to_layout)
        self.inner_lvl_text = f"{date[0]}\t{date[1]}\n{str(description[:500])}...\n\n{tbl_of_cntns}"


    def change_sync_mode(self, checkbox, value):
        self.synch_mode_var = value
        print("synch_mode_var", self.synch_mode_var)

    def layout_section_btns(self, current_table):
        to_layout_list = list()

        for i in Data_base:
            if Data_base[i][1] == current_table:
                to_layout_list.append(i)

        for item in reversed(to_layout_list):
            section_btn = SectionBtn(item,  # section_name
                       current_table)
            self.notebooks_list_layout.add_widget(section_btn)

    def open_section(self, current_table, inner_table):
        for button in self.notebooks_list_layout.children:
            self.notebooks_list_layout.remove_widget(button)

        self.add_notebook_textinput.set_current_table(inner_table)

        self.layout_section_btns(inner_table)















if __name__ == '__main__':
    Data_base_file = "techsupport_base"
    app = MainApp()
    app.run()