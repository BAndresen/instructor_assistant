
"""PADI Scuba Diving Instructors are required to complete the 'Record_and_Referral_Form' for every student
after the PADI Open Water Course. This 'Instructor Assistant' aims to make that process fast and easy.

Additionally, this program is a project to help me learn Python.

Author: Brendan Andresen <brendan.development@pm.me>
Created: May 6th, 2023
"""

__version__ = "0.1.0"

import datetime
import os
import tkinter
import json
import time
import hashlib
import secrets
import customtkinter  # I modified ctk.entry.py line 388 def get() to only return entry.get().
import pandas
import configparser
import webbrowser

from tkcalendar import DateEntry
from fillpdf import fillpdfs
from tkinter import Toplevel, Menu, messagebox, filedialog, PhotoImage

# TODO refactor and decouple program

# Import UI label lists
if not os.path.exists("gui_setup_labels.json"):
    messagebox.showerror(message="missing configuration file 'gui_setup_labels.json")
else:
    with open("gui_setup_labels.json", "r") as data:
        date_file = json.load(data)
        cw_label_list = date_file["cw_water_list"]
        kd_string_list = date_file["kd_string_list"]
        ow_string_list = date_file["ow_string_list"]

if os.path.exists("Record_and_Referral_Form.pdf"):
    fields = fillpdfs.get_form_fields("Record_and_Referral_Form.pdf")
else:
    messagebox.showerror(message="Missing 'Record_and_Referral_Form.pdf'")

today = datetime.datetime.today()

# --------------------------- THEME --------------------------------- #

# set a default save path for pdf to users desktop
default_desktop_save_path = os.path.join(os.path.join(os.environ["USERPROFILE"]),"Desktop")

if os.path.exists("config.ini"):
    config = configparser.ConfigParser()
    config.read("config.ini")
    theme = config["style"]["theme"]
    config["save path"]["student_record_path"] = default_desktop_save_path

    with open("config.ini", "w") as configfile:
        config.write(configfile)


else:
    messagebox.showerror(message="Missing 'config.ini' file")

if os.path.exists("themes.json"):
    with open("themes.json", "r") as file:
        theme_dict = json.load(file)
        set_text_color = theme_dict[theme]["set_text_color"]
        reset_main_text_color = theme_dict[theme]["reset_main_text_color"]
        listbox_color = theme_dict[theme]["listbox_color"]
        text_color = theme_dict[theme]["text_color"]
        background_color = theme_dict[theme]["background_color"]
        frame_color = theme_dict[theme]["frame_color"]
        main_button_color = theme_dict[theme]["main_button_color"]
        main_button_color_hover = theme_dict[theme]["main_button_color_hover"]
        main_button_text_color = theme_dict[theme]["main_button_text_color"]
        switch_on_color = theme_dict[theme]["switch_on_color"]
        switch_off_color = theme_dict[theme]["switch_off_color"]
        switch_button_color = theme_dict[theme]["switch_button_color"]
        switch_hover_color = theme_dict[theme]["switch_hover_color"]
        master_switch_on_color = theme_dict[theme]["master_switch_on_color"]
        master_switch_off_color = theme_dict[theme]["master_switch_off_color"]
        master_switch_button_color = theme_dict[theme]["master_switch_button_color"]
        master_switch_hover_color = theme_dict[theme]["master_switch_hover_color"]
else:
    messagebox.showerror(message="Missing 'themes.json' file")

# theme constants
student_listbox_height = 9
instructor_listbox_height = 7
font = ("roboto", "10")
header = ("roboto", "14")

# Student Information Global Dictionary
student_dict_global = {}


def or_elearning_select():
    """Toggle Checkboxes for Knowledge Development"""
    if kd_switch_list[0].get() == 1:
        [switches.deselect() for switches in kd_switch_list if kd_switch_list.index(switches) < 5]
        [kr_check.deselect() for kr_check in kr_checkbox_list if kr_checkbox_list.index(kr_check) < 5]
        [vid_check.deselect() for vid_check in kd_video_checkbox_list if kd_video_checkbox_list.index(vid_check) < 5]
        kd_switch_list[5].select()
        kd_video_checkbox_list[5].select()
        kr_checkbox_list[5].select()
        select_elearning_button.configure(text="Manual & Classroom")

    else:
        [switches.select() for switches in kd_switch_list if kd_switch_list.index(switches) < 5]
        [kr_check.select() for kr_check in kr_checkbox_list if kr_checkbox_list.index(kr_check) < 5]
        [vid_check.select() for vid_check in kd_video_checkbox_list if kd_video_checkbox_list.index(vid_check) < 5]
        kd_switch_list[5].deselect()
        kd_video_checkbox_list[5].deselect()
        kr_checkbox_list[5].deselect()
        select_elearning_button.configure(text="Elearning")


def speed_calc_decorator(function):
    """Check function speed"""

    def wrapper_function():
        start = time.time()
        function()
        end = time.time()
        print(f'{function.__name__} run speed: {end - start}s')

    return wrapper_function


