from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.lang.builder import Builder
from datetime import datetime
import pickle
import yadsk
import tkinter as tk
from tkinter import messagebox



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
        return "Yes"


    def no(self, event):
        app.main_layout.remove_widget(self)
        return "No"


class SynchSelector(CheckBox):
    def __init__(self):
        super().__init__(active=None)
        self.bind(active=app.change_sync_mode)


class AddNotebookBtn(Button):
    def __init__(self):
        super().__init__(text=self.text,
                        size_hint=(.3, 1))
                        # pos_hint={'center_x': .8, 'center_y': .5})
        self.bind(on_release=app.add_notebook_textinput.add_section)
        self.text = "Add notebook"

    def set_text(self, new_text):
        self.text = new_text

    def delete_notebook(self, e):
        print("Start delete")
        if tk.messagebox.askyesno("Attention", f"Delete {app.current_table}?"):
            # app.compare_with_cloud()
            # try:
            del app.Data_base[app.current_table]
            print(f"app.Data_base[{app.current_table}] deleted")
            i = 1
            while i > 0:
                data_base = tuple(app.Data_base)
                print(len(app.Data_base), "during an iteration")
                print(data_base, "\n current data_base tuple", i, "-i")
                for key in data_base:
                    if app.Data_base[key][1] not in app.Data_base.keys() and app.Data_base[key][1] != "TSH":
                        print(f"Deleting {key}")
                        del app.Data_base[key]
                        i += 1
                i -= 1
            with open(app.Data_base_file, "wb") as f:
                pickle.dump(app.Data_base, f)
                if app.synch_mode_var:
                    yadsk.upload(app)
            # except KeyError:
            #     AskYesNo(f"There is no {app.current_table} notebook")
            self.unbind(on_release=self.delete_notebook)
            self.bind(on_release=app.add_notebook_textinput.add_section)
            self.set_text("Add notebook")
            app.noteboooks_and_inner_lvl_layout.clear_widgets()
            app.layout_notebooks_list_inner_level()
            app.back_btn.unbind(on_release=app.back_btn.save_command)
            app.back_btn.bind(on_release=app.back_btn.command)
            print(f"will be openned {app.parent_table}, with its parent {app.Data_base[app.parent_table][1]}")
            app.open_section(app.Data_base[app.parent_table][1], app.parent_table)


class SearchInterface():
    def __init__(self, mode, *args):
        super().__init__()
        app.notebooks_list_layout.clear_widgets()
        self.mode = mode
        self.found_result = list()
        self.found_notes = dict()

        if mode == "name":
            self.search_name()
        else:
            self.search_note()

    def search_note(self):
        for key in app.Data_base.keys():
            if app.search_textinput.text in app.Data_base[key][1]:
                note = app.Data_base[key][0]
                if len(note)>202:
                    start_index = note.find(app.search_textinput.text)
                    if start_index>99:
                        short = note[start_index-100:start_index+100]
                    else:
                        short = note[0:start_index+200]
                else:
                    short = note
                self.found_notes[key] = short

        for key in self.found_notes.keys():
            SectionBtn(key, app.Data_base[key][1], self.found_notes[key])



    def search_name(self):
        for key in app.Data_base.keys():
            if app.search_textinput.text.upper() in str(key):
                self.found_result.append(key)
        for i in self.found_result:
            SectionBtn(i, app.Data_base[i][1])


class FindNoteBtn(Button):
    def __init__(self):
        super().__init__(text="Find\nnote", size_hint=(0.15, 1))
        self.bind(on_release=self.start_search)

    def start_search(self, e):
        print("start search")
        SearchInterface("note")


class FindNameBtn(Button):
    def __init__(self):
        print("Instance of FindNameBtn")
        super().__init__(text="Find\nname", size_hint=(0.15, 1))

        self.bind(on_release=self.start_search)

    def start_search(self, e):
        print("start search")

        SearchInterface("name")

class NewSectionEntry(TextInput):
    def __init__(self):
        super().__init__(multiline=False,
                       readonly=False,
                       halign="left",
                       # font_size=50,
                       size_hint=(.7, 1))


    def add_section(self, e):
        self.section_title = self.text.upper()
        print(self.section_title, "section_title")
        if app.synch_mode_var:
            if yadsk.is_cloud_more_fresh(app):
                yadsk.download()
                with open(app.Data_base_file, "rb") as f:
                    app.Data_base = pickle.load(f)
        else:
            pass
        if self.section_title != "":
            self.text = ""
            # if not section_title in existing_sections:
        try:
            app.Data_base[self.section_title]
            print(f"{self.section_title} already exists")
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
        if app.synch_mode_var:
            yadsk.upload(app)
        btn = SectionBtn(self.section_title, app.current_table)

    def set_initial_text(self, new_text):
        self.text = new_text

