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
    def __init__(self):
        super().__init__(active=None)
        self.bind(active=app.change_sync_mode)
        self.bind(on_press=self.synchronize)

    def synchronize(self, *args):
        # check synch status
        if app.synch_mode_var==True:
            print("if app.synch_mode_var:")
            #   check if the disk is more fresh
            #  the same if no file on the disk to compare
            if yadsk.is_cloud_more_fresh(app.synch_mode_var):
                print("if yadsk.is_cloud_more_fresh(app.synch_mode_var):")
                #  select the option
                if AskYesNo(
"The base from the cloud is more fresh. Update from the cloud (Yes) or update the cloud (No)?"):
                    #  try to download from the cloud
                    if yadsk.download():
                        #  after download successfull open the file
                        with open(app.Data_base_file, "rb") as f:
                            app.Data_base = pickle.load(f)
                    #  if couldn't download the file show error
                    else:
                        AskYesNo("Couldn't download from the cloud")
                         # open section offline
                #  if update the cloud from the disk selected
                else:
                    try:
                        print("first askyesno, else, first try")
                        #  try upload the file to the cloud
                        yadsk.upload()
                        with open(app.Data_base_file, "rb") as f:
                            app.Data_base = pickle.load(f)
                    #  if file not found on the disk create a new empty one
                    except FileNotFoundError:
                        app.Data_base = dict()
                        app.Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                        app.Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                        with open(app.Data_base_file, "wb") as f:
                            pickle.dump(app.Data_base, f)
            #  if disk is more fresh or no file in the cloud
            else:
                print("if yadsk.is_cloud_more_fresh(app.synch_mode_var):else")
                try:
                     print("if yadsk.is_cloud_more_fresh(app.synch_mode_var):try upload")
                     #  try upload to the cloud
                     yadsk.upload()

                     with open(app.Data_base_file, "rb") as f:
                         app.Data_base = pickle.load(f)
                #  if no file on the disk create the new one
                except FileNotFoundError:
                    print("filenotfound")
                    app.Data_base = dict()
                    app.Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                    app.Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                    with open(app.Data_base_file, "wb") as f:
                        pickle.dump(app.Data_base, f)
                except:
                    print("connection error probably")
                    AskYesNo("Connection error porobably")
                    try:
                        with open(app.Data_base_file, "rb") as f:
                            app.Data_base = pickle.load(f)
                    except EOFError:
                        print("EOFError")
                        app.Data_base = dict()
                        app.Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                        app.Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                        with open(app.Data_base_file, "wb") as f:
                            pickle.dump(app.Data_base, f)
                    except FileNotFoundError:
                        print("FileNotFoundError")
                        app.Data_base = dict()
                        app.Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                        app.Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                        with open(app.Data_base_file, "wb") as f:
                            pickle.dump(app.Data_base, f)

        else:
            try:
                print("try open data_base")
                with open(app.Data_base_file, "rb") as f:
                    app.Data_base = pickle.load(f)
            except EOFError:
                print("EOFError")
                app.Data_base = dict()
                app.Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                app.Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                with open(app.Data_base_file, "wb") as f:
                    pickle.dump(app.Data_base, f)
            except FileNotFoundError:
                print("FileNotFoundError")
                app.Data_base = dict()
                app.Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
                app.Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
                with open(app.Data_base_file, "wb") as f:
                    pickle.dump(app.Data_base, f)


class NewSectionEntry(TextInput):
    def __init__(self, current_table):
        super().__init__(multiline=False,
                       readonly=False,
                       halign="left",
                       font_size=50,
                       size_hint=(.7, 1))
        self.add_notebook_btn = Button(text="Add notebook",
                                    size_hint=(.3, 1))
                                    # pos_hint={'center_x': .8, 'center_y': .5})
        self.add_notebook_btn.bind(on_release=self.add_section)

    def add_section(self):
        section_title = self.text
        print(section_title, "section_title")
        if app.synch_mode_var:
            if yadsk.is_cloud_more_fresh(app.synch_mode_var):
                yadsk.download()
                with open(app.Data_base_file, "rb") as f:
                    app.Data_base = pickle.load(f)
        else:
            pass
        if section_title != "":
            self.text = ""
            # if not section_title in existing_sections:
        try:
            app.Data_base[section_title]
            print(f"{section_title} already exists")
        except KeyError:
            self.add_table_to_tbls_list()
            # new_section_btn = Button(section_frame, section_title, open_section, current_table)
            # else:
            #     messagebox.showinfo("Ошибка", "Такая запись уже существует")
        else:
            pass

    def add_table_to_tbls_list(self):
        app.Data_base[self.section_title] = ["Empty", app.current_table, datetime.now(), datetime.now()]
        with open(app.Data_base_file, "wb") as f:
            pickle.dump(app.Data_base, f)
        if self.synch_mode_var.get():
            yadsk.upload()