def new_template():
    """New UI Window for user to make a new custom Dive Template.  Often Instructors complete skills in a
    consistent sequence.  Applying a dive template allows instructors to autofill sections based on information
    from other sections"""
    new_template_window = Toplevel(window)
    new_template_window.config(pady=50, padx=50)
    new_template_window.geometry("1400x1000+200+5")
    new_template_window.grid_columnconfigure(0, weight=1)
    new_template_window.grid_columnconfigure(1, weight=1)
    new_template_window.grid_rowconfigure(0, weight=1)
    new_template_window.grid_rowconfigure(1, weight=1)

    # --- Title Template
    template_title_frame = customtkinter.CTkFrame(new_template_window, fg_color=frame_color)
    template_title_frame.grid(row=0, column=0, padx=10, pady=10, stick="nsew")
    template_name_entry = customtkinter.CTkEntry(template_title_frame, width=200, height=30)
    template_name_entry.grid(column=1, row=0, pady=20, sticky="w")
    template_name_label = tkinter.Label(template_title_frame, text="Template Name:", font=header,
                                        background=frame_color)
    template_name_label.grid(column=0, row=0, pady=20, padx=(20, 10))

    # ----------------------- CONFINED WATER FRAME TEMPLATE WINDOW -------------------- #

    template_confined_frame = customtkinter.CTkFrame(new_template_window, fg_color=frame_color)
    template_confined_frame.grid(row=1, column=0, ipadx=10, ipady=10, padx=10, pady=10, sticky="nsew")

    confined_water_string_template_list = [
        "Confined Water 1 (Code: 0)",
        "Confined Water 2 (Code: 1)",
        "Confined Water 3 (Code: 2)",
        "Confined Water 4 (Code: 3)",
        "Confined Water 5 (Code: 4)",
        "200M Swim (Code: 5)",
        "10min Float (Code: 6)",
        "Equipment Prep (Code: 7)",
        "Disconnect LP Hose (Code: 8)",
        "Loose Cylinder Band (Code: 9)",
        "Weight System Remove & Replace (Code: 10)",
        "Emergency Weight Drop (Code: 11)",
        "Skin Diver (Code: 12)",
        "Drysuit Orientation (Code: 13)",
        "All Confined Water Skills (Code: 14)",
    ]

    for i in range(15):
        string = tkinter.Label(template_confined_frame, text=confined_water_string_template_list[i],
                               font=font, background=frame_color)
        string.grid(row=i + 1, column=0, sticky="e", padx=(20, 5))
        confined_water_string_template_list.append(string)

    confined_water_section_set_rule = tkinter.Label(template_confined_frame, text="Confined Water", font=header,
                                                    background=frame_color)
    confined_water_section_set_rule.grid(row=0, column=0, sticky="w", padx=(20, 0), pady=(10, 0))

    def switch_press(switch_index):
        """changes entry placeholder text"""
        if cw_switch_list[switch_index].get() == 0:
            cw_entry_list[switch_index].configure(placeholder_text="--")
        else:
            cw_entry_list[switch_index].configure(placeholder_text=switch_index)

    def reset():
        if cw_switch_list[0].get() == 1:
            for cw in range(15):
                cw_entry_list[cw].configure(placeholder_text="--")
                cw_switch_list[cw].deselect()

        else:
            for cw in range(15):
                cw_entry_list[cw].configure(placeholder_text=cw)
                cw_switch_list[cw].select()

    kd_reset_swtich = customtkinter.CTkSwitch(template_confined_frame, text="", command=reset,
                                              fg_color=master_switch_off_color,
                                              progress_color=master_switch_on_color,
                                              button_color=master_switch_button_color,
                                              button_hover_color=master_switch_hover_color, )

    kd_reset_swtich.select()
    kd_reset_swtich.grid(row=0, column=2, pady=(20, 5), padx=(0))

    # create row of switches
    cw_switch_list = []
    for i in range(15):
        switch = customtkinter.CTkSwitch(template_confined_frame, text="",
                                         command=lambda p=i: switch_press(p),
                                         fg_color=switch_off_color,
                                         progress_color=switch_on_color,
                                         button_color=switch_button_color,
                                         button_hover_color=switch_hover_color,
                                         )
        switch.grid(row=i + 1, column=2, padx=10)
        switch.select()
        cw_switch_list.append(switch)

    # create row of entries
    cw_entry_list = []
    for n in range(15):
        cw_entry = customtkinter.CTkEntry(template_confined_frame, width=40,
                                          placeholder_text_color=text_color, placeholder_text=n, height=25)
        cw_entry.grid(row=n + 1, column=1, pady=2)
        cw_entry_list.append(cw_entry)

    # --------------------------- KNOWLEDGE DEVELOPMENT TEMPLATE WINDOW ----------------- #

    template_knowledge_frame = customtkinter.CTkFrame(new_template_window, fg_color=frame_color)
    template_knowledge_frame.grid(row=0, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky="nsew")
    knowledge_development_title = tkinter.Label(template_knowledge_frame, text="Knowledge Development",
                                                font=header, background=frame_color)
    knowledge_development_title.grid(row=0, column=0, padx=20, pady=(20, 0))
    pass_exam_set_rule = tkinter.Label(template_knowledge_frame, text="Quiz/Exam", font=font, background=frame_color)
    pass_exam_set_rule.grid(row=0, column=3, columnspan=1, pady=(20, 0), padx=(0, 20))

    knowledge_string_template_list = [
        "Section 1 (Code: 15)",
        "Section 2 (Code: 16)",
        "Section 3 (Code: 17)",
        "Section 4 (Code: 18)",
        "Section 5 (Code: 19)",
        "OR Elearning (Code: 20)",
        "All Knowledge Development (Code: 21)",
    ]

    kd_switch_list = []

    def switch_press_kd(switch_index):
        """changes entry placeholder text"""
        if kd_switch_list[switch_index].get() == 0:
            kd_entry_list[switch_index].configure(placeholder_text="--")
        else:
            kd_entry_list[switch_index].configure(placeholder_text=switch_index + 15)

    def reset_kd():
        if kd_switch_list[0].get() == 1:
            for kd in range(7):
                kd_entry_list[kd].configure(placeholder_text="--")
                kd_switch_list[kd].deselect()

        else:
            for kd in range(7):
                kd_entry_list[kd].configure(placeholder_text=kd + 15)
                kd_switch_list[kd].select()

    kd_reset_swtich = customtkinter.CTkSwitch(template_knowledge_frame, text="", command=reset_kd,
                                              fg_color=master_switch_off_color,
                                              progress_color=master_switch_on_color,
                                              button_color=master_switch_button_color,
                                              button_hover_color=master_switch_hover_color, )

    kd_reset_swtich.select()
    kd_reset_swtich.grid(row=0, column=2, pady=(15, 0), padx=(7, 0))

    for n in range(7):
        kd_string = tkinter.Label(template_knowledge_frame, text=knowledge_string_template_list[n],
                                  font=font, background=frame_color)
        kd_string.grid(row=n + 1, column=0, padx=(33, 5), sticky="e")

    for i in range(7):
        switch = customtkinter.CTkSwitch(template_knowledge_frame, text="",
                                         command=lambda p=i: switch_press_kd(p),
                                         fg_color=switch_off_color,
                                         progress_color=switch_on_color,
                                         button_color=switch_button_color,
                                         button_hover_color=switch_hover_color
                                         )
        switch.grid(row=i + 1, column=2, padx=(10, 0))
        switch.select()
        kd_switch_list.append(switch)

    # create row of entries
    kd_entry_list = []
    for n in range(7):
        kd_entry = customtkinter.CTkEntry(template_knowledge_frame, placeholder_text=(n + 15),
                                          width=40,
                                          placeholder_text_color=text_color,
                                          height=25
                                          )
        kd_entry.grid(row=n + 1, column=1, pady=2)
        kd_entry_list.append(kd_entry)

    kd_exam_entry_list = []
    for n in range(6):
        kd_entry_exam = customtkinter.CTkEntry(template_knowledge_frame, placeholder_text=(""), width=60, height=25)
        kd_entry_exam.grid(row=n + 1, column=3, columnspan=1, padx=(0, 20))
        kd_exam_entry_list.append(kd_entry_exam)

    # ----------------------------- OPEN WATER -------------------------- #

    template_open_water = customtkinter.CTkFrame(new_template_window, fg_color=frame_color)
    template_open_water.grid(row=1, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky="nsew")

    # --- Open Water Dives Labels - Set Rule Window
    ow_dives_label_set_rule = tkinter.Label(template_open_water, text="Open Water Dives", font=header,
                                            background=frame_color)
    ow_dives_label_set_rule.grid(row=0, column=0, pady=(10, 0), padx=(0, 10))

    ow_string_list_template = [
        "Open Water 1 (Code: 22)",
        "Open Water 2 (Code: 23)",
        "Open Water 3 (Code: 24)",
        "Open Water 4 (Code: 25)",
        "Cramp Removal",
        "Snorkel/Regulator Exchange",
        "Inflatable Signal Tube",
        "Emergency Weight Drop",
        "Surface Swim with Compass",
        "Tired Diver Tow",
        "Remove/Replace Scuba",
        "Remove/Replace Weight",
        "CESA",
        "UW Compass Navigation",
        "All Open Water Dive Flex Skills (Code: 26)",
        "All Certification Requirements (Code: 27)",
    ]

    def switch_press_ow(switch_index):
        """changes entry placeholder text"""
        if ow_switch_list[switch_index].get() == 0:
            ow_entry_list[switch_index].configure(placeholder_text="--")
        else:
            if 3 < switch_index < 14:
                ow_entry_list[switch_index].configure(placeholder_text="")

            elif switch_index >= 14:
                ow_entry_list[switch_index].configure(placeholder_text=switch_index + 12)

            else:
                ow_entry_list[switch_index].configure(placeholder_text=switch_index + 22)

    def reset_ow():
        if ow_switch_list[0].get() == 1:
            for ow in range(16):
                ow_entry_list[ow].configure(placeholder_text="--")
                ow_switch_list[ow].deselect()

        else:
            switch_index_ow = 22
            for ow in range(16):
                if 3 < ow < 14:
                    ow_switch_list[ow].select()
                    ow_entry_list[ow].configure(placeholder_text="")

                else:
                    try:
                        ow_entry_list[ow].configure(placeholder_text=switch_index_ow)
                        ow_switch_list[ow].select()
                        switch_index_ow += 1
                    except AttributeError:
                        pass

    kd_reset_swtich = customtkinter.CTkSwitch(template_open_water, text="", command=reset_ow,
                                              fg_color=master_switch_off_color,
                                              progress_color=master_switch_on_color,
                                              button_color=master_switch_button_color,
                                              button_hover_color=master_switch_hover_color, )

    kd_reset_swtich.select()
    kd_reset_swtich.grid(row=0, column=2, )

    for n in range(16):
        ow_string = tkinter.Label(template_open_water, text=ow_string_list_template[n],
                                  font=font, background=frame_color)
        ow_string.grid(row=n + 1, column=0, padx=(20, 5), sticky="e")

    ow_switch_list = []
    for i in range(16):
        switch = customtkinter.CTkSwitch(template_open_water, text="",
                                         command=lambda p=i: switch_press_ow(p),
                                         fg_color=switch_off_color,
                                         progress_color=switch_on_color,
                                         button_color=switch_button_color,
                                         button_hover_color=switch_hover_color
                                         )
        switch.grid(row=i + 1, column=2, padx=10)
        switch.select()

        ow_switch_list.append(switch)

    # create row of entries
    ow_entry_list = []
    index_ow = 22
    for n in range(16):
        if 3 < n < 14:
            ow_entry = customtkinter.CTkEntry(template_open_water, placeholder_text="", width=40,
                                              placeholder_text_color=text_color,
                                              height=25, )
            ow_entry.grid(row=n + 1, column=1, pady=2)
        else:
            ow_entry = customtkinter.CTkEntry(template_open_water, placeholder_text=(index_ow), width=40,
                                              placeholder_text_color=text_color,
                                              height=25)
            ow_entry.grid(row=n + 1, column=1, pady=2)
            index_ow += 1
        ow_entry_list.append(ow_entry)

    # --- Set Course Options Labels and Entries

    def elearning():
        if kd_switch_list[0].get() == 1:
            for n in range(5):
                kd_entry_list[n].configure(placeholder_text="--")
                kd_switch_list[n].deselect()
                kd_switch_list[5].select()
                elearning_manual_button.configure(text="Manual & Classroom")
                kd_entry_list[5].configure(placeholder_text=20)

        else:
            for n in range(5):
                kd_entry_list[n].configure(placeholder_text=n + 15)
                kd_switch_list[n].select()
                kd_switch_list[5].deselect()
                kd_entry_list[5].configure(placeholder_text="--")
                elearning_manual_button.configure(text="Elearning")

    course_option_frame = customtkinter.CTkFrame(new_template_window, fg_color=frame_color)
    course_option_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    course_option_label_set_rule = tkinter.Label(course_option_frame, text="Course Option:", font=header,
                                                 background=frame_color)
    course_option_label_set_rule.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    rdp_table_switch_set_rule = customtkinter.CTkSwitch(course_option_frame, text="RDP Table",
                                                        fg_color=switch_off_color,
                                                        progress_color=switch_on_color,
                                                        button_color=switch_button_color,
                                                        button_hover_color=switch_hover_color
                                                        )
    rdp_table_switch_set_rule.grid(row=2, column=0, pady=4)

    erdpml_switch_set_rule = customtkinter.CTkSwitch(course_option_frame, text="eRDPml",
                                                     fg_color=switch_off_color,
                                                     progress_color=switch_on_color,
                                                     button_color=switch_button_color,
                                                     button_hover_color=switch_hover_color
                                                     )
    erdpml_switch_set_rule.grid(row=4, column=0, pady=4)
    computer_switch_set_rule = customtkinter.CTkSwitch(course_option_frame, text="Computer",
                                                       fg_color=switch_off_color,
                                                       progress_color=switch_on_color,
                                                       button_color=switch_button_color,
                                                       button_hover_color=switch_hover_color
                                                       )
    computer_switch_set_rule.grid(row=5, column=0, pady=4)

    elearning_manual_button = customtkinter.CTkButton(course_option_frame, text="Elearning",
                                                      fg_color=main_button_color, text_color=main_button_text_color,
                                                      hover_color=main_button_color_hover,
                                                      command=elearning
                                                      )
    elearning_manual_button.grid(row=6, column=0, pady=20)

    # --------------------------- RIGHT BUTTON FRAME TEMPLATE WINDOW

    template_right_frame = customtkinter.CTkFrame(new_template_window, fg_color=frame_color)
    template_right_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

    def delete_template(nuked_rule):
        with open("dive_template_data.json", "r") as data:
            temp = json.load(data)

        del temp[nuked_rule]
        with open("dive_template_data.json", "w") as data:
            json.dump(temp, data, indent=4)

        date_rule_box_set_rule.configure(values=temp)
        date_rule_box_set_rule.set("")
        date_rule_box.set("")
        date_rule_box.configure(values=temp)

    delete_label = tkinter.Label(template_right_frame, text="Delete Template", font=font, background=frame_color)
    delete_label.grid(row=0, column=0, pady=(20, 5))

    try:
        with open("dive_template_data.json", "r") as data:
            templates = json.load(data)
    except FileNotFoundError:
        templates = {}

    delete_values = []
    for temps in templates.keys():
        delete_values.append(temps)
    date_rule_box_set_rule = customtkinter.CTkOptionMenu(template_right_frame, values=delete_values,
                                                         fg_color=background_color,
                                                         text_color=text_color,
                                                         button_color=main_button_color,
                                                         button_hover_color=main_button_color_hover
                                                         )
    date_rule_box_set_rule.grid(row=1, column=0, padx=(15, 0), pady=(0, 20))

    delete_rule_button = customtkinter.CTkButton(template_right_frame, text="Delete Template:",
                                                 fg_color=main_button_color, text_color=main_button_text_color,
                                                 hover_color=main_button_color_hover,
                                                 command=lambda: delete_template(date_rule_box_set_rule.get())
                                                 )

    delete_rule_button.grid(column=0, row=2, pady=10, padx=(15, 0))

    def save_template():

        template_name = template_name_entry.get()
        ow_cal_entries = ow_entry_list[:4] + ow_entry_list[14:16]
        all_cal_entries = cw_entry_list + kd_entry_list + ow_cal_entries
        all_switches = cw_switch_list + kd_switch_list + ow_switch_list

        new_data = {
            template_name_entry.get(): {
                "calendar_entries": [],
                "switches": [],
                "knowledge_quiz": [],
                "dive_flex": [],
                "course_option": [],
            }
        }

        for cal in all_cal_entries:
            if cal.get() == "":
                # .get() returns an empty string if placeholder is left
                new_data[template_name]["calendar_entries"].append(cal.cget("placeholder_text"))
            elif cal.get() == "--":
                pass
            else:
                calendar_code = int(cal.get())
                new_data[template_name]["calendar_entries"].append(calendar_code)

        for switch in all_switches:
            new_data[template_name]["switches"].append(switch.get())
        for quiz in kd_exam_entry_list:
            new_data[template_name]["knowledge_quiz"].append(quiz.get())
        for dive_flex in ow_entry_list[4:14]:
            if dive_flex.get() == "":
                # .get() returns an empty string if placeholder is left
                new_data[template_name]["dive_flex"].append(dive_flex.cget("placeholder_text"))
            elif dive_flex.get() == "--":
                pass
            else:
                calendar_flex_code = (dive_flex.get())
                new_data[template_name]["dive_flex"].append(calendar_flex_code)

        new_data[template_name]["course_option"].append(rdp_table_switch_set_rule.get())
        new_data[template_name]["course_option"].append(erdpml_switch_set_rule.get())
        new_data[template_name]["course_option"].append(computer_switch_set_rule.get())

        try:
            with open("dive_template_data.json", "r") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            with open("dive_template_data.json", "w") as data_file:
                json.dump(new_data, data_file, indent=4)
        else:
            data.update(new_data)

            new_key_list = []
            for templates in data.keys():
                new_key_list.append(templates)

            date_rule_box.configure(values=new_key_list)

            with open("dive_template_data.json", "w") as data_file:
                json.dump(data, data_file, indent=4)

        new_template_window.destroy()

    set_rule_button = customtkinter.CTkButton(template_right_frame, text="Save Template",
                                              fg_color=main_button_color, text_color=main_button_text_color,
                                              hover_color=main_button_color_hover,
                                              command=save_template)

    set_rule_button.grid(column=0, row=3, padx=(15, 0), pady=(400, 0))