class BackBtnMain(Button):
    def __init__(self):
        self.is_inactive = False
        super().__init__(text="Back",
                               size_hint=(0.25, 1),
                               disabled=self.is_inactive)

    def command(self, e):
        print("usuall return")
        if app.parent_table != "TSH":
            app.open_section(app.Data_base[app.parent_table][1], app.parent_table)
            self.set_state()
        else:
            app.open_section("TSH", "main")
            self.set_state()

    def set_state(self):
        if app.current_table != "main":
            self.is_inactive = False
        else:
            self.is_inactive = True

    def save_command(self, *args):
        print("saving")
        new_note =  app.edit_interface.text
        print(app.parent_table)
        if new_note != app.edit_interface.initial_text or app.add_notebook_textinput.text.upper() != app.current_table.upper():
            if app.set_new_note(new_note) == "saved":
                app.noteboooks_and_inner_lvl_layout.clear_widgets()
                app.add_notebook_textinput.set_initial_text("")
                app.layout_notebooks_list_inner_level()
            elif app.set_new_note(new_note) == "key_error":
                parent_table = app.Data_base[app.parent_table][1]
                app.noteboooks_and_inner_lvl_layout.clear_widgets()
                app.add_notebook_textinput.set_initial_text("")
                app.layout_notebooks_list_inner_level()
        else:
            app.noteboooks_and_inner_lvl_layout.clear_widgets()
            app.layout_notebooks_list_inner_level()
            app.add_notebook_textinput.set_initial_text("")

        self.unbind(on_release=self.save_command)
        self.bind(on_release=self.command)
        app.add_notebook_button.set_text("Add notebook")
        app.add_notebook_button.unbind(on_release=app.add_notebook_button.delete_notebook())
        app.add_notebook_button.bind(on_release=app.add_notebook_textinput.add_section)
        print("end of save_command, back button should be configured")


class SectionBtn(Button):
    def __init__(self, section, parent_table, *args):
        super().__init__(text=section,
                         size_hint=(1,None),
                         text_size=(app.noteboooks_and_inner_lvl_layout.width/2, None),
                         halign="center",
                         height=self.texture_size[1] + dp(100))
        try:
            self.text = args[0]
        except IndexError:
            self.text = section
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
                         text_size=(app.main_layout.width*2, None),
                         height = self.texture_size[1],
                         size_hint=(1, None),
                         valign="middle",
                         pos_hint={'center_x': .8, 'bottom_y': 1})

    def update_text(self, to_layout, description, date):
        to_layout.insert(0, "Содержание")
        if len(to_layout) < 2:
            to_layout.insert(1, "Здесь пока пусто")
        tbl_of_cntns = "\n".join(to_layout)
        self.text = f"{date[0]}\t{date[1]}\n{str(description[:500])}...\n\n{tbl_of_cntns}"



class DirectoryLabel(Label):
    def __init__(self):
        super().__init__(text=self.text,size_hint=(0.5, 1))
        self.text = "TSH/main"

    def set_text(self):
        self.text = f"{app.parent_table}/{app.current_table}"


class EditBtn(Button):
    def __init__(self):
        super().__init__(text=self.text,
                         size_hint=(0.25, 1))
        self.bound_notebook = app.current_table
        self.bind(on_release=self.command)
        self.text = "Edit"

    def set_text(self, new_text):
        self.text = new_text

    def set_current(self):
        self.bound_notebook = app.current_table

    def command(self, e):
        self.set_current()
        app.start_edit()

    def move_notebook(self, e):
        app.back_btn.save_command()
        self.set_current()
        current_parent = app.Data_base[self.bound_notebook][1]
        app.open_section(app.Data_base[current_parent][1], self.bound_notebook)
        self.unbind(on_release=self.move_notebook)
        self.bind(on_release=self.set_new_parent_while_move)
        self.set_text("Select")

    def set_new_parent_while_move(self, e):
        value = app.Data_base[self.bound_notebook]
        app.Data_base[self.bound_notebook] = [value[0], app.current_table, value[2], value[3]]
        self.set_text("Edit")
        self.unbind(on_release=self.set_new_parent_while_move)
        self.bind(on_release=self.command)
#         remove all widgets from noteboooks_and_inner_lvl_layout

# create buttons layout to edit text features
# create textinput widget
# make add section button inactive
#  set save command for the back button



