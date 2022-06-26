# encoding="utf-8"
import multiprocessing
import asyncio
import threading
from kivy import *
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.uix.dropdown import DropDown
import time
from datetime import datetime
from datetime import timedelta
import pickle
import os

import yadsk



class AskYesNoLayout(BoxLayout):
    def __init__(self, message, yes_text, no_text):
        super().__init__(orientation="vertical")
        self.yes_text = yes_text
        self.no_text = no_text
        self.label = Label(text=message)
        self.btn_layout = BoxLayout(orientation="horizontal")
        self.yes_btn = Button(text=self.yes_text)
        self.yes_btn.bind(on_release=self.yes)
        self.no_btn = Button(text=self.no_text)
        self.no_btn.bind(on_release=self.no)
        self.cancel_btn = Button(text="Cancel")

        app.noteboooks_and_inner_lvl_layout.clear_widgets()
        app.noteboooks_and_inner_lvl_layout.add_widget(self)
        self.add_widget(self.label)
        self.add_widget(self.btn_layout)
        self.btn_layout.add_widget(self.yes_btn)
        self.btn_layout.add_widget(self.no_btn)
        self.btn_layout.add_widget(self.cancel_btn)
        self.result = str()

    def yes(self, event):
        app.noteboooks_and_inner_lvl_layout.clear_widgets()
        app.write_to_log("Yes")
        return "Yes"

    def no(self, event):
        app.noteboooks_and_inner_lvl_layout.clear_widgets()
        return "No"

    def cancel(self, e):
        app.noteboooks_and_inner_lvl_layout.clear_widgets()
        return "Cancel"


class AdditionalMenu(DropDown):
    def __init__(self):
        super(AdditionalMenu, self).__init__()
        d = DumpDataBase()
        self.add_widget(d)
        q = QuitButton()
        self.add_widget(q)
        

class DumpDataBase(Button):
    def __init__(self):
        print("Dump button is created")
        super(DumpDataBase, self).__init__(text="Save",
                                           font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                                           size_hint_y=None, height=44)
        self.bind(on_release=self.dump_data_base)
        self.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))

    def dump_data_base(self, e):
        def main():
            app.change_synch_label("Saving to file")
            self.data = ""
            for i in app.Data_base.items():
                self.data = f"""{self.data}\nname: {i[0]}\n
parent= {i[1][1]}\n
{i[1][2].strftime('%d %b %Y %H:%M:%S'), i[1][3].strftime('%d %b %Y %H:%M:%S')}\n
                                {i[1][0]}"""
            with open(f"{datetime.now().strftime('%d %b %Y %H %M')} data.txt", "w", encoding="utf-8") as f:
                f.write(self.data)
            time.sleep(2)
            app.change_synch_label("Up to date")

        t = threading.Thread(target=main)
        threads.append(t)
        t.start()
        

class QuitButton(Button):
    def __init__(self):
        super(QuitButton, self).__init__(text="Quit",
                                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                                         size_hint_y=None, height=44)
        self.bind(on_release=self.quit)
        self.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))


    def quit(self, e):
        print("Quit is called")
        app.change_synch_label("Will be closed soon")
        app.is_used = False
        for t in threads:
            t.join()
            print(f"{t} is killed")
        quit()


class SynchSelector(CheckBox):
    def __init__(self):
        super().__init__(active=True)
        self.bind(active=app.change_sync_mode)
        app.clock_synch()


