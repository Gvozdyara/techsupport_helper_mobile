from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput


class MainApp(App):
    class ButtonApp(App):
        def build(self):
            self.main_layout = BoxLayout(orientation="vertical")

            self.search_layout = BoxLayout(orientation="horizontal",
                                           size_hint=(1, 0.22),
                                           padding=(2, 10))
            self.search_textinput = TextInput(multiline=False,
                                                   readonly=False,
                                                   halign="left",
                                                   font_size=50,
                                                   size_hint=(1, 1)
                                              )
            self.search_buttons_layout = BoxLayout(orientation="vertical",
                                                   size_hint=(0.25, 1))

            self.search_name_btn = Button(text="Find name",
                                          size_hint=(1, 1),
                                          pos_hint={'center_x': .5, 'center_y': .5})
            self.search_note_btn = Button(text="Find note",
                                          size_hint=(1, 1),
                                          pos_hint={'center_x': .5, 'center_y': .5})

            self.add_notebook_layout = BoxLayout(orientation="horizontal",
                                                 size_hint=(1, 0.2),
                                                 padding=(2, 0, 2, 10))
            self.add_notebook_textinput = TextInput(multiline=False,
                                                   readonly=False,
                                                   halign="left",
                                                   font_size=50)
            self.add_notebook_btn = Button(text="Add notebook",
                                                  size_hint=(.25, 1),
                                                  pos_hint={'center_x': .8, 'center_y': .5})

            self.notebooks_layout = BoxLayout(orientation="vertical")
            self.directory_label = Label(text="directory/notebook",
                                         size_hint=(1, .15))
            self.notebooks_list_layout = BoxLayout(orientation="vertical")
            self.notebook_btn = Button(text="Notebook 1",
                                       size=(75, 50),
                                       size_hint=(None, None))


            self.main_layout.add_widget(self.search_layout)
            self.search_layout.add_widget(self.search_textinput)
            self.search_layout.add_widget(self.search_buttons_layout)
            self.search_buttons_layout.add_widget(self.search_name_btn)
            self.search_buttons_layout.add_widget(self.search_note_btn)
            self.main_layout.add_widget(self.add_notebook_layout)
            self.add_notebook_layout.add_widget(self.add_notebook_textinput)
            self.add_notebook_layout.add_widget(self.add_notebook_btn)
            self.main_layout.add_widget(self.notebooks_layout)
            self.notebooks_layout.add_widget(self.directory_label)
            self.main_layout.add_widget(self.notebooks_list_layout)
            self.notebooks_list_layout.add_widget(self.notebook_btn)


            return self.main_layout

        def on_press_button(self):
            print('You pressed the button!')

    if __name__ == '__main__':
        app = ButtonApp()
        app.run()



class SectionBtn(Button):
    global Data_base
    def __init__(self, frame, button_section_name, click_cmnd, current_table):
        self.section_name = StringVar(value=button_section_name)
        super().__init__(frame, textvariable=self.section_name,
                         width=40, command=lambda: click_cmnd(current_table, self.section_name.get()))

        self.pack(fill=X, padx=3, side=TOP)
        self.current_table = current_table
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-3>", self.section_btn_right_clck_menu)
        self.frame = frame
        self.right_clck_menu = Menu(self.frame, tearoff=0)
        self.right_clck_menu.add_command(label="Rename", command=self.rename_section_interface)

    # выводим содержимое таблицы, куда наводится курсор к разделу (2 столбец)
    def on_enter(self, e):
        global section_inner_lvl_frame

        try:
            for widget in section_inner_lvl_frame.winfo_children():
                widget.destroy()
            section_inner_lvl_frame.update()
        except:
            pass

        time.sleep(0.1)
        description = Data_base[self.section_name.get()][0]
        to_layout_sections = list()
        for i in Data_base:
            if Data_base[i][1] == self.section_name.get():
                to_layout_sections.append(i)

        created_edited_time = Data_base[self.section_name.get()][2:]


        SectionInnerLvlLabel(section_inner_lvl_frame, to_layout_sections,
                             description, created_edited_time)

        return

    def on_leave(self, e):
        return

    def rename_section_interface(self):
        self.rename_win = Toplevel(self.frame)
        self.entry_widget = Entry(self.rename_win)
        self.entry_widget.pack()
        self.rename_button = ttk.Button(self.rename_win, text="Rename", command=self.rename_section)
        self.rename_button.pack()
        self.rename_win.mainloop()

    def rename_section(self):
        global Data_base
        new_table_name = self.entry_widget.get().strip().upper()
        if synch_mode_var.get():
            if yadsk.is_cloud_more_fresh(synch_mode_var):
                yadsk.download()
                with open(Data_base_file, "rb") as f:
                    Data_base = pickle.load(f)
        try:
            Data_base[new_table_name]
            messagebox.showinfo("Error", f"{new_table_name} already exists")
            self.rename_win.destroy()
        except KeyError:
            Data_base[new_table_name] = Data_base.pop(self.section_name.get())
            table_attr = Data_base[new_table_name]
            Data_base[new_table_name] = [table_attr[0], table_attr[1], table_attr[2], datetime.now()]
            for i in Data_base:
                if Data_base[i][1] == self.section_name.get():
                    i_attr = Data_base[i]
                    Data_base[i] = [i_attr[0], new_table_name, i_attr[2], i_attr[3]]

            self.section_name.set(new_table_name)
            with open(Data_base_file, "wb") as f:
                pickle.dump(Data_base, f)
            if synch_mode_var.get():
                yadsk.upload()
        self.rename_win.destroy()

    def section_btn_right_clck_menu(self, event):
        try:
            self.right_clck_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_clck_menu.grab_release()



if __name__ == '__main__':
    app = MainApp()
    app.run()