@speed_calc_decorator
def execute_template():
    """Function to set Dates and Dives in main Window to users specs.'"""

    with open("dive_template_data.json", "r") as datafile:  # --- Open Dictionary with Users Date/Dive Specs
        date_dict = json.load(datafile)

    template_name = date_rule_box.get()
    all_cal_entries_list = cw_cal_list + kd_cal_list + ow_cal_list
    all_switch_list = cw_switch_list + kd_switch_list + ow_switch_list

    index_cal = 0
    for i in date_dict[template_name]["calendar_entries"]:
        if i == "--":
            pass
            index_cal += 1
        else:
            # i = int(i)
            all_cal_entries_list[index_cal].set_date(all_cal_entries_list[i].get_date())
            index_cal += 1

    index_switch = 0
    for i in date_dict[template_name]["switches"]:  # CW
        if i == 0:
            all_switch_list[index_switch].deselect()
        index_switch += 1

    kr_index = 0
    for switches in kd_switch_list:
        if switches.get() == 0:
            kr_checkbox_list[kr_index].deselect()
            kd_video_checkbox_list[kr_index].deselect()
        kr_index += 1

    index_kw = 0
    for i in date_dict[template_name]["knowledge_quiz"]:
        kd_exam_entry_list[index_kw].configure(placeholder_text=i)
        index_kw += 1

    index_dive_flex = 0
    for i in date_dict[template_name]["dive_flex"]:
        if i == "--":
            index_dive_flex += 1
        else:
            ow_flex_dive_list[index_dive_flex].configure(placeholder_text=i)
            index_dive_flex += 1

    if date_dict[template_name]["course_option"][0] == 1:
        rdp_check.select()

    if date_dict[template_name]["course_option"][1] == 1:
        erdpml_check.select()

    if date_dict[template_name]["course_option"][2] == 1:
        computer_check.select()