class AddNotebookBtn(Button):
    def __init__(self):
        super().__init__(text=self.text,
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         size_hint=(.3, 1))
        # pos_hint={'center_x': .8, 'center_y': .5})
        self.bind(on_release=app.add_notebook_textinput.add_section)
        self.text = "Add notebook"

    def set_text(self, new_text):
        self.text = new_text

    def delete_notebook(self, e):
        app.write_to_log("Start delete")
        data = app.Data_base[app.current_table]
        app.Data_base[app.current_table] = [data[0], "TRASH BIN", data[2], data[3]]
        app.write_to_log(f"app.Data_base[{app.current_table}] deleted")
        i = 1
        while i > 0:
            data_base = tuple(app.Data_base)
            for key in data_base:
                if app.Data_base[key][1] not in app.Data_base.keys() and app.Data_base[key][1] != "TSH":
                    data = app.Data_base[key]
                    app.Data_base[app.current_table] = [data[0], "TRASH BIN", data[2], data[3]]
                    app.write_to_log(f"Deleting {key}")
                    i += 1
            i -= 1
        with open(app.Data_base_file, "wb") as f:
            pickle.dump(app.Data_base, f)
        if app.synch_mode_var:
            def main():
                yadsk.upload(app)
            t = threading.Thread(target=main)
            t.start()
            threads.append(t)
        # except KeyError:
        #     AskYesNo(f"There is no {app.current_table} notebook")
        app.edit_interface.is_used = False
        app.notebooks_header_layout.remove_widget(app.edit_interface.undo_btn)
        app.notebooks_header_layout.add_widget(app.directory_label)

        self.unbind(on_release=self.delete_notebook)
        self.bind(on_release=app.add_notebook_textinput.add_section)
        self.set_text("Add notebook")
        app.add_notebook_textinput.set_initial_text("")
        app.noteboooks_and_inner_lvl_layout.clear_widgets()
        app.layout_notebooks_list_inner_level()
        app.back_btn.unbind(on_release=app.back_btn.save_command)
        app.back_btn.bind(on_release=app.back_btn.command)
        app.edit_btn.unbind(on_release=app.edit_btn.move_notebook)
        app.edit_btn.bind(on_release=app.edit_btn.command)
        app.edit_btn.set_text("Edit")
        app.write_to_log(
            f"will be openned {app.parent_table}, with its parent {app.Data_base[app.parent_table][1]}")
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
            if app.search_textinput.text.lower() in app.Data_base[key][0].lower():
                note = app.Data_base[key][0]
                if len(note) > 202:
                    start_index = note.find(app.search_textinput.text)
                    if start_index > 99:
                        short = note[start_index - 100:start_index + 100]
                    else:
                        short = note[0:start_index + 200]
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
        super().__init__(text="Find\nnote",
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         size_hint=(0.15, 1))
        self.bind(on_release=self.start_search)

    def start_search(self, e):
        app.write_to_log("start search")
        SearchInterface("note")


class FindNameBtn(Button):
    def __init__(self):
        super().__init__(text="Find\nname",
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         size_hint=(0.15, 1))

        self.bind(on_release=self.start_search)

    def start_search(self, e):
        app.write_to_log("start search")
        SearchInterface("name")


class NewSectionEntry(TextInput):
    def __init__(self):
        super().__init__(multiline=False,
                         readonly=False,
                         halign="left",
                         font_size=24,
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         size_hint=(.7, 1))

    def add_section(self, e):
        self.section_title = self.text.upper()

        if self.section_title != "":
            self.text = ""
            # if not section_title in existing_sections:
        try:
            app.Data_base[self.section_title]
            app.write_to_log(f"{self.section_title} already exists")

            def main():
                print("start label change")
                app.change_synch_label("Already exist")
                time.sleep(1.5)
                app.change_synch_label("Up to date")
            t=threading.Thread(target=main)
            t.start()
            threads.append(t)
        except KeyError:
            self.add_table_to_tbls_list()



    def add_table_to_tbls_list(self):
        app.Data_base[self.section_title] = ["Empty", app.current_table, datetime.now(), datetime.now()]
        with open(app.Data_base_file, "wb") as f:
            pickle.dump(app.Data_base, f)
        if app.synch_mode_var:
            t = threading.Thread(target=yadsk.upload, args=(app,))
            t.start()
            threads.append(t)
        btn = SectionBtn(self.section_title, app.current_table)

    def set_initial_text(self, new_text):
        self.text = new_text