class BackBtnMain(Button):
    def __init__(self):
        self.is_inactive = False
        super().__init__(text="Back",
                               size_hint=(0.25, 1),
                               disabled=self.is_inactive)



    def command(self, e):
        if app.current_table != "TSH":
            app.open_section(app.Data_base[app.current_table][1], app.current_table)
        else:
            self.set_state()

    def set_state(self):
        if app.current_table != "TSH":
            self.is_inactive = False
        else:
            self.is_inactive = True


class SectionBtn(Button):
    def __init__(self, section, parent_table):
        super().__init__(text=section, size_hint=(1,.5))
        self.parent_table = parent_table
        self.section = section
        self.bind(on_release=self.click_command)
        self.bind(on_press=self.show_inner_lvl)
        self.description = app.Data_base[self.section][0]
        self.to_layout_sections = list()
        self.created_edited_time = app.Data_base[self.section][2:]
        app.notebooks_list_layout.add_widget(self)

    def click_command(self, *args):
        app.open_section(self.parent_table, self.section)
        print(f"open section {self.section} from {self.parent_table}")

    def show_inner_lvl(self, *args):
        for i in app.Data_base:
            if app.Data_base[i][1] == self.section:
                self.to_layout_sections.append(i)


        app.inner_lvl_label.update_text(self.to_layout_sections, self.description[:500], self.created_edited_time)


class InnerLvlLabel(Label):
    def __init__(self):
        self.text = ""
        super().__init__(text=self.text,
                         text_size=(self.width, None),
                         size = self.texture_size,
                         size_hint=(1, None),
                         pos_hint={'center_x': .8, 'bottom_y': 1})

    def update_text(self, to_layout, description, date):
        to_layout.insert(0, "Содержание")
        if len(to_layout) < 2:
            to_layout.insert(1, "Здесь пока пусто")
        tbl_of_cntns = "\n".join(to_layout)
        self.text = f"{date[0]}\t{date[1]}\n{str(description[:500])}...\n\n{tbl_of_cntns}"

class MainApp(App):

    def __init__(self):
        super().__init__()
        self.synch_mode_var = 0
        self.inner_lvl_text = ""
        self.Data_base_file = "techsupport_base"
        self.Data_base = dict()
        self.current_table = "main"

    def build(self):
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
        self.back_btn = BackBtnMain()
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

        self.inner_lvl_label = InnerLvlLabel()
        self.inner_lvl_layout = GridLayout(cols=1, size_hint_y=None, size_hint_x=1,
                                          pos_hint={"left_x":1, "top_y":0})
        self.inner_lvl_layout.bind(minimum_height=self.inner_lvl_layout.setter('height'))

        self.inner_lvl_scroll = ScrollView()

        self.notebooks_list_scroll = ScrollView()



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
        self.noteboooks_and_inner_lvl_layout.add_widget(self.notebooks_list_scroll)
        self.notebooks_list_scroll.add_widget(self.notebooks_list_layout)
        self.noteboooks_and_inner_lvl_layout.add_widget(self.inner_lvl_scroll)
        self.inner_lvl_scroll.add_widget((self.inner_lvl_layout))
        self.inner_lvl_layout.add_widget(self.inner_lvl_label)

        self.open_section("TSH", "main")

        return self.main_layout

    def set_current_table(self, new_current_table):
        self.current_table = new_current_table



    def change_inner_lvl_text(self, to_layout, description, date):
        to_layout.insert(0, "Содержание")
        if len(to_layout) < 2:
            to_layout.insert(1, "Здесь пока пусто")
        tbl_of_cntns = "\n".join(to_layout)
        self.inner_lvl_text = f"{date[0]}\t{date[1]}\n{str(description[:500])}...\n\n{tbl_of_cntns}"
        print(self.inner_lvl_text)


    def change_sync_mode(self, checkbox, value):
        self.synch_mode_var = value
        print("synch_mode_var", self.synch_mode_var)

    def open_section(self, current_table, inner_table):

        self.set_current_table(current_table)
        print(f"{self.current_table} is currently openned")

        self.back_btn.set_state()
        self.back_btn.bind(on_release=self.back_btn.command)
        self.layout_section_btns(inner_table)



    def layout_section_btns(self, inner_table):

        self.notebooks_list_layout.clear_widgets()

        self.to_layout_list = list()

        for i in self.Data_base:
            if self.Data_base[i][1] == inner_table:
                self.to_layout_list.append(i)


        for item in reversed(self.to_layout_list):
            SectionBtn(item, inner_table)


if __name__ == '__main__':
    app = MainApp()
    app.run()