@speed_calc_decorator
def set_instructor():
    """Password Verification UI window for users to input their Instructor Password."""
    with open("instructor_data.json", "r") as data_file:
        instructor_list = json.load(data_file)
    set_inst = list_box.get()
    inst = list_box.get()
    pass_window = Toplevel(window)
    pass_window.geometry("500x250")
    pass_window.title("Instructor Password")
    pass_window.config(pady=50, padx=50, background=background_color)
    pass_window.grid_columnconfigure(0, weight=1)
    pass_frame = customtkinter.CTkFrame(pass_window, fg_color=frame_color)
    pass_frame.grid(row=1, column=0, sticky="nsew")
    pass_frame.grid_columnconfigure(0, weight=1)
    pass_label = tkinter.Label(pass_window, text="Verify Instructor Password", font=header, background=background_color)
    pass_label.grid(column=0, row=0, sticky="w")
    pass_entry = customtkinter.CTkEntry(pass_frame, show="*")
    pass_entry.grid(column=0, row=0, pady=10, padx=10, sticky="ew")
    salt = (instructor_list[inst]["Password"]["Salt"])
    hashed_pass = (instructor_list[inst]["Password"]["Hash"])

    def show():
        if password_switch.get() == 0:
            pass_entry.configure(show="")
        else:
            pass_entry.configure(show="*")

    password_switch = customtkinter.CTkSwitch(pass_frame, text="Show password", command=show,
                                              fg_color=switch_off_color,
                                              progress_color=switch_on_color,
                                              button_hover_color=switch_hover_color,
                                              button_color=switch_button_color)
    password_switch.select()
    password_switch.grid(row=0, column=1, sticky="ew", padx=(5, 20))

    @speed_calc_decorator
    def password_verify():
        """Verify if password is correct.  If correct updates 'fields' dictionary if checkbox is selected."""
        hash_object = hashlib.sha256(salt.encode() + pass_entry.get().encode())
        hashed_password_entry = hash_object.hexdigest()
        if hashed_password_entry == hashed_pass:
            pass_window.destroy()
            if len(fields["PADI Instructor"]) == 0:  # --- check if first Instructor Info field is emtpy
                fields["PADI Instructor"] = instructor_list[set_inst]["PADI Instructor"]
                fields["PADI No"] = instructor_list[set_inst]["PADI Number"]
                fields["Dive CenterResort No"] = instructor_list[set_inst]["Dive Center"]
                fields["Date"] = today.day
                fields["undefined_9"] = today.month
                fields["undefined_10"] = today.year
                fields["undefined_12"] = instructor_list[set_inst]["Phone"]
                fields["Email_2"] = instructor_list[set_inst]["Email"]

            if fields["PADI Instructor"] == instructor_list[set_inst]["PADI Instructor"]:
                pass

            else:  # --- If first Instructor field has info, update the second Instructor field
                fields["PADI Instructor_2"] = instructor_list[set_inst]["PADI Instructor"]
                fields["PADI No_2"] = instructor_list[set_inst]["PADI Number"]
                fields["Dive CenterResort No_2"] = instructor_list[set_inst]["Dive Center"]
                fields["Date_2"] = today.day
                fields["undefined_15"] = today.month
                fields["undefined_16"] = today.year
                fields["undefined_18"] = instructor_list[set_inst]["Phone"]
                fields["Email_3"] = instructor_list[set_inst]["Email"]

            # --- Check if corresponding checkbox is True. If so update Instructor Initials and PADI Number
            if cw_switch_list[0].get() == 1:
                cw_set_instructor_list[0].config(text=inst, fg=set_text_color)
                fields["Initials 1"] = instructor_list[set_inst]["Initials"]
                fields["undefined_29"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[1].get() == 1:
                cw_set_instructor_list[1].config(text=inst, fg=set_text_color)
                fields["Initials 2"] = instructor_list[set_inst]["Initials"]
                fields["undefined_35"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[2].get() == 1:
                cw_set_instructor_list[2].config(text=inst, fg=set_text_color)
                fields["Initials 3"] = instructor_list[set_inst]["Initials"]
                fields["undefined_41"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[3].get() == 1:
                cw_set_instructor_list[3].config(text=inst, fg=set_text_color)
                fields["Initials 4"] = instructor_list[set_inst]["Initials"]
                fields["undefined_47"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[4].get() == 1:
                cw_set_instructor_list[4].config(text=inst, fg=set_text_color)
                fields["DSD with all CW Dive 1 skills  Open Water Diver CW Dive 1"] = instructor_list[set_inst]["Initials"]
                fields["undefined_55"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[5].get() == 1:
                cw_set_instructor_list[5].config(text=inst, fg=set_text_color)
                fields["200 metreyard Swim OR 300 metreyard MaskSnorkelFin Swim"] = instructor_list[set_inst]["Initials"]
                fields["undefined_68"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[6].get() == 1:
                cw_set_instructor_list[6].config(text=inst, fg=set_text_color)
                fields["undefined_73"] = instructor_list[set_inst]["Initials"]
                fields["undefined_74"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[7].get() == 1:
                cw_set_instructor_list[7].config(text=inst, fg=set_text_color)
                fields["undefined_77"] = instructor_list[set_inst]["Initials"]
                fields["undefined_78"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[8].get() == 1:
                cw_set_instructor_list[8].config(text=inst, fg=set_text_color)
                fields["undefined_93"] = instructor_list[set_inst]["Initials"]
                fields["undefined_94"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[9].get() == 1:
                cw_set_instructor_list[9].config(text=inst, fg=set_text_color)
                fields["undefined_98"] = instructor_list[set_inst]["Initials"]
                fields["undefined_99"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[10].get() == 1:
                cw_set_instructor_list[10].config(text=inst, fg=set_text_color)
                fields["undefined_104"] = instructor_list[set_inst]["Initials"]
                fields["undefined_101"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[11].get() == 1:
                cw_set_instructor_list[11].config(text=inst, fg=set_text_color)
                fields["undefined_105"] = instructor_list[set_inst]["Initials"]
                fields["undefined_106"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[12].get() == 1:
                cw_set_instructor_list[12].config(text=inst, fg=set_text_color)
                fields["undefined_119"] = instructor_list[set_inst]["Initials"]
                fields["undefined_120"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[13].get() == 1:
                cw_set_instructor_list[13].config(text=inst, fg=set_text_color)
                fields["undefined_124"] = instructor_list[set_inst]["Initials"]
                fields["undefined_125"] = instructor_list[set_inst]["PADI Number"]
            if cw_switch_list[14].get() == 1:
                cw_set_instructor_list[14].config(text=inst, fg=set_text_color)
                fields["PADI"] = instructor_list[set_inst]["PADI Number"]
            if kd_switch_list[0].get() == 1:
                kd_set_instructor_list[0].config(text=inst, fg=set_text_color)
                fields["undefined_33"] = instructor_list[set_inst]["Initials"]
                fields["undefined_34"] = instructor_list[set_inst]["PADI Number"]
            if kd_switch_list[1].get() == 1:
                kd_set_instructor_list[1].config(text=inst, fg=set_text_color)
                fields["undefined_39"] = instructor_list[set_inst]["Initials"]
                fields["undefined_40"] = instructor_list[set_inst]["PADI Number"]
            if kd_switch_list[2].get() == 1:
                kd_set_instructor_list[2].config(text=inst, fg=set_text_color)
                fields["undefined_45"] = instructor_list[set_inst]["Initials"]
                fields["undefined_46"] = instructor_list[set_inst]["PADI Number"]
            if kd_switch_list[3].get() == 1:
                kd_set_instructor_list[3].config(text=inst, fg=set_text_color)
                fields["undefined_51"] = instructor_list[set_inst]["Initials"]
                fields["undefined_52"] = instructor_list[set_inst]["PADI Number"]
            if kd_switch_list[4].get() == 1:
                kd_set_instructor_list[4].config(text=inst, fg=set_text_color)
                fields["undefined_59"] = instructor_list[set_inst]["Initials"]
                fields["undefined_60"] = instructor_list[set_inst]["PADI Number"]
            if kd_switch_list[5].get() == 1:
                kd_set_instructor_list[5].config(text=inst, fg=set_text_color)
                fields["undefined_64"] = instructor_list[set_inst]["Initials"]
                fields["undefined_65"] = instructor_list[set_inst]["PADI Number"]
            if kd_switch_list[6].get() == 1:
                kd_set_instructor_list[6].config(text=inst, fg=set_text_color)
                fields["undefined_69"] = instructor_list[set_inst]["PADI Number"]

            if ow_switch_list[0].get() == 1:
                ow_set_instructor_list[0].config(text=inst, fg=set_text_color)
                fields["Initials 1_2"] = instructor_list[set_inst]["Initials"]
                fields["undefined_86"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[1].get() == 1:
                ow_set_instructor_list[1].config(text=inst, fg=set_text_color)
                fields["Initials 2_2"] = instructor_list[set_inst]["Initials"]
                fields["undefined_81"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[2].get() == 1:
                ow_set_instructor_list[2].config(text=inst, fg=set_text_color)
                fields["Initials 1_3"] = instructor_list[set_inst]["Initials"]
                fields["undefined_89"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[3].get() == 1:
                ow_set_instructor_list[3].config(text=inst, fg=set_text_color)
                fields["Initials 2_3"] = instructor_list[set_inst]["Initials"]
                fields["undefined_90"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[4].get() == 1:
                ow_set_instructor_list[4].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 1"] = instructor_list[set_inst]["Initials"]
                fields["undefined_109"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[5].get() == 1:
                ow_set_instructor_list[5].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 2"] = instructor_list[set_inst]["Initials"]
                fields["undefined_110"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[6].get() == 1:
                ow_set_instructor_list[6].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 3"] = instructor_list[set_inst]["Initials"]
                fields["undefined_111"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[7].get() == 1:
                ow_set_instructor_list[7].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 4"] = instructor_list[set_inst]["Initials"]
                fields["undefined_112"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[8].get() == 1:
                ow_set_instructor_list[8].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 5"] = instructor_list[set_inst]["Initials"]
                fields["undefined_113"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[9].get() == 1:
                ow_set_instructor_list[9].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 6"] = instructor_list[set_inst]["Initials"]
                fields["undefined_114"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[10].get() == 1:
                ow_set_instructor_list[10].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 7"] = instructor_list[set_inst]["Initials"]
                fields["undefined_115"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[11].get() == 1:
                ow_set_instructor_list[11].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 8"] = instructor_list[set_inst]["Initials"]
                fields["undefined_116"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[12].get() == 1:
                ow_set_instructor_list[12].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 9"] = instructor_list[set_inst]["Initials"]
                fields["undefined_117"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[13].get() == 1:
                ow_set_instructor_list[13].config(text=inst, fg=set_text_color)
                fields["Instructor Initials 10"] = instructor_list[set_inst]["Initials"]
                fields["undefined_121"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[14].get() == 1:
                ow_set_instructor_list[14].config(text=inst, fg=set_text_color)
                fields["undefined_126"] = instructor_list[set_inst]["PADI Number"]
            if ow_switch_list[15].get() == 1:
                ow_set_instructor_list[15].config(text=inst, fg=set_text_color)
                fields["undefined_137"] = instructor_list[set_inst]["PADI Number"]

        else:  # --- User Enters Wrong Password
            pass_window.destroy()
            messagebox.showinfo("invalid password", "Wrong Password")

    # --- Password Submit Button
    pass_button = customtkinter.CTkButton(pass_frame, text="Submit", command=password_verify,
                                          fg_color=main_button_color, text_color=main_button_text_color,
                                          hover_color=main_button_color_hover
                                          )

    pass_button.grid(column=1, row=1, pady=10, padx=10)


@speed_calc_decorator
def set_date():
    """Add dates to 'field' dictionary and change 'Set Dive' Label to Calendar DateEntry"""

    # --- Confined Water Dives
    if cw_switch_list[0].get() == 1:
        con_water_one_date = cw_cal_list[0].get_date()
        cw_set_date_list[0].config(text=con_water_one_date, fg=set_text_color)
        fields["CW 1"] = con_water_one_date.day
        fields["undefined_27"] = con_water_one_date.month
        fields["undefined_28"] = con_water_one_date.year
    if cw_switch_list[1].get() == 1:
        con_water_two_date = cw_cal_list[1].get_date()
        cw_set_date_list[1].config(text=con_water_two_date, fg=set_text_color)
        fields["CW 2"] = con_water_two_date.day
        fields["undefined_21"] = con_water_two_date.month
        fields["undefined_22"] = con_water_two_date.year
    if cw_switch_list[2].get() == 1:
        con_water_three_date = cw_cal_list[2].get_date()
        cw_set_date_list[2].config(text=con_water_three_date, fg=set_text_color)
        fields["CW 3"] = con_water_three_date.day
        fields["undefined_23"] = con_water_three_date.month
        fields["undefined_24"] = con_water_three_date.year
    if cw_switch_list[3].get() == 1:
        con_water_four_date = cw_cal_list[3].get_date()
        cw_set_date_list[3].config(text=con_water_four_date, fg=set_text_color)
        fields["CW 4"] = con_water_four_date.day
        fields["undefined_25"] = con_water_four_date.month
        fields["undefined_26"] = con_water_four_date.year
    if cw_switch_list[4].get() == 1:
        con_water_five_date = cw_cal_list[4].get_date()
        cw_set_date_list[4].config(text=con_water_five_date, fg=set_text_color)
        fields["CW 5"] = con_water_five_date.day
        fields["undefined_53"] = con_water_five_date.month
        fields["undefined_54"] = con_water_five_date.year
    if cw_switch_list[5].get() == 1:  # Swim
        swim_date = cw_cal_list[5].get_date()
        cw_set_date_list[5].config(text=swim_date, fg=set_text_color)
        fields["10 Minute Survival Float"] = swim_date.day
        fields["undefined_66"] = swim_date.month
        fields["undefined_67"] = swim_date.year
    if cw_switch_list[6].get() == 1:  # Float
        float_date = cw_cal_list[6].get_date()
        cw_set_date_list[6].config(text=float_date, fg=set_text_color)
        fields["undefined_75"] = float_date.day
        fields["undefined_76"] = float_date.month
        fields["undefined_72"] = float_date.year
    if cw_switch_list[7].get() == 1:
        equip_date = cw_cal_list[7].get_date()
        cw_set_date_list[7].config(text=equip_date, fg=set_text_color)
        fields["Equipment Preparation and Care"] = equip_date.day
        fields["undefined_91"] = equip_date.month
        fields["undefined_92"] = equip_date.year
    if cw_switch_list[8].get() == 1:
        disconnect_date = cw_cal_list[8].get_date()
        cw_set_date_list[8].config(text=disconnect_date, fg=set_text_color)
        fields["Disconnect Low Pressure Inflator Hose"] = disconnect_date.day
        fields["undefined_95"] = disconnect_date.month
        fields["undefined_96"] = disconnect_date.year
    if cw_switch_list[9].get() == 1:
        loose_date = cw_cal_list[9].get_date()
        cw_set_date_list[9].config(text=loose_date, fg=set_text_color)
        fields["Loose Cylinder Band"] = loose_date.day
        fields["undefined_100"] = loose_date.month
        fields["undefined_97"] = loose_date.year
    if cw_switch_list[10].get() == 1:
        weight_date = cw_cal_list[10].get_date()
        cw_set_date_list[10].config(text=weight_date, fg=set_text_color)
        fields["Weight System Removal and Replacement surface"] = weight_date.day
        fields["undefined_102"] = weight_date.month
        fields["undefined_103"] = weight_date.year
    if cw_switch_list[11].get() == 1:
        weight_drop_date = cw_cal_list[11].get_date()
        cw_set_date_list[11].config(text=weight_drop_date, fg=set_text_color)
        fields["Emergency Weight Drop or in OW"] = weight_drop_date.day
        fields["undefined_107"] = weight_drop_date.month
        fields["undefined_108"] = weight_drop_date.year
    if cw_switch_list[12].get() == 1:
        skin_diving_date = cw_cal_list[12].get_date()
        cw_set_date_list[12].config(text=skin_diving_date, fg=set_text_color)
        fields["Skin Diving Skills"] = skin_diving_date.day
        fields["undefined_122"] = skin_diving_date.month
        fields["undefined_118"] = skin_diving_date.year
    if cw_switch_list[13].get() == 1:
        drysuit_orientation_date = cw_cal_list[13].get_date()
        cw_set_date_list[13].config(text=drysuit_orientation_date, fg=set_text_color)
        fields[
            "Note If all Confined Water Dives Confined Water Dive Flexible Skills and Wa"] = drysuit_orientation_date.day
        fields["undefined_129"] = drysuit_orientation_date.month
        fields["undefined_123"] = drysuit_orientation_date.year
    if cw_switch_list[14].get() == 1:
        confined_water_signoff_date = cw_cal_list[14].get_date()
        cw_set_date_list[14].config(text=confined_water_signoff_date, fg=set_text_color)
        fields["Date_6"] = confined_water_signoff_date.day
        fields["undefined_132"] = confined_water_signoff_date.month
        fields["undefined_133"] = confined_water_signoff_date.year
    # --- Knowledge Development

    if kd_switch_list[0].get() == 1:
        kr1_date = kd_cal_list[0].get_date()
        kd_set_date_list[0].config(text=kr1_date, fg=set_text_color)
        fields["Section 1"] = kr1_date.day
        fields["undefined_30"] = kr1_date.month
        fields["undefined_31"] = kr1_date.year
    if kd_switch_list[1].get() == 1:
        kr2_date = kd_cal_list[1].get_date()
        kd_set_date_list[1].config(text=kr2_date, fg=set_text_color)
        fields["Section 2"] = kr2_date.day
        fields["undefined_36"] = kr2_date.month
        fields["undefined_37"] = kr2_date.year
    if kd_switch_list[2].get() == 1:
        kr3_date = kd_cal_list[2].get_date()
        kd_set_date_list[2].config(text=kr3_date, fg=set_text_color)
        fields["Section 3"] = kr3_date.day
        fields["undefined_42"] = kr3_date.month
        fields["undefined_43"] = kr3_date.year
    if kd_switch_list[3].get() == 1:
        kr4_date = kd_cal_list[3].get_date()
        kd_set_date_list[3].config(text=kr4_date, fg=set_text_color)
        fields["Section 4"] = kr4_date.day
        fields["undefined_48"] = kr4_date.month
        fields["undefined_49"] = kr4_date.year
    if kd_switch_list[4].get() == 1:
        kr5_date = kd_cal_list[4].get_date()
        kd_set_date_list[4].config(text=kr5_date, fg=set_text_color)
        fields["Section 5"] = kr5_date.day
        fields["undefined_56"] = kr5_date.month
        fields["undefined_57"] = kr5_date.year
    if kd_switch_list[5].get() == 1:
        or_elearning_date = kd_cal_list[5].get_date()
        kd_set_date_list[5].config(text=or_elearning_date, fg=set_text_color)
        fields["Quick Review"] = or_elearning_date.day
        fields["undefined_61"] = or_elearning_date.month
        fields["undefined_62"] = or_elearning_date.year
    if kd_switch_list[6].get() == 1:
        all_knowledge_date = kd_cal_list[5].get_date()
        kd_set_date_list[6].config(text=all_knowledge_date, fg=set_text_color)
        fields["Date_3"] = all_knowledge_date.day
        fields["undefined_70"] = all_knowledge_date.month
        fields["undefined_71"] = all_knowledge_date.year

    # --- Open Water Dives
    if ow_switch_list[0].get() == 1:
        ow1_date = ow_cal_list[0].get_date()
        ow_set_date_list[0].config(text=ow1_date, fg=set_text_color)
        fields["Dive 1"] = ow1_date.day
        fields["undefined_84"] = ow1_date.month
        fields["undefined_85"] = ow1_date.year
    if ow_switch_list[1].get() == 1:
        ow2_date = ow_cal_list[1].get_date()
        ow_set_date_list[1].config(text=ow2_date, fg=set_text_color)
        fields["Dive 2"] = ow2_date.day
        fields["undefined_79"] = ow2_date.month
        fields["undefined_80"] = ow2_date.year
    if ow_switch_list[2].get() == 1:
        ow3_date = ow_cal_list[2].get_date()
        ow_set_date_list[2].config(text=ow3_date, fg=set_text_color)
        fields["Dive 3"] = ow3_date.day
        fields["undefined_87"] = ow3_date.month
        fields["undefined_88"] = ow3_date.year
    if ow_switch_list[3].get() == 1:
        ow4_date = ow_cal_list[3].get_date()
        ow_set_date_list[3].config(text=ow4_date, fg=set_text_color)
        fields["Dive 4"] = ow4_date.day
        fields["undefined_82"] = ow4_date.month
        fields["undefined_83"] = ow4_date.year

    # --- Open Water Flexible Skills
    if ow_switch_list[4].get() == 1:
        ow_set_date_list[4].config(text=ow_flex_dive_list[0].get(), fg=set_text_color)
        fields["Dive_9"] = ow_flex_dive_list[0].get()
    if ow_switch_list[5].get() == 1:
        ow_set_date_list[5].config(text=ow_flex_dive_list[1].get(), fg=set_text_color)
        fields["Dive"] = ow_flex_dive_list[1].get()
    if ow_switch_list[6].get() == 1:
        ow_set_date_list[6].config(text=ow_flex_dive_list[2].get(), fg=set_text_color)
        fields["Dive_2"] = ow_flex_dive_list[2].get()
    if ow_switch_list[7].get() == 1:
        ow_set_date_list[7].config(text=ow_flex_dive_list[3].get(), fg=set_text_color)
        fields["Dive_3"] = ow_flex_dive_list[3].get()
    if ow_switch_list[8].get() == 1:
        ow_set_date_list[8].config(text=ow_flex_dive_list[4].get(), fg=set_text_color)
        fields["Dive_4"] = ow_flex_dive_list[4].get()
    if ow_switch_list[9].get() == 1:
        ow_set_date_list[9].config(text=ow_flex_dive_list[5].get(), fg=set_text_color)
        fields["Dive_5"] = ow_flex_dive_list[5].get()
    if ow_switch_list[10].get() == 1:
        ow_set_date_list[10].config(text=ow_flex_dive_list[6].get(), fg=set_text_color)
        fields["Dive_6"] = ow_flex_dive_list[6].get()
    if ow_switch_list[11].get() == 1:
        ow_set_date_list[11].config(text=ow_flex_dive_list[7].get(), fg=set_text_color)
        fields["Dive_7"] = ow_flex_dive_list[7].get()
    if ow_switch_list[12].get() == 1:
        ow_set_date_list[12].config(text=ow_flex_dive_list[8].get(), fg=set_text_color)
        fields["Dive_8"] = ow_flex_dive_list[8].get()
    if ow_switch_list[13].get() == 1:
        ow_set_date_list[13].config(text=ow_flex_dive_list[9].get(), fg=set_text_color)
        fields["Dive_10"] = ow_flex_dive_list[9].get()
    if ow_switch_list[14].get() == 1:
        all_ow_flex_dives_date = ow_cal_list[4].get_date()
        ow_set_date_list[14].config(text=all_ow_flex_dives_date, fg=set_text_color)
        fields["Date_4"] = all_ow_flex_dives_date.day
        fields["undefined_127"] = all_ow_flex_dives_date.month
        fields["undefined_128"] = all_ow_flex_dives_date.year
    if ow_switch_list[15].get() == 1:
        all_cert_requirements_date = ow_cal_list[5].get_date()
        ow_set_date_list[15].config(text=all_cert_requirements_date, fg=set_text_color)
        fields["Date_8"] = all_cert_requirements_date.day
        fields["undefined_138"] = all_cert_requirements_date.month
        fields["undefined_139"] = all_cert_requirements_date.year


@speed_calc_decorator
def generate_pdf():
    """Functions to write 'fields' dictionary to fill 'Record_and_Referral_form' pdf."""
    input_path = "Record_and_Referral_Form.pdf"
    student_file_name = fields["Student Name"]

    # --- if checkbox are True update 'fields' dictionary
    if rdp_check.get() == 1:
        fields["Check Box24"] = "Yes"
    if erdpml_check.get() == 1:
        fields["Check Box23"] = "Yes"
    if computer_check.get() == 1:
        fields["Check Box22"] = "Yes"
    if kr_checkbox_list[0].get() == 1:
        fields["Check Box25"] = "Yes"
    if kr_checkbox_list[1].get() == 1:
        fields["Check Box27"] = "Yes"
    if kr_checkbox_list[2].get() == 1:
        fields["Check Box29"] = "Yes"
    if kr_checkbox_list[3].get() == 1:
        fields["Check Box31"] = "Yes"
    if kr_checkbox_list[4].get() == 1:
        fields["Check Box33"] = "Yes"
    if kr_checkbox_list[5].get() == 1:
        fields["Check Box35"] = "Yes"
    if kd_video_checkbox_list[0].get() == 1:
        fields["Check Box26"] = "Yes"
    if kd_video_checkbox_list[0].get() == 1:
        fields["Check Box28"] = "Yes"
    if kd_video_checkbox_list[0].get() == 1:
        fields["Check Box30"] = "Yes"
    if kd_video_checkbox_list[0].get() == 1:
        fields["Check Box32"] = "Yes"
    if kd_video_checkbox_list[0].get() == 1:
        fields["Check Box34"] = "Yes"
    if kd_video_checkbox_list[0].get() == 1:
        fields["Check Box36"] = "Yes"

    # --- Get string inputs from Knowledge Development Entries and update 'fields' dictionary
    fields["undefined_32"] = kd_exam_entry_list[0].get()
    fields["undefined_38"] = kd_exam_entry_list[1].get()
    fields["undefined_44"] = kd_exam_entry_list[2].get()
    fields["undefined_50"] = kd_exam_entry_list[3].get()
    fields["undefined_58"] = kd_exam_entry_list[4].get()
    fields["undefined_63"] = kd_exam_entry_list[5].get()

    # --- Save pdf file name

    save_path = config["save path"]["student_record_path"]
    output_path = f"{save_path}/{student_file_name}_Student_Record_Form_{today.day}_{today.month}_{today.year}.pdf"
    # --- Write pdf
    fillpdfs.write_fillable_pdf(input_path, output_path, fields)


@speed_calc_decorator
def new_student():
    """Allow users to add Student Diver Information"""
    student_window = Toplevel(window)
    student_window.geometry(f"{600}x{600}")
    student_window.title("Instructor Paperwork Assistant")
    student_window.config(pady=20, padx=20, background=background_color)
    student_window.grid_rowconfigure(1, weight=1)
    student_window.grid_columnconfigure(0, weight=1)
    student_frame = customtkinter.CTkFrame(student_window, fg_color=frame_color)
    student_frame.grid(row=1, column=0, columnspan=3, rowspan=10, padx=40, pady=(0, 40), sticky="nsew")
    student_frame.grid_columnconfigure(2, weight=1)
    student_frame.grid_columnconfigure(0, weight=1)
    student_frame.grid_columnconfigure(1, weight=1)
    student_info_label = tkinter.Label(student_window, text="Add Student Information", font=header,
                                       background=background_color)
    student_info_label.grid(row=0, column=0, sticky="sw", padx=40)

    student_f_name_label = tkinter.Label(student_frame, text="First Name:", background=frame_color, font=font)
    student_f_name_label.grid(column=0, row=0, sticky="e", pady=(30, 0), padx=2)
    student_f_name_entry = customtkinter.CTkEntry(student_frame, width=30, height=25)
    student_f_name_entry.grid(column=1, row=0, columnspan=3, padx=(0, 30), pady=(30, 2), sticky="ew")

    student_l_name_label = tkinter.Label(student_frame, text="Last Name:", background=frame_color, font=font)
    student_l_name_label.grid(column=0, row=1, sticky="e", pady=2)
    student_l_name_entry = customtkinter.CTkEntry(student_frame, width=30, height=25)
    student_l_name_entry.grid(column=1, row=1, columnspan=3, padx=(0, 30), pady=(2), sticky="ew")

    dob_label = tkinter.Label(student_frame, text="DOB: (DD/MM/YYYY)", background=frame_color, font=font)
    dob_label.grid(column=0, row=2, sticky="e", padx=(30, 0))
    dob_entry = customtkinter.CTkEntry(student_frame, width=15, height=25)
    dob_entry.grid(column=1, row=2, sticky="ew", pady=2)

    student_email_label = tkinter.Label(student_frame, text="Email:", background=frame_color, font=font)
    student_email_label.grid(row=3, column=0, sticky="e")
    student_email_entry = customtkinter.CTkEntry(student_frame, width=30, height=25)
    student_email_entry.grid(row=3, column=1, columnspan=3, sticky="ew", padx=(0, 30), pady=2)
    student_phone_label = tkinter.Label(student_frame, text="Phone:", background=frame_color, font=font)
    student_phone_label.grid(row=4, column=0, sticky="e", pady=5)
    student_phone_entry = customtkinter.CTkEntry(student_frame, width=30, height=25)
    student_phone_entry.grid(row=4, column=1, columnspan=3, padx=(0, 30), sticky="ew")

    sex_label = tkinter.Label(student_frame, text="Sex", padx=1, background=frame_color, font=font)
    sex_label.grid(row=5, column=0, sticky="e")
    sex_check_var = tkinter.IntVar()
    sex_radio_male = tkinter.Radiobutton(student_frame, text="Male", variable=sex_check_var, value=1,
                                         background=frame_color, font=font)
    sex_radio_male.grid(row=5, column=1, sticky="w", padx=(10, 0))
    sex_radio_female = tkinter.Radiobutton(student_frame, text="Female", variable=sex_check_var, value=2,
                                           background=frame_color, font=font)
    sex_radio_female.grid(row=6, column=1, sticky="w", padx=(10, 0))
    mailing_label = tkinter.Label(student_frame, text="Mailing Address", background=frame_color, font=font)
    mailing_label.grid(row=7, column=0, sticky="e", pady=(20, 5))
    street_label = tkinter.Label(student_frame, text="Street:", background=frame_color, font=font)
    street_label.grid(row=8, column=0, sticky="e", pady=2)
    street_entry = customtkinter.CTkEntry(student_frame, width=30, height=25)
    street_entry.grid(row=8, column=1, columnspan=3, padx=(0, 30), sticky="ew", pady=2)
    city_label = tkinter.Label(student_frame, text="City:", background=frame_color, font=font)
    city_label.grid(row=9, column=0, sticky="e")
    city_entry = customtkinter.CTkEntry(student_frame, height=25)
    city_entry.grid(row=9, column=1, sticky="ew", pady=2)
    province_label = tkinter.Label(student_frame, text="Province:", background=frame_color, font=font)
    province_label.grid(row=10, column=0, sticky="e")
    province_entry = customtkinter.CTkEntry(student_frame, height=25)
    province_entry.grid(row=10, column=1, sticky="ew", pady=2)
    country_label = tkinter.Label(student_frame, text="Country:", background=frame_color, font=font)
    country_label.grid(row=11, column=0, sticky="e")
    country_entry = customtkinter.CTkEntry(student_frame, height=25)
    country_entry.grid(row=11, column=1, sticky="ew", pady=2)
    postal_label = tkinter.Label(student_frame, text="Postal:", background=frame_color, font=font)
    postal_label.grid(row=12, column=0, sticky="e")
    postal_entry = customtkinter.CTkEntry(student_frame, height=25)
    postal_entry.grid(row=12, column=1, sticky="ew", pady=2)

    def update_student():
        """Function to update student dictionary with user inputs"""
        if sex_check_var.get() == 1:
            sex = "male"
        elif sex_check_var.get() == 2:
            sex = "female"
        else:
            sex = ""

        global student_dict_global
        new_student_data = {
            f"{student_f_name_entry.get()} {student_l_name_entry.get()}": {
                "first_name": student_f_name_entry.get(),
                "last_name": student_l_name_entry.get(),
                "date_of_birth": dob_entry.get(),
                "sex": sex,
                "phone": student_phone_entry.get(),
                "email": student_email_entry.get(),
                "street_address": street_entry.get(),
                "city": city_entry.get(),
                "province": province_entry.get(),
                "country": country_entry.get(),
                "postal": postal_entry.get(),
            }
        }

        list_box_student.insert("end", f"{student_f_name_entry.get()} {student_l_name_entry.get()}")

        student_dict_global.update(new_student_data)
        student_window.destroy()

    # --- Add Student Button
    student_button = customtkinter.CTkButton(student_frame, text="Add Student", command=update_student,
                                             fg_color=main_button_color, text_color=main_button_text_color,
                                             hover_color=main_button_color_hover
                                             )
    student_button.grid(column=2, row=13, columnspan=3, sticky="e", pady=30, padx=30)


def update_instructor_menu():
    """update instructor option menu"""
    with open("instructor_data.json", "r") as inst:
        instructor_info = json.load(inst)

    instructor_list_menu = []

    for instructor in instructor_info.keys():
        instructor_list_menu.append(instructor)

    list_box.configure(values=instructor_list_menu)


@speed_calc_decorator
def new_instructor():
    """Allows users to add a New Instructor"""
    instructor_window = Toplevel(window)
    instructor_window.geometry("700x500")
    instructor_window.title("Add Instructor Information")
    instructor_window.config(pady=50, padx=50, background=background_color)
    instructor_window.grid_columnconfigure(0, weight=1)

    add_instructor_label = tkinter.Label(instructor_window, text="Add Instructor", font=header,
                                         background=background_color)
    add_instructor_label.grid(row=0, column=0, sticky="w", padx=10)

    instructor_frame = customtkinter.CTkFrame(instructor_window, fg_color=frame_color)
    instructor_frame.grid(row=1, column=0, ipadx=20)
    instructor_frame.grid_columnconfigure(0, weight=1)

    instructor_name_label = tkinter.Label(instructor_frame, text="PADI Instructor:", font=font, background=frame_color)
    instructor_name_label.grid(column=0, row=0, sticky="e", pady=(20, 2))
    instructor_name_entry = customtkinter.CTkEntry(instructor_frame, height=25)
    instructor_name_entry.grid(column=1, row=0, columnspan=2, sticky="ew", pady=(20, 2))
    initials_label = tkinter.Label(instructor_frame, text="Initials", font=font, background=frame_color)
    initials_label.grid(column=0, row=1, sticky="e", pady=2)
    initials_entry = customtkinter.CTkEntry(instructor_frame, height=25)
    initials_entry.grid(column=1, row=1, sticky="ew", pady=2)
    padi_number_label = tkinter.Label(instructor_frame, text="PADI Number:", font=font, background=frame_color)
    padi_number_label.grid(row=3, column=0, sticky="e", pady=2)
    padi_number_entry = customtkinter.CTkEntry(instructor_frame, height=25)
    padi_number_entry.grid(row=3, column=1, sticky="ew", pady=2)
    store_number_label = tkinter.Label(instructor_frame, text="PADI Store Number s-:", font=font,
                                       background=frame_color)
    store_number_label.grid(row=4, column=0, sticky="e", pady=2)
    store_number_entry = customtkinter.CTkEntry(instructor_frame, height=25)
    store_number_entry.grid(row=4, column=1, sticky="ew", pady=2)
    phone_label = tkinter.Label(instructor_frame, text="Phone:", font=font, background=frame_color)
    phone_label.grid(row=5, column=0, sticky="e", pady=2)
    phone_entry = customtkinter.CTkEntry(instructor_frame, height=25)
    phone_entry.grid(row=5, column=1, columnspan=2, sticky="ew", pady=2)
    instructor_email_label = tkinter.Label(instructor_frame, text="Email:", font=font, background=frame_color)
    instructor_email_label.grid(row=6, column=0, sticky="e", pady=2)
    instructor_email_entry = customtkinter.CTkEntry(instructor_frame, height=25)
    instructor_email_entry.grid(row=6, column=1, columnspan=2, sticky="ew", pady=2)
    instructor_password_label = tkinter.Label(instructor_frame, text="Password:", font=font, background=frame_color)
    instructor_password_label.grid(row=7, column=0, sticky="e", pady=2)
    instructor_password_entry = customtkinter.CTkEntry(instructor_frame, show="*", height=25)
    instructor_password_entry.grid(row=7, column=1, columnspan=2, sticky="ew", pady=2)

    def update_instructor():
        """Save Instructor Information to 'instructor.json' for future use"""
        # --- Instructor Dictionary
        new_data = {
            instructor_name_entry.get(): {
                "PADI Instructor": instructor_name_entry.get(),
                "Initials": initials_entry.get(),
                "PADI Number": padi_number_entry.get(),
                "Dive Center": store_number_entry.get(),
                "Phone": phone_entry.get(),
                "Email": instructor_email_entry.get(),
                "Password": hash_password(instructor_password_entry.get()),
            }
        }
        try:
            with open("instructor_data.json", "r") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            with open("instructor_data.json", "w") as data_file:
                json.dump(new_data, data_file, indent=4)
        else:
            data.update(new_data)
            with open("instructor_data.json", "w") as data_file:
                json.dump(data, data_file, indent=4)

        # --- Refresher Instructor Listbox
        try:
            with open("instructor_data.json", "r") as data_file:
                Instructor_list = json.load(data_file)
        except FileNotFoundError:
            print("Instructor File not found")

        update_instructor_menu()
        instructor_window.destroy()

    # --- Add Instructor Button

    def show():
        """toggle switch to show password test"""
        if password_switch.get() == 0:
            instructor_password_entry.configure(show="")
        else:
            instructor_password_entry.configure(show="*")

    password_switch = customtkinter.CTkSwitch(instructor_frame, text="Show password", command=show,
                                              fg_color=switch_off_color,
                                              progress_color=switch_on_color,
                                              button_hover_color=switch_hover_color,
                                              button_color=switch_button_color)
    password_switch.select()
    password_switch.grid(row=7, column=3, sticky="ew", padx=(5, 20))

    # --- Add Instructor Button
    instructor_button = customtkinter.CTkButton(instructor_frame, text="Add Instructor", fg_color=main_button_color,
                                                text_color=main_button_text_color,
                                                hover_color=main_button_color_hover,
                                                command=update_instructor)
    instructor_button.grid(column=2, row=8, pady=(20))


def remove_inst(deleted_instructor):
    """delete selected instructor"""
    with open("instructor_data.json", "r") as data:
        inst_info = json.load(data)
        del inst_info[deleted_instructor]

    with open("instructor_data.json", "w") as data:
        json.dump(inst_info, data, indent=4)

    list_box.set("")
    update_instructor_menu()


def set_student():
    """Update 'fields' dictionary and "Set Instructor" label with student info."""
    index = list_box_student.curselection()
    global student_dict_global
    student = list_box_student.get(index)
    student_set_label.configure(text=student, fg=set_text_color)
    fields["Student Name"] = student

    try:
        if isinstance(student_dict_global[student]["date_of_birth"], str):
            date_of_birth = student_dict_global[student]["date_of_birth"].split("/")
            fields["Birth Date"] = date_of_birth[0]
            fields["undefined"] = date_of_birth[1]
            fields["undefined_2"] = date_of_birth[2]

        elif isinstance(student_dict_global[student]["date_of_birth"], datetime.datetime):
            date_of_birth = student_dict_global[student]["date_of_birth"]
            fields["Birth Date"] = date_of_birth.day
            fields["undefined"] = date_of_birth.month
            fields["undefined_2"] = date_of_birth.year

    except KeyError:
        print("No Birth Date")

    if student_dict_global[student]["sex"] == "male":
        fields["Check Box20"] = "Yes"
        fields["Check Box21"] = "No"
    elif student_dict_global[student]["sex"] == "female":
        fields["Check Box21"] = "Yes"
        fields["Check Box20"] = "No"

    fields["Mailing address 1"] = student_dict_global[student]["street_address"]
    fields["Mailing address 2"] = student_dict_global[student]["city"]
    fields["Mailing address 3"] = student_dict_global[student]["province"]
    try:
        fields["Mailing address 4"] = student_dict_global[student]["country"]
    except IndexError:
        print("No Country")
    fields["Mailing address 5"] = student_dict_global[student]["postal"]
    fields["undefined_4"] = student_dict_global[student]["phone"]
    fields["Email"] = student_dict_global[student]["email"]


def select_all_cw():
    """Toggle all Confined Water Checkboxes"""
    if cw_switch_list[0].get() == 1:
        for switches in cw_switch_list:
            switches.deselect()

    else:
        for switches in cw_switch_list:
            switches.select()


def select_all_kd():
    """Toggle all Knowledge Development Checkboxes"""
    if kd_switch_list[0].get() == 1:
        for switches in kd_switch_list:
            switches.deselect()
        for kr in kr_checkbox_list:
            kr.deselect()
        for video in kd_video_checkbox_list:
            video.deselect()
    else:
        for switches in kd_switch_list:
            switches.select()
        for kr in kr_checkbox_list:
            kr.select()
        for video in kd_video_checkbox_list:
            video.select()


def select_all_ow():
    """Toggle all Open Water Checkboxes"""
    if ow_switch_list[0].get() == 1:
        for switches in ow_switch_list:
            switches.deselect()
    else:
        for switches in ow_switch_list:
            switches.select()


def select_all():
    """Toggle all switches and checkboxes"""
    select_all_cw()
    select_all_kd()
    select_all_ow()
    if ow_switch_list[0].get() == 1:
        select_all_button.configure(text="Unselect All")
        main_switch_cw.select()
        main_switch_kd.select()
        main_switch_ow.select()
    else:
        select_all_button.configure(text="Select All")
        main_switch_cw.deselect()
        main_switch_kd.deselect()
        main_switch_ow.deselect()
        rdp_check.deselect()
        erdpml_check.deselect()
        computer_check.deselect()


def hash_password(password):
    """Save users password hash with salt. Return Password Dictionary"""

    # --- Generate a random salt
    salt = secrets.token_hex(10)

    # --- Hash the password using the salt and SHA-256 algorithm
    hash_object = hashlib.sha256(salt.encode() + password.encode())
    hashed_password = hash_object.hexdigest()

    # --- Create a dictionary to store the salt and hashed password
    password_data = {
        "Salt": salt,
        "Hash": hashed_password
    }
    return password_data


def choose_save_path():
    """User chooses save path for completed pdf"""
    file_path = filedialog.askdirectory()
    if file_path:
        config["save path"]["student_record_path"] = file_path
        with open("config.ini", "w") as path:
            config.write(path)


def import_student():
    """read excel file and import student data"""
    student_path = filedialog.askopenfilename()
    try:
        student_data = pandas.read_excel(student_path)
    except ValueError:
        messagebox.showerror(message="wrong file type. Support for excel files only")

    student_dict = student_data.to_dict(orient="records")

    try:
        for info in student_dict:
            full_name = f"{info['first_name']} {info['last_name']}"
            new_student_data = {
                full_name: {
                    'first_name': info['first_name'],
                    'last_name': info['last_name'],
                    'date_of_birth': info["date_of_birth"],
                    'sex': info['sex'],
                    'phone': info['phone'],
                    'email': info['email'],
                    'street_address': info['street_address'],
                    'city': info['city'],
                    'province': info['province'],
                    'postal': info['postal'],
                    'country': info['country'],
                }
            }
            student_dict_global.update(new_student_data)
            list_box_student.insert("end", full_name)
    except KeyError:
        messagebox.showerror(message="incorrect file format.  See help 'importing student data")


def refresher_main_combobox():
    with open("dive_template_data.json", "r") as data:
        template = json.load(data)

    key_list = []

    for temps in template.keys():
        key_list.append(temps)

    date_rule_box.configure(values=key_list)


def clear_dict_values():
    """clears dictionary fields for pdf form"""
    global fields
    fields = fillpdfs.get_form_fields("Record_and_Referral_Form.pdf")
    print(fields)


def reset_all():
    """resets main UI"""
    [set_date.configure(text="Set Date", fg=reset_main_text_color) for set_date in cw_set_date_list]
    [set_date.configure(text="Set Date", fg=reset_main_text_color) for set_date in kd_set_date_list]
    [set_date.configure(text="Set Date", fg=reset_main_text_color) for set_date in ow_set_date_list]
    [set_inst.configure(text="Set Instructor", fg=reset_main_text_color) for set_inst in cw_set_instructor_list]
    [set_inst.configure(text="Set Instructor", fg=reset_main_text_color) for set_inst in kd_set_instructor_list]
    [set_inst.configure(text="Set Instructor", fg=reset_main_text_color) for set_inst in ow_set_instructor_list]
    [quiz.delete(0, "end") for quiz in kd_exam_entry_list]
    [flex.delete(0, "end") for flex in ow_flex_dive_list]
    [flex.configure(placeholder_text="") for flex in ow_flex_dive_list]
    [switches.select() for switches in cw_switch_list]
    [switches.select() for switches in kd_switch_list]
    [switches.select() for switches in ow_switch_list]
    main_switch_ow.select()
    main_switch_cw.select()
    main_switch_kd.select()
    [kr_check.select() for kr_check in kr_checkbox_list]
    [vid_check.select() for vid_check in kd_video_checkbox_list]
    rdp_check.deselect()
    erdpml_check.deselect()
    computer_check.deselect()
    [cw_dates.set_date(today) for cw_dates in cw_cal_list]
    [kd_dates.set_date(today) for kd_dates in kd_cal_list]
    [ow_dates.set_date(today) for ow_dates in ow_cal_list]
    student_set_label.config(text="Set Student", font=header, background=frame_color, fg=reset_main_text_color)
    clear_dict_values()


def report_bug():
    """email support 'brendan.development@pm.me'"""
    webbrowser.open("mailto:brendan.development@pm.me")


# --------------------------- MAIN UI SETUP ------------------------------ #

window = customtkinter.CTk()
window.config(pady=(20), padx=30, bg=background_color)
window.title("Instructor Assistant")
window.geometry(f"{1750}x{970}+100+0")
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(2, weight=1)
window.iconbitmap("logo.ico")




# --- Student Listbox
student_lb_frame = customtkinter.CTkFrame(master=window, fg_color=frame_color, corner_radius=8,
                                          bg_color=background_color)
student_lb_frame.grid(row=0, column=0, pady=10, ipadx=10, ipady=10, sticky="nsew", padx=10)
student_lb_frame.grid_columnconfigure(0, weight=1)
student_label = tkinter.Label(student_lb_frame, text="Student Diver:", bg=frame_color, font=header)
student_label.grid(row=0, column=0, sticky="w", padx=(20, 0), pady=(5, 0))
student_set_label = tkinter.Label(student_lb_frame, text="Set Student", bg=frame_color, font=header)
student_set_label.grid(row=0, column=0, columnspan=2, padx=(80, 0), pady=(5, 0))
list_box_student = tkinter.Listbox(student_lb_frame, bg=listbox_color,
                                   height=student_listbox_height, font=font)
list_box_student.grid(row=1, column=0, rowspan=3, columnspan=2, padx=(20, 30), pady=(10, 0), sticky="ew")
add_student = customtkinter.CTkButton(student_lb_frame, text="Add Student", command=new_student,
                                      fg_color=main_button_color, text_color=main_button_text_color,
                                      hover_color=main_button_color_hover)
add_student.grid(row=1, column=2, padx=(0, 30))
set_student = customtkinter.CTkButton(student_lb_frame, text="Set Student", command=set_student,
                                      fg_color=main_button_color, text_color=main_button_text_color,
                                      hover_color=main_button_color_hover)
set_student.grid(row=2, column=2, padx=(0, 30))
import_student = customtkinter.CTkButton(student_lb_frame, text="Import Student", command=import_student,
                                         fg_color=main_button_color, text_color=main_button_text_color,
                                         hover_color=main_button_color_hover)
import_student.grid(row=3, column=2, padx=(0, 30))

# --- Instructor Option Menu
instructor_lb_frame = customtkinter.CTkFrame(master=window, fg_color=frame_color, corner_radius=8,
                                             bg_color=background_color)
instructor_lb_frame.grid(row=1, column=0, rowspan=1, sticky="nsew", padx=10, pady=10, ipadx=10, ipady=10)
instructor_lb_frame.grid_columnconfigure(0, weight=1)
instructor_label = tkinter.Label(instructor_lb_frame, text="PADI Instructor:", bg=frame_color, font=header)
instructor_label.grid(row=0, column=0, sticky="w", padx=(20, 0))

# --- Import Instructor information from .json
instructor_list_menu = []
try:
    with open("instructor_data.json", "r") as data_file:
        instructor_info = json.load(data_file)
        for instructor in instructor_info.keys():  # update list box
            instructor_list_menu.append(instructor)
except FileNotFoundError:
    print("No Instructor File Found")

list_box = customtkinter.CTkOptionMenu(instructor_lb_frame, values=instructor_list_menu, width=155,
                                       fg_color=background_color,
                                       text_color=text_color,
                                       button_color=main_button_color,
                                       button_hover_color=main_button_color_hover
                                       )
list_box.grid(row=0, column=1, padx=(0, 80), pady=20)
add_inst_button = customtkinter.CTkButton(instructor_lb_frame, text="Add Instructor", command=new_instructor,
                                          fg_color=main_button_color, text_color=main_button_text_color,
                                          hover_color=main_button_color_hover)
add_inst_button.grid(row=0, column=2, padx=(0, 30))
set_inst_button = customtkinter.CTkButton(instructor_lb_frame, text="Set Instructor", command=set_instructor,
                                          fg_color=main_button_color, text_color=main_button_text_color,
                                          hover_color=main_button_color_hover)
set_inst_button.grid(row=1, column=1, padx=(0, 80))
del_inst_button = customtkinter.CTkButton(instructor_lb_frame, text="Delete Instructor",
                                          command=lambda: remove_inst(list_box.get()),
                                          fg_color=main_button_color, text_color=main_button_text_color,
                                          hover_color=main_button_color_hover)
del_inst_button.grid(row=1, column=2, padx=(0, 30))

# --------------------------- CONFINED WATER ------------------------ #


confined_water_frame = customtkinter.CTkFrame(window, fg_color=frame_color, corner_radius=8, bg_color=background_color)
confined_water_frame.grid(column=0, row=2, padx=10, pady=10, sticky="nsew", ipadx=10, ipady=10)

main_switch_cw = customtkinter.CTkSwitch(confined_water_frame, text="", command=select_all_cw,
                                         fg_color=master_switch_off_color,
                                         progress_color=master_switch_on_color,
                                         button_hover_color=master_switch_hover_color,
                                         button_color=master_switch_button_color)
main_switch_cw.select()
main_switch_cw.grid(row=0, column=3, columnspan=2, stick="w")

# Confined Water Labels
confined_water_section = tkinter.Label(confined_water_frame, text="Confined Water", bg=frame_color, font=header)
confined_water_section.grid(row=0, column=0, pady=10)

for cw_l in range(15):
    cw_label = tkinter.Label(confined_water_frame, text=cw_label_list[cw_l], bg=frame_color, font=font)
    cw_label.grid(row=cw_l + 1, column=0, padx=(20, 0), sticky="e")

# Confined Water Calendar
cw_cal_list = []
for cw_c in range(15):
    cw_cal = DateEntry(confined_water_frame, selectmode="day", font=font)
    cw_cal.grid(row=cw_c + 1, column=1, padx=5)
    cw_cal_list.append(cw_cal)

# Confined Water Set Instructor Label
cw_set_instructor_list = []
for cw_inst in range(15):
    cw_set_inst = tkinter.Label(confined_water_frame, text="Set Instructor", bg=frame_color, font=font)
    cw_set_inst.grid(row=cw_inst + 1, column=2, padx=20)
    cw_set_instructor_list.append(cw_set_inst)

# Confined Water Set Date Labels
cw_set_date_list = []
for cw_date in range(15):
    cw_set_date = tkinter.Label(confined_water_frame, text="Set Date", bg=frame_color, font=font)
    cw_set_date.grid(row=cw_date + 1, column=4, padx=(0, 20))
    cw_set_date_list.append(cw_set_date)

# Confined Water Switches
cw_switch_list = []
for cw_switch in range(15):
    cw_main_switch = customtkinter.CTkSwitch(confined_water_frame, text="",
                                             fg_color=switch_off_color,
                                             progress_color=switch_on_color,
                                             button_hover_color=switch_hover_color,
                                             button_color=switch_button_color
                                             )
    cw_main_switch.grid(row=cw_switch + 1, column=3)
    cw_main_switch.select()
    cw_switch_list.append(cw_main_switch)

# --------------------------- KNOWLEDGE DEVELOPMENT ----------------- #


knowledge_development_frame = customtkinter.CTkFrame(window, fg_color=frame_color,
                                                     corner_radius=8, bg_color=background_color)
knowledge_development_frame.grid(row=0, column=1, rowspan=2, padx=20, pady=10, sticky="nsew", columnspan=2, ipadx=10,
                                 ipady=10)

knowledge_development_section = tkinter.Label(knowledge_development_frame, text="Knowledge Development", bg=frame_color,
                                              font=header)
knowledge_development_section.grid(row=0, column=0, sticky="w", pady=10, padx=(20, 0), columnspan=2)

main_switch_kd = customtkinter.CTkSwitch(knowledge_development_frame, text="", command=select_all_kd,
                                         fg_color=master_switch_off_color,
                                         progress_color=master_switch_on_color,
                                         button_color=master_switch_button_color,
                                         button_hover_color=master_switch_hover_color
                                         )
main_switch_kd.select()
main_switch_kd.grid(row=2, column=3, )

# --- RDP or eRDPml or Computer
course_option_label = tkinter.Label(knowledge_development_frame, text="Course Option:", bg=frame_color, font=font)
course_option_label.grid(row=1, column=3, pady=(0, 10))
rdp_check = customtkinter.CTkCheckBox(knowledge_development_frame, text="RDP", checkbox_width=20,
                                      checkbox_height=20,
                                      fg_color=switch_on_color,
                                      hover_color=switch_hover_color,
                                      border_color=switch_on_color,
                                      )

rdp_check.grid(row=1, column=5, pady=(0, 10))

erdpml_check = customtkinter.CTkCheckBox(knowledge_development_frame, text="eRDPml", checkbox_width=20,
                                         checkbox_height=20,
                                         fg_color=switch_on_color,
                                         hover_color=switch_hover_color,
                                         border_color=switch_on_color,
                                         )
erdpml_check.grid(row=1, column=6, pady=(0, 10))

computer_check = customtkinter.CTkCheckBox(knowledge_development_frame, text="Computer", checkbox_width=20,
                                           checkbox_height=20,
                                           fg_color=switch_on_color,
                                           hover_color=switch_hover_color,
                                           border_color=switch_on_color,

                                           )
computer_check.grid(row=1, column=7, pady=(0, 10))

kr_complete = tkinter.Label(knowledge_development_frame, text="Knowledge", bg=frame_color, font=font)
kr_complete.grid(row=2, column=4, padx=(0, 5), columnspan=2)
pass_exam = tkinter.Label(knowledge_development_frame, text="Quiz/Exam", bg=frame_color, font=font)
pass_exam.grid(row=2, column=5, columnspan=2, padx=(15, 0))
video_complete = tkinter.Label(knowledge_development_frame, text="Video", bg=frame_color, font=font)
video_complete.grid(row=2, column=6, columnspan=2, padx=(20, 0))

# Knowledge Development string
for kd_s in range(7):
    kd_string = tkinter.Label(knowledge_development_frame, text=kd_string_list[kd_s],
                              font=font, background=frame_color)
    kd_string.grid(row=kd_s + 3, column=0, padx=(30, 0), sticky="e")

# Knowledge Development Calendar
kd_cal_list = []
for kd_c in range(7):
    kd_cal = DateEntry(knowledge_development_frame, selectmode="day", font=font)
    kd_cal.grid(row=kd_c + 3, column=1, padx=5, pady=2)
    kd_cal_list.append(kd_cal)

# Knowledge Development Set Instructor Label
kd_set_instructor_list = []
for kd_inst in range(7):
    kd_set_inst = tkinter.Label(knowledge_development_frame, text="Set Instructor", bg=frame_color, font=font)
    kd_set_inst.grid(row=kd_inst + 3, column=2, padx=20)
    kd_set_instructor_list.append(kd_set_inst)

# Knowledge Development Set Date Labels
kd_set_date_list = []
for kd_date in range(7):
    kd_set_date = tkinter.Label(knowledge_development_frame, text="Set Date", bg=frame_color, font=font)
    kd_set_date.grid(row=kd_date + 3, column=4, padx=(0, 20))
    kd_set_date_list.append(kd_set_date)

# Knowledge Development Switches
kd_switch_list = []
for kd_switch in range(7):
    kd_main_switch = customtkinter.CTkSwitch(knowledge_development_frame, text="",
                                             fg_color=switch_off_color,
                                             progress_color=switch_on_color,
                                             button_hover_color=switch_hover_color,
                                             button_color=switch_button_color
                                             )
    kd_main_switch.grid(row=kd_switch + 3, column=3)
    kd_main_switch.select()
    kd_switch_list.append(kd_main_switch)

# --- Knowledge Quiz/Exam Checkbox
kr_checkbox_list = []
for kd_box in range(7):
    kd_check_box = customtkinter.CTkCheckBox(knowledge_development_frame, text="", checkbox_width=20,
                                             checkbox_height=20,
                                             fg_color=switch_on_color,
                                             hover_color=switch_hover_color,
                                             border_color=switch_on_color,

                                             )
    kd_check_box.grid(row=kd_box + 3, column=5, padx=(5, 0))
    kd_check_box.select()
    kr_checkbox_list.append(kd_check_box)

kd_video_checkbox_list = []
for kd_vid in range(7):
    kd_vid_box = customtkinter.CTkCheckBox(knowledge_development_frame, text="", checkbox_width=20,
                                           checkbox_height=20,
                                           fg_color=switch_on_color,
                                           hover_color=switch_hover_color,
                                           border_color=switch_on_color,

                                           )

    kd_vid_box.grid(row=kd_vid + 3, column=7, padx=(0, 5))
    kd_vid_box.select()
    kd_video_checkbox_list.append(kd_vid_box)

kd_exam_entry_list = []
for kd_exam in range(6):
    kd_exam_entry = customtkinter.CTkEntry(knowledge_development_frame, width=70, height=25)
    kd_exam_entry.grid(row=kd_exam + 3, column=5, columnspan=2, padx=(25, 5))
    kd_exam_entry_list.append(kd_exam_entry)

# --------------------------- OPEN WATER FLEX ENTRY ----------------- #


open_water_frame = customtkinter.CTkFrame(window, fg_color=frame_color,
                                          corner_radius=8, bg_color=background_color)
open_water_frame.grid(column=1, row=2, rowspan=1, stick="nsew", padx=(20, 10), pady=10, ipadx=10, ipady=10)

open_water_section = tkinter.Label(open_water_frame, text="Open Water", bg=frame_color,
                                   font=header)
open_water_section.grid(row=0, column=0, sticky="w", pady=10, padx=(20, 0), columnspan=2)

# Main Switch
main_switch_ow = customtkinter.CTkSwitch(open_water_frame, text="", command=select_all_ow,
                                         fg_color=master_switch_off_color,
                                         progress_color=master_switch_on_color,
                                         button_color=master_switch_button_color,
                                         button_hover_color=master_switch_hover_color
                                         )
main_switch_ow.select()
main_switch_ow.grid(row=0, column=3, columnspan=1)

for ow_s in range(16):
    ow_string = tkinter.Label(open_water_frame, text=ow_string_list[ow_s], font=font, background=frame_color)
    ow_string.grid(row=ow_s + 1, column=0, padx=(20, 0), sticky="e")

ow_cal_list = []
for ow_c in range(16):
    if 3 < ow_c < 14:
        pass
    else:
        ow_cal = DateEntry(open_water_frame, selectmode="day", font=font)
        ow_cal.grid(row=ow_c + 1, column=1, padx=5)
        ow_cal_list.append(ow_cal)

# Open Water Set Instructor Label
ow_set_instructor_list = []
for ow_inst in range(16):
    ow_set_inst = tkinter.Label(open_water_frame, text="Set Instructor", bg=frame_color, font=font)
    ow_set_inst.grid(row=ow_inst + 1, column=2, padx=20)
    ow_set_instructor_list.append(ow_set_inst)

# Knowledge Development Set Date Labels
ow_set_date_list = []
for ow_date in range(16):
    ow_set_date = tkinter.Label(open_water_frame, text="Set Date", bg=frame_color, font=font)
    ow_set_date.grid(row=ow_date + 1, column=4)
    ow_set_date_list.append(ow_set_date)

# Knowledge Development Switches
ow_switch_list = []
for ow_switch in range(16):
    ow_main_switch = customtkinter.CTkSwitch(open_water_frame, text="",
                                             fg_color=switch_off_color,
                                             progress_color=switch_on_color,
                                             button_hover_color=switch_hover_color,
                                             button_color=switch_button_color
                                             )
    ow_main_switch.grid(row=ow_switch + 1, column=3)
    ow_main_switch.select()
    ow_switch_list.append(ow_main_switch)

# Dive flex entry boxes
ow_flex_dive_list = []
for flex_c in range(16):
    if 3 < flex_c < 14:
        flex_cal = customtkinter.CTkEntry(open_water_frame, width=40, height=15)
        flex_cal.grid(row=flex_c + 1, column=1, padx=5)
        ow_flex_dive_list.append(flex_cal)

# --------------------------- RIGHT BUTTON MENU ------------------------- #


right_frame = customtkinter.CTkFrame(window, fg_color=frame_color, corner_radius=8, bg_color=background_color)
right_frame.grid(row=2, column=2, sticky="nsew", padx=(10, 20), pady=10, )

choose_template_label = tkinter.Label(right_frame, text="Choose Template:", font=font, bg=frame_color)
choose_template_label.grid(row=0, column=0, pady=(20, 5))

key_list = []
try:
    with open("dive_template_data.json", "r") as data_file:
        data = json.load(data_file)
        for keys in data.keys():
            key_list.append(keys)

except FileNotFoundError:
    print("template file no found")

date_rule_box = customtkinter.CTkOptionMenu(right_frame, values=key_list, width=155,
                                            fg_color=background_color,
                                            text_color=text_color,
                                            button_color=main_button_color,
                                            button_hover_color=main_button_color_hover
                                            )
date_rule_box.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

set_date_rule_button = customtkinter.CTkButton(right_frame, text="Set Template", command=execute_template,
                                               fg_color=main_button_color, text_color=main_button_text_color,
                                               hover_color=main_button_color_hover)
set_date_rule_button.grid(row=2, column=0, pady=(5, 10))

set_date_button = customtkinter.CTkButton(right_frame, text="New Template", command=new_template,
                                          fg_color=main_button_color,
                                          text_color=main_button_text_color,
                                          hover_color=main_button_color_hover)
set_date_button.grid(row=3, column=0, pady=(0, 70))

set_date_button = customtkinter.CTkButton(right_frame, text="Set Date/Dive", command=set_date,
                                          fg_color=main_button_color,
                                          text_color=main_button_text_color,
                                          hover_color=main_button_color_hover)
set_date_button.grid(row=4, column=0, pady=(0, 10))

refresh_main = customtkinter.CTkButton(master=right_frame, text="Reset All", command=reset_all,
                                       fg_color=main_button_color, text_color=main_button_text_color,
                                       hover_color=main_button_color_hover)
refresh_main.grid(row=5, column=0, pady=(0, 10))

select_all_button = customtkinter.CTkButton(master=right_frame, text="Unselect All", command=select_all,
                                            fg_color=main_button_color, text_color=main_button_text_color,
                                            hover_color=main_button_color_hover)
select_all_button.grid(row=6, column=0, pady=(0, 10))

select_elearning_button = customtkinter.CTkButton(master=right_frame, text="Elearning",
                                                  command=or_elearning_select, fg_color=main_button_color,
                                                  text_color=main_button_text_color,
                                                  hover_color=main_button_color_hover)
select_elearning_button.grid(row=7, column=0, pady=(0, 70))

gen_pfd_button = customtkinter.CTkButton(right_frame, text="Generate PDF", command=generate_pdf,
                                         fg_color=main_button_color, text_color=main_button_text_color,
                                         hover_color=main_button_color_hover)
gen_pfd_button.grid(row=8, column=0)

# --------------------------- FILE MENU ----------------------------- #

menubar = Menu(window)

# --- Adding File Menu and commands
file = Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=file)
file.add_command(label='Start New', command=reset_all)
file.add_separator()
file.add_command(label='Exit', command=window.destroy)

# --- Adding Edit Menu and commands
edit = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Edit', menu=edit)
edit.add_command(label='Choose PDF Save Path', command=choose_save_path)
edit.add_command(label='New Template', command=new_template)

# - add themes in future
# --- Settings
# settings = Menu(menubar, tearoff=False)
# menubar.add_cascade(label="Settings", menu=settings)
# sub_menu = Menu(settings, tearoff=False)
# sub_menu.add_command(label='Light', command=lambda: theme_update("light_theme"))
# sub_menu.add_command(label='Sea', command=lambda: theme_update("sea_theme"))
# settings.add_cascade(label='Theme', menu=sub_menu)

# --- Adding Help Menu
help_ = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Help', menu=help_)
help_.add_command(label='Report a Issue', command=report_bug)
help_.add_separator()
help_.add_command(label='About Instructor Paperwork Assistant', command=None)

# --- Display Menu
window.config(menu=menubar)

window.mainloop()