class BackBtnMain(Button):
    def __init__(self):
        self.is_inactive = False
        super().__init__(text="Back",
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         size_hint=(0.25, 1),
                         disabled=self.is_inactive)

    def command(self, e):
        app.write_to_log("usual return")
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
        app.write_to_log("saving")
        new_note = app.edit_interface.text
        if app.set_new_note(new_note) == "saved":
            app.noteboooks_and_inner_lvl_layout.clear_widgets()
            app.add_notebook_textinput.set_initial_text("")
            app.layout_notebooks_list_inner_level()
        elif app.set_new_note(new_note) == "key_error":
            app.parent_table = app.Data_base[app.parent_table][1]
            app.noteboooks_and_inner_lvl_layout.clear_widgets()
            app.add_notebook_textinput.set_initial_text("")
            app.layout_notebooks_list_inner_level()

        
        self.unbind(on_release=self.save_command)
        self.bind(on_release=self.command)
        app.add_notebook_button.set_text("Add notebook")
        app.add_notebook_button.unbind(on_release=app.add_notebook_button.delete_notebook)
        app.add_notebook_button.bind(on_release=app.add_notebook_textinput.add_section)
        app.edit_btn.unbind(on_release=app.edit_btn.move_notebook)
        app.edit_btn.bind(on_release=app.edit_btn.command)
        app.edit_btn.set_text("Edit")
        app.write_to_log("end of save_command, back button should be configured")


        app.edit_interface.is_used = False
        app.notebooks_header_layout.remove_widget(app.edit_interface.undo_btn)
        app.notebooks_header_layout.add_widget(app.directory_label)


class SectionBtn(Button):
    def __init__(self, section, parent_table, *args):
        super().__init__(text=section,
                         size_hint=(1, None),
                         text_size=(app.noteboooks_and_inner_lvl_layout.width / 2, None),
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         halign="center",
                         height=self.texture_size[1] + dp(50))
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
        app.write_to_log(f"open section {self.section} from {self.parent_table}")

    def show_inner_lvl(self, *args):
        for i in app.Data_base:
            if app.Data_base[i][1] == self.section:
                self.to_layout_sections.append(i)
        self.to_layout_sections = list(reversed(self.to_layout_sections))

        app.inner_lvl_label.update_text(self.to_layout_sections, self.description[:500], self.created_edited_time)


class InnerLvlLabel(Label):
    def __init__(self):
        self.text = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        super().__init__(text=self.text,
                         text_size=(self.width *3.8, None),
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         width=self.texture_size[0],
                         size_hint=(1, 1),
                         valign="top",
                         pos_hint={'center_x': .8, 'bottom_y': 0}
                         )

    def update_text(self, to_layout, description, date):
        to_layout.insert(0, "Содержание")
        if len(to_layout) < 2:
            to_layout.insert(1, "Здесь пока пусто")
        tbl_of_cntns = "\n\n".join(to_layout)
        self.text = f"{date[0]}\t{date[1]}\n{str(description[:1000])}...\n\n{tbl_of_cntns}"


class DirectoryLabel(Label):
    def __init__(self):
        super().__init__(text=self.text,
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         size_hint=(0.5, 1))
        self.text = "TSH/main"

    def set_text(self):
        self.text = f"{app.parent_table}/{app.current_table}"