class EditText(TextInput):
    def __init__(self):
        self.initial_text = app.Data_base[app.current_table][0]
        self.font_size = int(12)
        self.text_alignce = str("left")
        self.bold = bool(False)
        self.italic = bool(False)
        self.underline = bool(False)
        super().__init__(text=self.initial_text,
                         font_size=self.font_size)
        app.add_notebook_textinput.set_initial_text(app.current_table)
        app.noteboooks_and_inner_lvl_layout.add_widget(self)
        app.back_btn.unbind(on_release=app.back_btn.command)
        app.back_btn.bind(on_release=app.back_btn.save_command)
        app.add_notebook_button.unbind(on_release=app.add_notebook_textinput.add_section)
        app.add_notebook_button.bind(on_release=app.add_notebook_button.delete_notebook)
        app.add_notebook_button.set_text("Delete notebook")

    def set_bold(self, e, value):
        self.bold = value

    def set_italic(self, e, value):
        self.italic = value

    def set_underline(self, e, value):
        self.underline = value


class MainApp(App):

    def __init__(self):
        super().__init__()
        self.synch_mode_var = bool()
        self.inner_lvl_text = ""
        self.Data_base_file = "techsupport_base"
        self.Data_base = dict()
        self.current_table = "main"
        self.parent_table = "TSH"


    def build(self):
        self.main_layout = BoxLayout(orientation="vertical")

        self.top_menu_layout = BoxLayout(orientation="horizontal",
                                         size_hint=(1, 0.05))

        self.top_dot_menu_btn = Button(text="...",
                                       size_hint=(.1, 1))

        self.synch_layout = BoxLayout(orientation="horizontal",
                                      size_hint=(0.9, 1))
        self.synch_btn = SynchSelector()

        if self.compare_with_cloud():
            print("comparing is done")
        else:
            print("comparing is done with else")

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

        self.search_name_btn = FindNameBtn()
        self.search_note_btn = FindNoteBtn()

        self.add_notebook_layout = BoxLayout(orientation="horizontal",
                                             size_hint=(1, 0.1),
                                             padding=(2, 0, 2, 10))
        self.add_notebook_textinput = NewSectionEntry()
        self.add_notebook_button = AddNotebookBtn()

        self.notebooks_layout = BoxLayout(orientation="vertical",
                                          size_hint=(1, 0.8))
        self.notebooks_header_layout = BoxLayout(orientation="horizontal",
                                                 size_hint=(1, 0.05))
        self.back_btn = BackBtnMain()
        self.directory_label = DirectoryLabel()
        self.edit_btn = EditBtn()
        self.noteboooks_and_inner_lvl_layout = BoxLayout(orientation="horizontal",
                 size_hint=(1, 1),
                 padding=(0,10,0,0))

        self.notebooks_list_layout = GridLayout(size_hint_y=None,
            cols=1)
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
        self.add_notebook_layout.add_widget(self.add_notebook_button)
        self.main_layout.add_widget(self.notebooks_layout)
        self.notebooks_layout.add_widget(self.notebooks_header_layout)
        self.notebooks_header_layout.add_widget(self.back_btn)
        self.notebooks_header_layout.add_widget(self.edit_btn)
        self.notebooks_header_layout.add_widget(self.directory_label)
        self.notebooks_layout.add_widget(self.noteboooks_and_inner_lvl_layout)
        self.notebooks_list_scroll.add_widget(self.notebooks_list_layout)
        self.inner_lvl_scroll.add_widget(self.inner_lvl_layout)
        self.inner_lvl_layout.add_widget(self.inner_lvl_label)

        self.back_btn.bind(on_release=self.back_btn.command)

        self.layout_notebooks_list_inner_level()
        self.open_section("TSH", "main")

        return self.main_layout

    def layout_notebooks_list_inner_level(self):
        self.noteboooks_and_inner_lvl_layout.add_widget(self.notebooks_list_scroll)
        self.noteboooks_and_inner_lvl_layout.add_widget(self.inner_lvl_scroll)


    def set_current_table(self, new_current_table):
        self.current_table = new_current_table

    def set_parent_table(self, new_parent_table):
        self.parent_table = new_parent_table

    def change_inner_lvl_text(self, to_layout, description, date):
        to_layout.insert(0, "Содержание")
        if len(to_layout) < 2:
            to_layout.insert(1, "Здесь пока пусто")
        tbl_of_cntns = "\n".join(to_layout)
        self.inner_lvl_text = f"{date[0]}\t{date[1]}\n{str(description[:500])}...\n\n{tbl_of_cntns}"
        print(self.inner_lvl_text)

    def change_sync_mode(self, checkbox, value):
        if value:
            print("active")
            self.synch_mode_var = True
            print(self.synch_mode_var)
            self.compare_with_cloud()
        else:
            self.synch_mode_var = False
            print(self.synch_mode_var)
            print("inactive")

    def start_edit(self):
        self.noteboooks_and_inner_lvl_layout.clear_widgets()
        self.text_features_layout = BoxLayout(orientation="horizontal")
        self.edit_interface = EditText()
        self.edit_btn.unbind(on_release=self.edit_btn.command)
        self.edit_btn.bind(on_release=self.edit_btn.move_notebook)
        self.edit_btn.set_text("Move")

    def set_new_note(self, new_note):
        self.compare_with_cloud()
        print("compare is done")
        try:

            value = self.Data_base[self.current_table]
            name = self.add_notebook_textinput.text.upper()
            if name in self.Data_base:
                name = self.current_table
                print(f"Name {self.add_notebook_textinput.text.upper()} already exists")
            print(name)
            self.Data_base[name] = [new_note, value[1], value[2], datetime.now()]
            if name != self.current_table:
                del self.Data_base[self.current_table]
                for key in self.Data_base:
                    if self.Data_base[key] == self.current_table:
                        value = self.Data_base[key]
                        self.Data_base[key] = [value[0, name, value[2], value[3]]]
                self.set_current_table(name)
                self.directory_label.set_text()
                with open(self.Data_base_file, "wb") as f:
                    pickle.dump(self.Data_base, f)
                    if self.synch_mode_var:
                        yadsk.upload(self)
            return "saved"
        except KeyError:
            print(f"{self.current_table} was deleted from another account")
            return "key_error"


    def open_section(self, parent_table, current_table):
        self.set_current_table(current_table)
        self.set_parent_table(parent_table)
        self.directory_label.set_text()
        print(f"{self.current_table} is currently openned")

        self.back_btn.set_state()
        self.back_btn.bind(on_release=self.back_btn.command)

        self.layout_section_btns(current_table)

    def create_new_data_base(self):
        self.Data_base = dict()
        self.Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
        self.Data_base["My notebook"] = ["New note", "main", datetime.now(), datetime.now()]
        with open(self.Data_base_file, "wb") as f:
            pickle.dump(self.Data_base, f)

    def compare_with_cloud(self, *args):
        print(f'compare fun is called, sunchmodevar is {self.synch_mode_var}')
        if self.synch_mode_var:
            print(self.synch_mode_var)
            print("if app.synch_mode_var:")
            #   check if the disk is more fresh
            #  the same if no file on the disk to compare
            if yadsk.is_cloud_more_fresh(self):
                print("if yadsk.is_cloud_more_fresh(app.synch_mode_var):")
                #  select the option
                if tk.messagebox.askyesno("Attention", "The base from the cloud is more fresh. Update from the cloud (Yes) or update the cloud (No)?"):
                    #  try to download from the cloud
                    if yadsk.download():
                        print("downloaded")
                        #  after download successfull open the file
                        with open(self.Data_base_file, "rb") as f:
                            self.Data_base = pickle.load(f)
                    #  if couldn't download the file show error
                    else:
                        tk.messagebox.showerror("Couldn't download from the cloud")
                         # open section offline
                        try:
                            with open(self.Data_base_file, "rb") as f:
                                self.Data_base = pickle.load(f)
                            #  if file not found on the disk create a new empty one
                        except FileNotFoundError:
                            self.create_new_data_base()
                #  upload to the disk option is selected
                else :
                    print("Update the disk")
                    try:
                        print("if yadsk.is_cloud_more_fresh(app.synch_mode_var):try upload")
                        #  try upload to the cloud
                        yadsk.upload(self)

                        with open(app.Data_base_file, "rb") as f:
                            app.Data_base = pickle.load(f)
                        try:
                            self.open_section(self.parent_table, self.current_table)
                        except KeyError:
                            self.open_section("TSH", "main")
                            print("KeyError while openning current notebook after synchronization")
                    #  if no file on the disk create the new one
                    except FileNotFoundError:
                        print("filenotfound")
                        self.create_new_data_base()
                    except:
                        print("connection error probably")
                        AskYesNo("Connection error porobably")
                        try:
                            with open(app.Data_base_file, "rb") as f:
                                app.Data_base = pickle.load(f)
                        except EOFError:
                            print("EOFError")
                            self.create_new_data_base()
                        except FileNotFoundError:
                            print("FileNotFoundError")
                            self.create_new_data_base()
        #   if cloud is not more fresh
            else:
                try:
                    print("try open data_base")
                    with open(self.Data_base_file, "rb") as f:
                        self.Data_base = pickle.load(f)
                except EOFError:
                    print("EOFError")
                    self.create_new_data_base()
                except FileNotFoundError:
                    print("FileNotFoundError")
                    self.create_new_data_base()

        #  if synch_mode is false
        else:
            try:
                print("try open data_base without ")
                with open(self.Data_base_file, "rb") as f:
                    self.Data_base = pickle.load(f)
            except EOFError:
                print("EOFError")
                self.create_new_data_base()
            except FileNotFoundError:
                print("FileNotFoundError")
                self.create_new_data_base()


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