class EditBtn(Button):
    def __init__(self):
        super().__init__(text=self.text,
                         font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                         size_hint=(0.25, 1))
        self.bound_notebook = app.current_table
        self.bind(on_release=self.command)
        self.text = "Edit"

    def set_text(self, new_text):
        self.text = new_text

    def set_current(self):
        self.bound_notebook = app.current_table

    def command(self, e):
        if app.current_table != "main":
            self.set_current()
            app.start_edit()

    def move_notebook(self, e):
        app.write_to_log("saving before moving")
        new_note = app.edit_interface.text

        if app.set_new_note(new_note) == "saved":
            app.noteboooks_and_inner_lvl_layout.clear_widgets()
            app.add_notebook_textinput.set_initial_text("")
            app.layout_notebooks_list_inner_level()
        elif app.set_new_note(new_note) == "key_error":
            app.parent_table = app.Data_base[app.parent_table][1]
            app.noteboooks_and_inner_lvl_layout.clear_widgets()
            app.add_notebook_textinput.set_initial_text("")
            app.layout_notebooks_list_inner_level()

        app.edit_interface.is_used = False
        app.notebooks_header_layout.remove_widget(app.edit_interface.undo_btn)
        app.notebooks_header_layout.add_widget(app.directory_label)

        app.back_btn.unbind(on_release=app.back_btn.save_command)
        app.back_btn.bind(on_release=app.back_btn.command)
        app.add_notebook_button.set_text("Add notebook")
        app.add_notebook_button.unbind(on_release=app.add_notebook_button.delete_notebook)
        app.add_notebook_button.bind(on_release=app.add_notebook_textinput.add_section)
        self.set_current()
        current_parent = app.Data_base[self.bound_notebook][1]
        try:
            app.open_section(app.Data_base[current_parent][1], self.bound_notebook)
        except KeyError:
            app.open_section("TSH", "main")
        self.unbind(on_release=self.move_notebook)
        self.bind(on_release=self.set_new_parent_while_move)
        self.set_text("Select")

    def set_new_parent_while_move(self, e):

        value = app.Data_base[self.bound_notebook]
        if self.bound_notebook != app.current_table:
            app.Data_base[self.bound_notebook] = [value[0], app.current_table, value[2], value[3]]
            with open(app.Data_base_file, "wb") as f:
                pickle.dump(app.Data_base, f)
            if app.synch_mode_var:
                t = threading.Thread(target=yadsk.upload, args=(app,))
                t.start()
                threads.append(t)

        self.unbind(on_release=self.set_new_parent_while_move)
        self.bind(on_release=self.command)
        self.set_text("Edit")


class EditText(TextInput):
    def __init__(self):
        self.initial_text = app.Data_base[app.current_table][0]
        self.font_name = os.path.join("TruetypewriterPolyglott-mELa.ttf")
        self.font_size = int(24)
        self.text_alignce = str("left")
        self.bold = bool(False)
        self.italic = bool(True)
        self.underline = bool(False)
        self.scrolling = ScrollView(effect_cls=ScrollEffect)

        self.change_history = [self.initial_text]
        self.change_history_ind = -1
        self.is_used = True
        app.notebooks_header_layout.remove_widget(app.directory_label)
        self.undo_btn = Button(text="Undo", size_hint_x=0.5,
                               font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"))
        self.undo_btn.bind(on_release=self.undo)
        app.notebooks_header_layout.add_widget(self.undo_btn)
        super().__init__(text=self.initial_text,
                         font_size=self.font_size,
                         size_hint=(1, 1)
                         )
        app.add_notebook_textinput.set_initial_text(app.current_table)
        app.noteboooks_and_inner_lvl_layout.add_widget(self.scrolling)
        self.scrolling.add_widget(self)
        self.bind(minimum_height=self.setter("height"))
        app.back_btn.unbind(on_release=app.back_btn.command)
        app.back_btn.bind(on_release=app.back_btn.save_command)
        app.add_notebook_button.unbind(on_release=app.add_notebook_textinput.add_section)
        app.add_notebook_button.bind(on_release=app.add_notebook_button.delete_notebook)
        app.add_notebook_button.set_text("Delete notebook")
        #  save chang history for undo button
        self.change_history_saver()
        #  check if no change to close the editor so no 
        Clock.schedule_interval(self.check_activity, 300)

    def set_bold(self, e, value):
        self.bold = value

    def set_italic(self, e, value):
        self.italic = value

    def set_underline(self, e, value):
        self.underline = value

    def change_history_saver(self):

        def add_change():
            while self.is_used == True:
                try:
                    if self.text != self.change_history[-1]:
                        self.change_history.append(self.text)
                        time.sleep(1)
                    else:
                        time.sleep(1)
                except IndexError as e:
                    if self.text != self.initial_text:
                        self.change_history.append(self.text)
                        time.sleep(1)
                    else:
                        time.sleep(1)

        self.t = threading.Thread(target=add_change)
        self.t.start()
        threads.append(self.t)

    def check_activity(self, dt):
        while self.is_used:
            print("Start of  checking state cycle")
            text_state = self.text
            if text_state == self.text:
                print("saving")
                app.back_btn.save_command()
            else:
                continue
    

    def undo(self, e):
        try:
            self.change_history.pop()
            self.text = self.change_history[-1][0]

        except Exception as e:
            print(f"{e=}")

    def __del__(self):
        self.is_used = False


class MainApp(App):

    def __init__(self):
        super().__init__()
        self.synch_mode_var = True
        self.inner_lvl_text = ""
        self.Data_base_file = "techsupport_base"
        self.Data_base = dict()
        self.current_table = "main"
        self.parent_table = "TSH"
        self.is_used = True
        try:
            with open(self.Data_base_file, "rb") as f:
                self.Data_base = pickle.load(f)
        except FileNotFoundError or EOFError:
            self.create_new_data_base()

    def build(self):
        self.main_layout = BoxLayout(orientation="vertical")

        self.top_menu_layout = BoxLayout(orientation="horizontal",
                                         size_hint=(1, 0.05))

        self.top_dot_menu_btn = Button(text="...",
                                       size_hint=(.1, 1))
        self.dropdown = AdditionalMenu()

        self.top_dot_menu_btn.bind(on_release=self.dropdown.open)

        self.synch_layout = BoxLayout(orientation="horizontal",
                                      size_hint=(0.9, 1))
        self.synch_btn = SynchSelector()

        self.synch_label = Label(text="Synchronization",
                                 font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
                                 size_hint=(0.5, 1))

        self.search_layout = BoxLayout(orientation="horizontal",
                                       size_hint=(1, 0.1),
                                       padding=(2, 10))
        self.search_textinput = TextInput(multiline=False,
                                          readonly=False,
                                          halign="left",
                                          font_size=24,
                                          font_name=os.path.join("TruetypewriterPolyglott-mELa.ttf"),
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
                                                         padding=(0, 10, 0, 0))

        self.notebooks_list_layout = GridLayout(size_hint_y=None,
                                                cols=1)
        self.notebooks_list_layout.bind(minimum_height=self.notebooks_list_layout.setter('height'))

        
        self.inner_lvl_layout = GridLayout(cols=1, size_hint_y=2, size_hint_x=1,
                                           pos_hint={"left_x": 0, "top_y": 0})
        self.inner_lvl_layout.bind(minimum_height=self.inner_lvl_layout.setter('height'))

        self.inner_lvl_scroll = ScrollView()
        self.inner_lvl_scroll.effect_cls = ScrollEffect

        self.notebooks_list_scroll = ScrollView()
        self.notebooks_list_scroll.effect_cls = ScrollEffect
        self.inner_lvl_label = InnerLvlLabel()

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

    def change_sync_mode(self, event, value):
        if value:
            self.write_to_log("active")
            self.synch_mode_var = True
            self.compare_with_cloud()
            self.clock_synch()
        else:
            self.synch_mode_var = False
            self.write_to_log("inactive")

    def start_edit(self):
        self.noteboooks_and_inner_lvl_layout.clear_widgets()
        self.text_features_layout = BoxLayout(orientation="horizontal")
        self.edit_interface = EditText()
        self.edit_btn.unbind(on_release=self.edit_btn.command)
        self.edit_btn.bind(on_release=self.edit_btn.move_notebook)
        self.edit_btn.set_text("Move")

    def set_new_note(self, new_note):

        try:
            value = self.Data_base[self.current_table]
            name = self.add_notebook_textinput.text.upper()
            is_note_changed = False
            is_name_changed = False
            if new_note != app.edit_interface.initial_text:
                value = [new_note, value[1], value[2], datetime.now()]
                self.Data_base[self.current_table] = value
                self.write_to_log(f"{new_note} is added to {name}")
                is_note_changed = True
            if name != self.current_table:
                if name in self.Data_base.keys():
                    self.write_to_log(f"Name {name} already exists")
                    self.change_synch_label("Choose another name")
                    name = self.current_table
                else:
                    self.Data_base[name] = value
                    self.write_to_log(f"{new_note} is added to {name}")
                    del self.Data_base[self.current_table]
                    for key in self.Data_base:
                        if self.Data_base[key][1] == self.current_table:
                            value = self.Data_base[key]
                            self.Data_base[key] = [value[0], name, value[2], value[3]]
                    self.set_current_table(name)
                    self.directory_label.set_text()
                    is_name_changed = True

            if is_name_changed or is_note_changed:
                
                def update_parents_last_edit(notebook):
                    val = self.Data_base[notebook]
                    del self.Data_base[notebook]
                    self.Data_base[notebook] = [val[0],val[1],val[2],datetime.now()]
                    if val[1] != "main":
                        update_parents_last_edit(val[1])
                        
                update_parents_last_edit(name)
                
                with open(self.Data_base_file, "wb") as f:
                    pickle.dump(self.Data_base, f)
                if self.synch_mode_var:
                    def main(self):
                        self.change_synch_label("Saved. Uploading...")
                        yadsk.upload(app)
                        self.change_synch_label("Up to date")

                    t = threading.Thread(target=main, args=(self,))
                    t.start()
                    threads.append(t)
                else:
                    def main():
                        self.change_synch_label("Saving")
                        time.sleep(0.3)
                        self.change_synch_label("Up to date")

                    t = threading.Thread(target=main)
                    t.start()
                    threads.append(t)
                return "saved"
            else:
                return "saved"
        except KeyError:
            self.write_to_log(f"{self.current_table} was deleted from another account")
            return "key_error"

    def open_section(self, parent_table, current_table):
        self.set_current_table(current_table)
        self.set_parent_table(parent_table)
        self.directory_label.set_text()
        self.write_to_log(f"{self.current_table} is currently openned")

        self.back_btn.set_state()
        self.back_btn.bind(on_release=self.back_btn.command)

        self.layout_section_btns(current_table)

    def create_new_data_base(self):
        self.Data_base = dict()
        self.Data_base["main"] = ["Main folder", "TSH", datetime.now(), datetime.now()]
        self.Data_base["MY NOTEBOOK"] = ["New note", "main", datetime.now(), datetime.now()]
        self.Data_base["TRASH BIN"] = ["Trash belongs here", "main", datetime.now(), datetime.now()]
        with open(self.Data_base_file, "wb") as f:
            pickle.dump(self.Data_base, f)

    def change_synch_label(self, name):
        self.synch_label.text = name

    def compare_with_cloud(self, *args):
        self.write_to_log(f'compare fun is called, synchmodevar is {self.synch_mode_var}')
        if self.synch_mode_var:
            self.change_synch_label("Check")
            self.write_to_log(f"Syncronization is {self.synch_mode_var}")
            #   check if the disk is more fresh
            #  the same if no file on the disk to compare
            comparing_result = yadsk.is_cloud_more_fresh(self)
            if comparing_result == "Cloud":
                self.change_synch_label("In progress")
                self.write_to_log("Cloud is more fresh")
                #  select the option
                if True:
                    #  try to download from the cloud
                    if yadsk.download():
                        self.write_to_log("downloaded")
                        #  after download successfull merge
                        with open(self.Data_base_file, "rb") as f:
                            self.cloud_base = pickle.load(f)
                        self.merge_bases(self.cloud_base)
                        self.change_synch_label("Up to date")
                    #  if couldn't download the file show error
                    else:
                        self.write_to_log("Couldn't download")
                        self.change_synch_label("Can't download")
                        # open section offline
                        try:
                            with open(self.Data_base_file, "rb") as f:
                                self.Data_base = pickle.load(f)
                            #  if file not found on the disk create a new empty one
                        except FileNotFoundError:
                            self.create_new_data_base()
                  #  (not used) upload to the cloud option is selected
                else:
                    self.write_to_log("Uploading to the cloud is selected")
                    try:
                        self.write_to_log("Trying to upload")
                        #  try upload to the cloud
                        yadsk.upload(self)
               
                        with open(app.Data_base_file, "rb") as f:
                            app.Data_base = pickle.load(f)
                        try:
                            self.open_section(self.parent_table, self.current_table)
                        except KeyError:
                            self.open_section("TSH", "main")
                            self.write_to_log("KeyError while openning current notebook after synchronization")
                    #  if no file on the disk create the new one
                    except FileNotFoundError:
                        self.write_to_log("filenotfound")
                        self.create_new_data_base()
                    except:
                        self.write_to_log("connection error probably, unknown exception")
                        tk.messagebox.showinfo("Connection error porobably")
                        try:
                            with open(app.Data_base_file, "rb") as f:
                                app.Data_base = pickle.load(f)
                        except EOFError:
                            self.write_to_log("EOFError")
                            self.create_new_data_base()
                        except FileNotFoundError:
                            self.write_to_log("FileNotFoundError")
                            self.create_new_data_base()
              # if cloud is not more fresh
            elif comparing_result == "Disk":
                try:
                    self.write_to_log("Merging")
                    yadsk.download()
                    with open(self.Data_base_file, "rb") as f:
                        self.cloud_base = pickle.load(f)
                    self.merge_bases(self.cloud_base)
                    self.change_synch_label("Up to date")
                except EOFError:
                    self.write_to_log("EOFError")
                    self.create_new_data_base()
                    self.change_synch_label("No file")
                except FileNotFoundError:
                    self.write_to_log("FileNotFoundError")
                    self.create_new_data_base()
                    self.change_synch_label("No file")
            else:
                self.change_synch_label(comparing_result)

        #  if synch_mode is false
        else:
            self.change_synch_label("Synch is OFF")
            try:
                self.write_to_log("trying to read local file")
                with open(self.Data_base_file, "rb") as f:
                    self.Data_base = pickle.load(f)
            except EOFError:
                self.write_to_log("EOFError while reading local file")
                self.create_new_data_base()
            except FileNotFoundError:
                self.write_to_log("FileNotFoundError while reading local file")
                self.create_new_data_base()

    def merge_bases(self, cloud_base, *args):
        
        merged_base = dict()
        #  compare data_bases
        for i in cloud_base.keys():
            #  check if the item is in both data_bases
            if i in self.Data_base.keys():
                #  select the newest
                #  if datetime.strptime(cloud_base[i][3], "%d %b %Y %H:%M:%S") >= datetime.strptime(self.Data_base[i][3], "%d %b %Y %H:%M:%S"):
                if cloud_base[i][3] >= self.Data_base[i][3]:
                    data = cloud_base[i]
                    merged_base[i] = [data[0],data[1],data[2],data[3]]
                    del self.Data_base[i]
                else:
                    data = self.Data_base[i]
                    merged_base[i] = [data[0],data[1],data[2],data[3]]
                    del self.Data_base[i]
            else:
                data = cloud_base[i]
                merged_base[i] = [data[0],data[1],data[2],data[3]]
        for i in self.Data_base.keys():
            data = self.Data_base[i]
            merged_base[i] = [data[0],data[1],data[2],data[3]]

        self.Data_base = merged_base

        with open(self.Data_base_file, "wb") as f:
            pickle.dump(self.Data_base, f)

    def layout_section_btns(self, inner_table):

        self.notebooks_list_layout.clear_widgets()

        self.to_layout_list = list()
        if inner_table == "main":
            self.to_layout_list.append("TRASH BIN")
        for i in self.Data_base:
            if self.Data_base[i][1] == inner_table:
                if i != "TRASH BIN":
                    self.to_layout_list.append(i)

        for item in reversed(self.to_layout_list):
            SectionBtn(item, inner_table)

    def askyesnocancel(self, message, yes_text, no_text):
        ask_interface = AskYesNoLayout(message, yes_text, no_text)
        time.sleep(2)
        while True:
            if ask_interface.result == "Yes":
                return True
            if ask_interface.result == "No":
                return False

    def write_to_log(self, message):
        with open("log.txt", "a", encoding="utf8") as f:
            f.write(f"{datetime.now()}\n{message}\n")

    def clock_synch(self):
        def tick_synch():
            while self.is_used:
                if self.synch_mode_var:
                    print("iteration")
                    self.compare_with_cloud()
                    time.sleep(30)

        self.t = threading.Thread(target=tick_synch)
        self.t.start()
        threads.append(self.t)


if __name__ == '__main__':
    threads = []
    app = MainApp()
    app.run()
    quit()
    # for t in threads:
    #     t.join()
