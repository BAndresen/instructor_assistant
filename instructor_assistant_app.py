"""PADI Scuba Diving Instructors are required to complete the 'Record_and_Referral_Form' for every student
after the PADI Open Water Course. This 'Instructor Assistant' aims to make that process fast and easy.

Author: Brendan Andresen <brendan.development@pm.me>
Created: May 6th, 2023
"""


__version__ = "1.0.0"

import datetime
import os
import tkinter
import json
import hashlib
import secrets
import customtkinter
import pandas
import configparser
import webbrowser

from tkcalendar import DateEntry
from fillpdf import fillpdfs
from tkinter import Toplevel, Menu, messagebox, filedialog
from dataclasses import dataclass

# Datetime
today = datetime.datetime.today()

# Constants
path = os.getcwd()

UI_SETUP_LABELS = f"{path}\\config\\ui_setup_labels.json"
with open(UI_SETUP_LABELS, "r") as file:
    data = json.load(file)
CONFINED_WATER_LABELS = data["cw_water_list"]
KNOWLEDGE_DEVELOPMENT_LABELS = data["kd_string_list"]
OPEN_WATER_LABELS = data["ow_string_list"]
STUDENT_AND_REFERRAL_FORM = f"{path}\\assets\\Record_and_Referral_Form.pdf"
STANDARD_FONT = ("roboto", "10")
TITLE_HEADER_FONT = ("roboto", "14")

INSTRUCTOR_DATA = f"{path}\\config\\instructor_data.json"
DIVE_TEMPLATE_DATA = f"{path}\\config\\dive_template_data.json"

# Student Information Global Dictionary
student_dict_global = {}


@dataclass
class Student:
    first_name: str
    last_name: str
    date_of_birth: str
    sex: str
    phone: str
    email: str
    street_address: str
    city: str
    province: str
    postal: str
    country: str


# --------------------------- THEME --------------------------------- #


class Theme:
    def __init__(self, style: str, style_dict: dict):
        self.set_text_color = style_dict[style]["set_text_color"]
        self.reset_main_text_color = style_dict[style]["reset_main_text_color"]
        self.listbox_color = style_dict[style]["listbox_color"]
        self.text_color = style_dict[style]["text_color"]
        self.background_color = style_dict[style]["background_color"]
        self.frame_color = style_dict[style]["frame_color"]
        self.main_button_color = style_dict[style]["main_button_color"]
        self.main_button_color_hover = style_dict[style]["main_button_color_hover"]
        self.main_button_text_color = style_dict[style]["main_button_text_color"]
        self.switch_on_color = style_dict[style]["switch_on_color"]
        self.switch_off_color = style_dict[style]["switch_off_color"]
        self.switch_button_color = style_dict[style]["switch_button_color"]
        self.switch_hover_color = style_dict[style]["switch_hover_color"]
        self.master_switch_on_color = style_dict[style]["master_switch_on_color"]
        self.master_switch_off_color = style_dict[style]["master_switch_off_color"]
        self.master_switch_button_color = style_dict[style]["master_switch_button_color"]
        self.master_switch_hover_color = style_dict[style]["master_switch_hover_color"]


def or_elearning_select():
    """Toggle Checkboxes for Knowledge Development"""
    if main_ui.kd_switch_list[0].get() == 1:
        [switches.deselect() for switches in main_ui.kd_switch_list if main_ui.kd_switch_list.index(switches) < 5]
        [kr_check.deselect() for kr_check in main_ui.kr_checkbox_list if main_ui.kr_checkbox_list.index(kr_check) < 5]
        [vid_check.deselect() for vid_check in main_ui.kd_video_checkbox_list if
         main_ui.kd_video_checkbox_list.index(vid_check) < 5]
        main_ui.kd_switch_list[5].select()
        main_ui.kd_video_checkbox_list[5].select()
        main_ui.kr_checkbox_list[5].select()
        main_ui.select_elearning_button.configure(text="Manual & Classroom")

    else:
        [switches.select() for switches in main_ui.kd_switch_list if main_ui.kd_switch_list.index(switches) < 5]
        [kr_check.select() for kr_check in main_ui.kr_checkbox_list if main_ui.kr_checkbox_list.index(kr_check) < 5]
        [vid_check.select() for vid_check in main_ui.kd_video_checkbox_list if
         main_ui.kd_video_checkbox_list.index(vid_check) < 5]
        main_ui.kd_switch_list[5].deselect()
        main_ui.kd_video_checkbox_list[5].deselect()
        main_ui.kr_checkbox_list[5].deselect()
        main_ui.select_elearning_button.configure(text="Elearning")


def new_template(ui):
    """New UI Window for user to make a new custom Dive Template.  Often Instructors complete skills in a
    consistent sequence.  Applying a dive template allows instructors to autofill sections based on information
    from other sections"""
    new_template_window = Toplevel(ui)
    new_template_window.config(pady=50, padx=50)
    new_template_window.geometry("1400x975+200+0")
    new_template_window.iconbitmap("assets/logo.ico")

    new_template_window.grid_columnconfigure(0, weight=1)
    new_template_window.grid_columnconfigure(1, weight=1)
    new_template_window.grid_rowconfigure(0, weight=1)
    new_template_window.grid_rowconfigure(1, weight=1)

    # --- Title Template
    template_title_frame = customtkinter.CTkFrame(new_template_window, fg_color=theme.frame_color)
    template_title_frame.grid(row=0, column=0, padx=10, pady=10, stick="nsew")
    template_name_entry = customtkinter.CTkEntry(template_title_frame, width=200, height=30,
                                                 text_color=theme.text_color,
                                                 fg_color=theme.listbox_color,
                                                 border_color=theme.main_button_color)

    template_name_entry.grid(column=1, row=0, pady=20, sticky="w")
    template_name_label = tkinter.Label(template_title_frame, text="Template Name:", font=TITLE_HEADER_FONT,
                                        background=theme.frame_color)
    template_name_label.grid(column=0, row=0, pady=20, padx=(20, 10))

    # ----------------------- CONFINED WATER FRAME TEMPLATE WINDOW -------------------- #

    template_confined_frame = customtkinter.CTkFrame(new_template_window, fg_color=theme.frame_color)
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
                               font=STANDARD_FONT, background=theme.frame_color)
        string.grid(row=i + 1, column=0, sticky="e", padx=(20, 5))
        confined_water_string_template_list.append(string)

    confined_water_section_set_rule = tkinter.Label(template_confined_frame, text="Confined Water",
                                                    font=TITLE_HEADER_FONT,
                                                    background=theme.frame_color)
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

    cw_reset_switch = customtkinter.CTkSwitch(template_confined_frame, text="", command=reset,
                                              fg_color=theme.master_switch_off_color,
                                              progress_color=theme.master_switch_on_color,
                                              button_color=theme.master_switch_button_color,
                                              button_hover_color=theme.master_switch_hover_color,
                                              width=65)

    cw_reset_switch.select()
    cw_reset_switch.grid(row=0, column=2, pady=(20, 5), padx=(0))

    # create row of switches
    cw_switch_list = []
    for i in range(15):
        switch = customtkinter.CTkSwitch(template_confined_frame, text="",
                                         command=lambda p=i: switch_press(p),
                                         fg_color=theme.switch_off_color,
                                         progress_color=theme.switch_on_color,
                                         button_color=theme.switch_button_color,
                                         button_hover_color=theme.switch_hover_color,
                                         width=65
                                         )
        switch.grid(row=i + 1, column=2, padx=10)
        switch.select()
        cw_switch_list.append(switch)

    # create row of entries
    cw_entry_list = []
    for n in range(15):
        cw_entry = customtkinter.CTkEntry(template_confined_frame, width=40,
                                          placeholder_text_color=theme.text_color, placeholder_text=n, height=25,
                                          text_color=theme.text_color,
                                          fg_color=theme.listbox_color,
                                          border_color=theme.main_button_color,
                                          )

        cw_entry.grid(row=n + 1, column=1, pady=2)
        cw_entry_list.append(cw_entry)

    # --------------------------- KNOWLEDGE DEVELOPMENT TEMPLATE WINDOW ----------------- #

    template_knowledge_frame = customtkinter.CTkFrame(new_template_window, fg_color=theme.frame_color)
    template_knowledge_frame.grid(row=0, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky="nsew")
    knowledge_development_title = tkinter.Label(template_knowledge_frame, text="Knowledge Development",
                                                font=TITLE_HEADER_FONT, background=theme.frame_color)
    knowledge_development_title.grid(row=0, column=0, padx=20, pady=(20, 0))
    pass_exam_set_rule = tkinter.Label(template_knowledge_frame, text="Quiz/Exam", font=STANDARD_FONT,
                                       background=theme.frame_color)
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

    kd_reset_switch = customtkinter.CTkSwitch(template_knowledge_frame, text="", command=reset_kd,
                                              fg_color=theme.master_switch_off_color,
                                              progress_color=theme.master_switch_on_color,
                                              button_color=theme.master_switch_button_color,
                                              button_hover_color=theme.master_switch_hover_color,
                                              width=65)

    kd_reset_switch.select()
    kd_reset_switch.grid(row=0, column=2, pady=(15, 0), padx=(7, 0))

    for n in range(7):
        kd_string = tkinter.Label(template_knowledge_frame, text=knowledge_string_template_list[n],
                                  font=STANDARD_FONT, background=theme.frame_color)
        kd_string.grid(row=n + 1, column=0, padx=(33, 5), sticky="e")

    for i in range(7):
        switch = customtkinter.CTkSwitch(template_knowledge_frame, text="",
                                         command=lambda p=i: switch_press_kd(p),
                                         fg_color=theme.switch_off_color,
                                         progress_color=theme.switch_on_color,
                                         button_color=theme.switch_button_color,
                                         button_hover_color=theme.switch_hover_color,
                                         width=65
                                         )
        switch.grid(row=i + 1, column=2, padx=(10, 0))
        switch.select()
        kd_switch_list.append(switch)

    # create row of entries
    kd_entry_list = []
    for n in range(7):
        kd_entry = customtkinter.CTkEntry(template_knowledge_frame, placeholder_text=(n + 15),
                                          width=40,
                                          placeholder_text_color=theme.text_color,
                                          height=25,
                                          text_color=theme.text_color,
                                          fg_color=theme.listbox_color,
                                          border_color=theme.main_button_color)

        kd_entry.grid(row=n + 1, column=1, pady=2)
        kd_entry_list.append(kd_entry)

    kd_exam_entry_list = []
    for n in range(6):
        kd_entry_exam = customtkinter.CTkEntry(template_knowledge_frame, placeholder_text=(""), width=60, height=25,
                                               text_color=theme.text_color,
                                               fg_color=theme.listbox_color,
                                               border_color=theme.main_button_color)
        kd_entry_exam.grid(row=n + 1, column=3, columnspan=1, padx=(0, 20))
        kd_exam_entry_list.append(kd_entry_exam)

    # ----------------------------- OPEN WATER -------------------------- #

    template_open_water = customtkinter.CTkFrame(new_template_window, fg_color=theme.frame_color)
    template_open_water.grid(row=1, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky="nsew")

    # --- Open Water Dives Labels - Set Rule Window
    ow_dives_label_set_rule = tkinter.Label(template_open_water, text="Open Water Dives", font=TITLE_HEADER_FONT,
                                            background=theme.frame_color)
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

    ow_reset_switch = customtkinter.CTkSwitch(template_open_water, text="", command=reset_ow,
                                              fg_color=theme.master_switch_off_color,
                                              progress_color=theme.master_switch_on_color,
                                              button_color=theme.master_switch_button_color,
                                              button_hover_color=theme.master_switch_hover_color,
                                              width=65)

    ow_reset_switch.select()
    ow_reset_switch.grid(row=0, column=2, )

    for n in range(16):
        ow_string = tkinter.Label(template_open_water, text=ow_string_list_template[n],
                                  font=STANDARD_FONT, background=theme.frame_color)
        ow_string.grid(row=n + 1, column=0, padx=(20, 5), sticky="e")

    ow_switch_list = []
    for i in range(16):
        switch = customtkinter.CTkSwitch(template_open_water, text="",
                                         command=lambda p=i: switch_press_ow(p),
                                         fg_color=theme.switch_off_color,
                                         progress_color=theme.switch_on_color,
                                         button_color=theme.switch_button_color,
                                         button_hover_color=theme.switch_hover_color,
                                         width=65
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
                                              placeholder_text_color=theme.text_color,
                                              height=25,
                                              text_color=theme.text_color,
                                              fg_color=theme.listbox_color,
                                              border_color=theme.main_button_color)

            ow_entry.grid(row=n + 1, column=1, pady=2)
        else:
            ow_entry = customtkinter.CTkEntry(template_open_water, placeholder_text=(index_ow), width=40,
                                              placeholder_text_color=theme.text_color,
                                              height=25,
                                              text_color=theme.text_color,
                                              fg_color=theme.listbox_color,
                                              border_color=theme.main_button_color)
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

    course_option_frame = customtkinter.CTkFrame(new_template_window, fg_color=theme.frame_color)
    course_option_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    course_option_label_set_rule = tkinter.Label(course_option_frame, text="Course Option:", font=TITLE_HEADER_FONT,
                                                 background=theme.frame_color)
    course_option_label_set_rule.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    rdp_table_switch_set_rule = customtkinter.CTkSwitch(course_option_frame, text="RDP Table",
                                                        fg_color=theme.switch_off_color,
                                                        progress_color=theme.switch_on_color,
                                                        button_color=theme.switch_button_color,
                                                        button_hover_color=theme.switch_hover_color,
                                                        text_color=theme.text_color,
                                                        width=65
                                                        )
    rdp_table_switch_set_rule.grid(row=2, column=0, pady=4, padx=(2, 0))

    erdpml_switch_set_rule = customtkinter.CTkSwitch(course_option_frame, text="eRDPml",
                                                     fg_color=theme.switch_off_color,
                                                     progress_color=theme.switch_on_color,
                                                     button_color=theme.switch_button_color,
                                                     button_hover_color=theme.switch_hover_color,
                                                     text_color=theme.text_color,
                                                     width=65
                                                     )
    erdpml_switch_set_rule.grid(row=4, column=0, pady=4, padx=(0, 10))
    computer_switch_set_rule = customtkinter.CTkSwitch(course_option_frame, text="Computer",
                                                       fg_color=theme.switch_off_color,
                                                       progress_color=theme.switch_on_color,
                                                       button_color=theme.switch_button_color,
                                                       button_hover_color=theme.switch_hover_color,
                                                       text_color=theme.text_color,
                                                       width=65
                                                       )
    computer_switch_set_rule.grid(row=5, column=0, pady=4)

    elearning_manual_button = customtkinter.CTkButton(course_option_frame, text="Elearning",
                                                      fg_color=theme.main_button_color,
                                                      text_color=theme.main_button_text_color,
                                                      hover_color=theme.main_button_color_hover,
                                                      command=elearning
                                                      )
    elearning_manual_button.grid(row=6, column=0, pady=20)

    # --------------------------- RIGHT BUTTON FRAME TEMPLATE WINDOW

    template_right_frame = customtkinter.CTkFrame(new_template_window, fg_color=theme.frame_color)
    template_right_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

    def delete_template(nuked_rule):
        with open(DIVE_TEMPLATE_DATA, "r") as data:
            temp = json.load(data)

        del temp[nuked_rule]
        with open(DIVE_TEMPLATE_DATA, "w") as data:
            json.dump(temp, data, indent=4)

        date_rule_box_set_rule.configure(values=temp)
        date_rule_box_set_rule.set("")
        main_ui.date_rule_box.set("")
        main_ui.date_rule_box.configure(values=temp)

    delete_label = tkinter.Label(template_right_frame, text="Delete Template", font=STANDARD_FONT,
                                 background=theme.frame_color)
    delete_label.grid(row=0, column=0, pady=(20, 5))

    try:
        with open(DIVE_TEMPLATE_DATA, "r") as data:
            templates = json.load(data)
    except FileNotFoundError:
        templates = {}

    delete_values = []
    for temps in templates.keys():
        delete_values.append(temps)
    date_rule_box_set_rule = customtkinter.CTkOptionMenu(template_right_frame, values=delete_values,
                                                         fg_color=theme.background_color,
                                                         text_color=theme.text_color,
                                                         button_color=theme.main_button_color,
                                                         button_hover_color=theme.main_button_color_hover,
                                                         dropdown_fg_color=theme.background_color,
                                                         dropdown_text_color=theme.text_color,
                                                         dropdown_hover_color=theme.frame_color
                                                         )
    date_rule_box_set_rule.grid(row=1, column=0, padx=(15, 0), pady=(0, 20))

    delete_rule_button = customtkinter.CTkButton(template_right_frame, text="Delete Template:",
                                                 fg_color=theme.main_button_color,
                                                 text_color=theme.main_button_text_color,
                                                 hover_color=theme.main_button_color_hover,
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
        cal_index = 0
        for cal in all_cal_entries:
            if cal.get() == "":
                # .get() returns an empty string if placeholder is left
                new_data[template_name]["calendar_entries"].append(cal.cget("placeholder_text"))
                cal_index += 1
            elif cal.get() == "--":
                new_data[template_name]["calendar_entries"].append(cal_index)
                cal_index += 1
            else:
                calendar_code = int(cal.get())
                new_data[template_name]["calendar_entries"].append(calendar_code)
                cal_index += 1

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
            with open(DIVE_TEMPLATE_DATA, "r") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            with open(DIVE_TEMPLATE_DATA, "w") as data_file:
                json.dump(new_data, data_file, indent=4)
        else:
            data.update(new_data)

            new_key_list = []
            for templates in data.keys():
                new_key_list.append(templates)

            main_ui.date_rule_box.configure(values=new_key_list)

            with open(DIVE_TEMPLATE_DATA, "w") as data_file:
                json.dump(data, data_file, indent=4)

        new_template_window.destroy()

    set_rule_button = customtkinter.CTkButton(template_right_frame, text="Save Template",
                                              fg_color=theme.main_button_color, text_color=theme.main_button_text_color,
                                              hover_color=theme.main_button_color_hover,
                                              command=save_template)

    set_rule_button.grid(column=0, row=3, padx=(15, 0), pady=(350, 0))


def execute_template():
    """Function to set Dates and Dives in main Window to users specs.'"""

    with open(DIVE_TEMPLATE_DATA, "r") as datafile:  # --- Open Dictionary with Users Date/Dive Specs
        date_dict = json.load(datafile)

    template_name = main_ui.date_rule_box.get()
    all_cal_entries_list = main_ui.cw_cal_list + main_ui.kd_cal_list + main_ui.ow_cal_list
    all_switch_list = main_ui.cw_switch_list + main_ui.kd_switch_list + main_ui.ow_switch_list

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
    for switches in main_ui.kd_switch_list:
        if switches.get() == 0:
            main_ui.kr_checkbox_list[kr_index].deselect()
            main_ui.kd_video_checkbox_list[kr_index].deselect()
        kr_index += 1

    index_kw = 0
    for i in date_dict[template_name]["knowledge_quiz"]:
        main_ui.kd_exam_entry_list[index_kw].configure(placeholder_text=i)
        index_kw += 1

    index_dive_flex = 0
    for i in date_dict[template_name]["dive_flex"]:
        if i == "--":
            index_dive_flex += 1
        else:
            main_ui.ow_flex_dive_list[index_dive_flex].configure(placeholder_text=i)
            index_dive_flex += 1

    if date_dict[template_name]["course_option"][0] == 1:
        main_ui.rdp_check.select()

    if date_dict[template_name]["course_option"][1] == 1:
        main_ui.erdpml_check.select()

    if date_dict[template_name]["course_option"][2] == 1:
        main_ui.computer_check.select()


def set_instructor(ui):
    """Password Verification UI window for users to input their Instructor Password."""
    with open(INSTRUCTOR_DATA, "r") as data_file:
        instructor_list = json.load(data_file)
    set_inst = main_ui.list_box.get()
    inst = main_ui.list_box.get()
    pass_window = Toplevel(ui)
    pass_window.geometry("500x250")
    pass_window.title("Instructor Password")
    pass_window.iconbitmap("assets/logo.ico")

    pass_window.config(pady=50, padx=50, background=theme.background_color)
    pass_window.grid_columnconfigure(0, weight=1)
    pass_frame = customtkinter.CTkFrame(pass_window, fg_color=theme.frame_color)
    pass_frame.grid(row=1, column=0, sticky="nsew")
    pass_frame.grid_columnconfigure(0, weight=1)
    pass_label = tkinter.Label(pass_window, text="Verify Instructor Password", font=TITLE_HEADER_FONT,
                               background=theme.background_color)
    pass_label.grid(column=0, row=0, sticky="w")
    pass_entry = customtkinter.CTkEntry(pass_frame, show="*",
                                        text_color=theme.text_color,
                                        fg_color=theme.listbox_color,
                                        border_color=theme.main_button_color)

    pass_entry.grid(column=0, row=0, pady=10, padx=10, sticky="ew")
    salt = (instructor_list[inst]["Password"]["Salt"])
    hashed_pass = (instructor_list[inst]["Password"]["Hash"])

    def show():
        if password_switch.get() == 0:
            pass_entry.configure(show="")
        else:
            pass_entry.configure(show="*")

    password_switch = customtkinter.CTkSwitch(pass_frame, text="Show password", command=show,
                                              fg_color=theme.switch_off_color,
                                              progress_color=theme.switch_on_color,
                                              button_hover_color=theme.switch_hover_color,
                                              button_color=theme.switch_button_color)
    password_switch.select()
    password_switch.grid(row=0, column=1, sticky="ew", padx=(5, 20))

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
            if main_ui.cw_switch_list[0].get() == 1:
                main_ui.cw_set_instructor_list[0].config(text=inst, fg=theme.set_text_color)
                fields["Initials 1"] = instructor_list[set_inst]["Initials"]
                fields["undefined_29"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[1].get() == 1:
                main_ui.cw_set_instructor_list[1].config(text=inst, fg=theme.set_text_color)
                fields["Initials 2"] = instructor_list[set_inst]["Initials"]
                fields["undefined_35"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[2].get() == 1:
                main_ui.cw_set_instructor_list[2].config(text=inst, fg=theme.set_text_color)
                fields["Initials 3"] = instructor_list[set_inst]["Initials"]
                fields["undefined_41"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[3].get() == 1:
                main_ui.cw_set_instructor_list[3].config(text=inst, fg=theme.set_text_color)
                fields["Initials 4"] = instructor_list[set_inst]["Initials"]
                fields["undefined_47"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[4].get() == 1:
                main_ui.cw_set_instructor_list[4].config(text=inst, fg=theme.set_text_color)
                fields["DSD with all CW Dive 1 skills  Open Water Diver CW Dive 1"] = instructor_list[set_inst][
                    "Initials"]
                fields["undefined_55"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[5].get() == 1:
                main_ui.cw_set_instructor_list[5].config(text=inst, fg=theme.set_text_color)
                fields["200 metreyard Swim OR 300 metreyard MaskSnorkelFin Swim"] = instructor_list[set_inst][
                    "Initials"]
                fields["undefined_68"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[6].get() == 1:
                main_ui.cw_set_instructor_list[6].config(text=inst, fg=theme.set_text_color)
                fields["undefined_73"] = instructor_list[set_inst]["Initials"]
                fields["undefined_74"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[7].get() == 1:
                main_ui.cw_set_instructor_list[7].config(text=inst, fg=theme.set_text_color)
                fields["undefined_77"] = instructor_list[set_inst]["Initials"]
                fields["undefined_78"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[8].get() == 1:
                main_ui.cw_set_instructor_list[8].config(text=inst, fg=theme.set_text_color)
                fields["undefined_93"] = instructor_list[set_inst]["Initials"]
                fields["undefined_94"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[9].get() == 1:
                main_ui.cw_set_instructor_list[9].config(text=inst, fg=theme.set_text_color)
                fields["undefined_98"] = instructor_list[set_inst]["Initials"]
                fields["undefined_99"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[10].get() == 1:
                main_ui.cw_set_instructor_list[10].config(text=inst, fg=theme.set_text_color)
                fields["undefined_104"] = instructor_list[set_inst]["Initials"]
                fields["undefined_101"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[11].get() == 1:
                main_ui.cw_set_instructor_list[11].config(text=inst, fg=theme.set_text_color)
                fields["undefined_105"] = instructor_list[set_inst]["Initials"]
                fields["undefined_106"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[12].get() == 1:
                main_ui.cw_set_instructor_list[12].config(text=inst, fg=theme.set_text_color)
                fields["undefined_119"] = instructor_list[set_inst]["Initials"]
                fields["undefined_120"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[13].get() == 1:
                main_ui.cw_set_instructor_list[13].config(text=inst, fg=theme.set_text_color)
                fields["undefined_124"] = instructor_list[set_inst]["Initials"]
                fields["undefined_125"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.cw_switch_list[14].get() == 1:
                main_ui.cw_set_instructor_list[14].config(text=inst, fg=theme.set_text_color)
                fields["PADI"] = instructor_list[set_inst]["PADI Number"]

            if main_ui.kd_switch_list[0].get() == 1:
                main_ui.kd_set_instructor_list[0].config(text=inst, fg=theme.set_text_color)
                fields["undefined_33"] = instructor_list[set_inst]["Initials"]
                fields["undefined_34"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.kd_switch_list[1].get() == 1:
                main_ui.kd_set_instructor_list[1].config(text=inst, fg=theme.set_text_color)
                fields["undefined_39"] = instructor_list[set_inst]["Initials"]
                fields["undefined_40"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.kd_switch_list[2].get() == 1:
                main_ui.kd_set_instructor_list[2].config(text=inst, fg=theme.set_text_color)
                fields["undefined_45"] = instructor_list[set_inst]["Initials"]
                fields["undefined_46"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.kd_switch_list[3].get() == 1:
                main_ui.kd_set_instructor_list[3].config(text=inst, fg=theme.set_text_color)
                fields["undefined_51"] = instructor_list[set_inst]["Initials"]
                fields["undefined_52"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.kd_switch_list[4].get() == 1:
                main_ui.kd_set_instructor_list[4].config(text=inst, fg=theme.set_text_color)
                fields["undefined_59"] = instructor_list[set_inst]["Initials"]
                fields["undefined_60"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.kd_switch_list[5].get() == 1:
                main_ui.kd_set_instructor_list[5].config(text=inst, fg=theme.set_text_color)
                fields["undefined_64"] = instructor_list[set_inst]["Initials"]
                fields["undefined_65"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.kd_switch_list[6].get() == 1:
                main_ui.kd_set_instructor_list[6].config(text=inst, fg=theme.set_text_color)
                fields["undefined_69"] = instructor_list[set_inst]["PADI Number"]

            if main_ui.ow_switch_list[0].get() == 1:
                main_ui.ow_set_instructor_list[0].config(text=inst, fg=theme.set_text_color)
                fields["Initials 1_2"] = instructor_list[set_inst]["Initials"]
                fields["undefined_86"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[1].get() == 1:
                main_ui.ow_set_instructor_list[1].config(text=inst, fg=theme.set_text_color)
                fields["Initials 2_2"] = instructor_list[set_inst]["Initials"]
                fields["undefined_81"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[2].get() == 1:
                main_ui.ow_set_instructor_list[2].config(text=inst, fg=theme.set_text_color)
                fields["Initials 1_3"] = instructor_list[set_inst]["Initials"]
                fields["undefined_89"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[3].get() == 1:
                main_ui.ow_set_instructor_list[3].config(text=inst, fg=theme.set_text_color)
                fields["Initials 2_3"] = instructor_list[set_inst]["Initials"]
                fields["undefined_90"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[4].get() == 1:
                main_ui.ow_set_instructor_list[4].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 1"] = instructor_list[set_inst]["Initials"]
                fields["undefined_109"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[5].get() == 1:
                main_ui.ow_set_instructor_list[5].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 2"] = instructor_list[set_inst]["Initials"]
                fields["undefined_110"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[6].get() == 1:
                main_ui.ow_set_instructor_list[6].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 3"] = instructor_list[set_inst]["Initials"]
                fields["undefined_111"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[7].get() == 1:
                main_ui.ow_set_instructor_list[7].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 4"] = instructor_list[set_inst]["Initials"]
                fields["undefined_112"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[8].get() == 1:
                main_ui.ow_set_instructor_list[8].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 5"] = instructor_list[set_inst]["Initials"]
                fields["undefined_113"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[9].get() == 1:
                main_ui.ow_set_instructor_list[9].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 6"] = instructor_list[set_inst]["Initials"]
                fields["undefined_114"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[10].get() == 1:
                main_ui.ow_set_instructor_list[10].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 7"] = instructor_list[set_inst]["Initials"]
                fields["undefined_115"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[11].get() == 1:
                main_ui.ow_set_instructor_list[11].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 8"] = instructor_list[set_inst]["Initials"]
                fields["undefined_116"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[12].get() == 1:
                main_ui.ow_set_instructor_list[12].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 9"] = instructor_list[set_inst]["Initials"]
                fields["undefined_117"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[13].get() == 1:
                main_ui.ow_set_instructor_list[13].config(text=inst, fg=theme.set_text_color)
                fields["Instructor Initials 10"] = instructor_list[set_inst]["Initials"]
                fields["undefined_121"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[14].get() == 1:
                main_ui.ow_set_instructor_list[14].config(text=inst, fg=theme.set_text_color)
                fields["undefined_126"] = instructor_list[set_inst]["PADI Number"]
            if main_ui.ow_switch_list[15].get() == 1:
                main_ui.ow_set_instructor_list[15].config(text=inst, fg=theme.set_text_color)
                fields["undefined_137"] = instructor_list[set_inst]["PADI Number"]

        else:  # --- User Enters Wrong Password
            pass_window.destroy()
            messagebox.showinfo("invalid password", "Wrong Password")

    # --- Password Submit Button
    pass_button = customtkinter.CTkButton(pass_frame, text="Submit", command=password_verify,
                                          fg_color=theme.main_button_color, text_color=theme.main_button_text_color,
                                          hover_color=theme.main_button_color_hover
                                          )

    pass_button.grid(column=1, row=1, pady=10, padx=10)


def set_date():
    """Add dates to 'field' dictionary and change 'Set Dive' Label to Calendar DateEntry"""

    # --- Confined Water Dives
    if main_ui.cw_switch_list[0].get() == 1:
        con_water_one_date = main_ui.cw_cal_list[0].get_date()
        main_ui.cw_set_date_list[0].config(text=con_water_one_date, fg=theme.set_text_color)
        fields["CW 1"] = con_water_one_date.day
        fields["undefined_27"] = con_water_one_date.month
        fields["undefined_28"] = con_water_one_date.year
    if main_ui.cw_switch_list[1].get() == 1:
        con_water_two_date = main_ui.cw_cal_list[1].get_date()
        main_ui.cw_set_date_list[1].config(text=con_water_two_date, fg=theme.set_text_color)
        fields["CW 2"] = con_water_two_date.day
        fields["undefined_21"] = con_water_two_date.month
        fields["undefined_22"] = con_water_two_date.year
    if main_ui.cw_switch_list[2].get() == 1:
        con_water_three_date = main_ui.cw_cal_list[2].get_date()
        main_ui.cw_set_date_list[2].config(text=con_water_three_date, fg=theme.set_text_color)
        fields["CW 3"] = con_water_three_date.day
        fields["undefined_23"] = con_water_three_date.month
        fields["undefined_24"] = con_water_three_date.year
    if main_ui.cw_switch_list[3].get() == 1:
        con_water_four_date = main_ui.cw_cal_list[3].get_date()
        main_ui.cw_set_date_list[3].config(text=con_water_four_date, fg=theme.set_text_color)
        fields["CW 4"] = con_water_four_date.day
        fields["undefined_25"] = con_water_four_date.month
        fields["undefined_26"] = con_water_four_date.year
    if main_ui.cw_switch_list[4].get() == 1:
        con_water_five_date = main_ui.cw_cal_list[4].get_date()
        main_ui.cw_set_date_list[4].config(text=con_water_five_date, fg=theme.set_text_color)
        fields["CW 5"] = con_water_five_date.day
        fields["undefined_53"] = con_water_five_date.month
        fields["undefined_54"] = con_water_five_date.year
    if main_ui.cw_switch_list[5].get() == 1:  # Swim
        swim_date = main_ui.cw_cal_list[5].get_date()
        main_ui.cw_set_date_list[5].config(text=swim_date, fg=theme.set_text_color)
        fields["10 Minute Survival Float"] = swim_date.day
        fields["undefined_66"] = swim_date.month
        fields["undefined_67"] = swim_date.year
    if main_ui.cw_switch_list[6].get() == 1:  # Float
        float_date = main_ui.cw_cal_list[6].get_date()
        main_ui.cw_set_date_list[6].config(text=float_date, fg=theme.set_text_color)
        fields["undefined_75"] = float_date.day
        fields["undefined_76"] = float_date.month
        fields["undefined_72"] = float_date.year
    if main_ui.cw_switch_list[7].get() == 1:
        equip_date = main_ui.cw_cal_list[7].get_date()
        main_ui.cw_set_date_list[7].config(text=equip_date, fg=theme.set_text_color)
        fields["Equipment Preparation and Care"] = equip_date.day
        fields["undefined_91"] = equip_date.month
        fields["undefined_92"] = equip_date.year
    if main_ui.cw_switch_list[8].get() == 1:
        disconnect_date = main_ui.cw_cal_list[8].get_date()
        main_ui.cw_set_date_list[8].config(text=disconnect_date, fg=theme.set_text_color)
        fields["Disconnect Low Pressure Inflator Hose"] = disconnect_date.day
        fields["undefined_95"] = disconnect_date.month
        fields["undefined_96"] = disconnect_date.year
    if main_ui.cw_switch_list[9].get() == 1:
        loose_date = main_ui.cw_cal_list[9].get_date()
        main_ui.cw_set_date_list[9].config(text=loose_date, fg=theme.set_text_color)
        fields["Loose Cylinder Band"] = loose_date.day
        fields["undefined_100"] = loose_date.month
        fields["undefined_97"] = loose_date.year
    if main_ui.cw_switch_list[10].get() == 1:
        weight_date = main_ui.cw_cal_list[10].get_date()
        main_ui.cw_set_date_list[10].config(text=weight_date, fg=theme.set_text_color)
        fields["Weight System Removal and Replacement surface"] = weight_date.day
        fields["undefined_102"] = weight_date.month
        fields["undefined_103"] = weight_date.year
    if main_ui.cw_switch_list[11].get() == 1:
        weight_drop_date = main_ui.cw_cal_list[11].get_date()
        main_ui.cw_set_date_list[11].config(text=weight_drop_date, fg=theme.set_text_color)
        fields["Emergency Weight Drop or in OW"] = weight_drop_date.day
        fields["undefined_107"] = weight_drop_date.month
        fields["undefined_108"] = weight_drop_date.year
    if main_ui.cw_switch_list[12].get() == 1:
        skin_diving_date = main_ui.cw_cal_list[12].get_date()
        main_ui.cw_set_date_list[12].config(text=skin_diving_date, fg=theme.set_text_color)
        fields["Skin Diving Skills"] = skin_diving_date.day
        fields["undefined_122"] = skin_diving_date.month
        fields["undefined_118"] = skin_diving_date.year
    if main_ui.cw_switch_list[13].get() == 1:
        drysuit_orientation_date = main_ui.cw_cal_list[13].get_date()
        main_ui.cw_set_date_list[13].config(text=drysuit_orientation_date, fg=theme.set_text_color)
        fields[
            "Note If all Confined Water Dives Confined Water Dive Flexible Skills and Wa"] = drysuit_orientation_date.day
        fields["undefined_129"] = drysuit_orientation_date.month
        fields["undefined_123"] = drysuit_orientation_date.year
    if main_ui.cw_switch_list[14].get() == 1:
        confined_water_signoff_date = main_ui.cw_cal_list[14].get_date()
        main_ui.cw_set_date_list[14].config(text=confined_water_signoff_date, fg=theme.set_text_color)
        fields["Date_6"] = confined_water_signoff_date.day
        fields["undefined_132"] = confined_water_signoff_date.month
        fields["undefined_133"] = confined_water_signoff_date.year
    # --- Knowledge Development

    if main_ui.kd_switch_list[0].get() == 1:
        kr1_date = main_ui.kd_cal_list[0].get_date()
        main_ui.kd_set_date_list[0].config(text=kr1_date, fg=theme.set_text_color)
        fields["Section 1"] = kr1_date.day
        fields["undefined_30"] = kr1_date.month
        fields["undefined_31"] = kr1_date.year
    if main_ui.kd_switch_list[1].get() == 1:
        kr2_date = main_ui.kd_cal_list[1].get_date()
        main_ui.kd_set_date_list[1].config(text=kr2_date, fg=theme.set_text_color)
        fields["Section 2"] = kr2_date.day
        fields["undefined_36"] = kr2_date.month
        fields["undefined_37"] = kr2_date.year
    if main_ui.kd_switch_list[2].get() == 1:
        kr3_date = main_ui.kd_cal_list[2].get_date()
        main_ui.kd_set_date_list[2].config(text=kr3_date, fg=theme.set_text_color)
        fields["Section 3"] = kr3_date.day
        fields["undefined_42"] = kr3_date.month
        fields["undefined_43"] = kr3_date.year
    if main_ui.kd_switch_list[3].get() == 1:
        kr4_date = main_ui.kd_cal_list[3].get_date()
        main_ui.kd_set_date_list[3].config(text=kr4_date, fg=theme.set_text_color)
        fields["Section 4"] = kr4_date.day
        fields["undefined_48"] = kr4_date.month
        fields["undefined_49"] = kr4_date.year
    if main_ui.kd_switch_list[4].get() == 1:
        kr5_date = main_ui.kd_cal_list[4].get_date()
        main_ui.kd_set_date_list[4].config(text=kr5_date, fg=theme.set_text_color)
        fields["Section 5"] = kr5_date.day
        fields["undefined_56"] = kr5_date.month
        fields["undefined_57"] = kr5_date.year
    if main_ui.kd_switch_list[5].get() == 1:
        or_elearning_date = main_ui.kd_cal_list[5].get_date()
        main_ui.kd_set_date_list[5].config(text=or_elearning_date, fg=theme.set_text_color)
        fields["Quick Review"] = or_elearning_date.day
        fields["undefined_61"] = or_elearning_date.month
        fields["undefined_62"] = or_elearning_date.year
    if main_ui.kd_switch_list[6].get() == 1:
        all_knowledge_date = main_ui.kd_cal_list[5].get_date()
        main_ui.kd_set_date_list[6].config(text=all_knowledge_date, fg=theme.set_text_color)
        fields["Date_3"] = all_knowledge_date.day
        fields["undefined_70"] = all_knowledge_date.month
        fields["undefined_71"] = all_knowledge_date.year

    # --- Open Water Dives
    if main_ui.ow_switch_list[0].get() == 1:
        ow1_date = main_ui.ow_cal_list[0].get_date()
        main_ui.ow_set_date_list[0].config(text=ow1_date, fg=theme.set_text_color)
        fields["Dive 1"] = ow1_date.day
        fields["undefined_84"] = ow1_date.month
        fields["undefined_85"] = ow1_date.year
    if main_ui.ow_switch_list[1].get() == 1:
        ow2_date = main_ui.ow_cal_list[1].get_date()
        main_ui.ow_set_date_list[1].config(text=ow2_date, fg=theme.set_text_color)
        fields["Dive 2"] = ow2_date.day
        fields["undefined_79"] = ow2_date.month
        fields["undefined_80"] = ow2_date.year
    if main_ui.ow_switch_list[2].get() == 1:
        ow3_date = main_ui.ow_cal_list[2].get_date()
        main_ui.ow_set_date_list[2].config(text=ow3_date, fg=theme.set_text_color)
        fields["Dive 3"] = ow3_date.day
        fields["undefined_87"] = ow3_date.month
        fields["undefined_88"] = ow3_date.year
    if main_ui.ow_switch_list[3].get() == 1:
        ow4_date = main_ui.ow_cal_list[3].get_date()
        main_ui.ow_set_date_list[3].config(text=ow4_date, fg=theme.set_text_color)
        fields["Dive 4"] = ow4_date.day
        fields["undefined_82"] = ow4_date.month
        fields["undefined_83"] = ow4_date.year

    # --- Open Water Flexible Skills
    for entry_box_num in range(len(main_ui.ow_flex_dive_list)):  # this is a fix to get placeholder text
        main_ui.ow_flex_dive_list[entry_box_num]._placeholder_text_active = False

    if main_ui.ow_switch_list[4].get() == 1:
        main_ui.ow_set_date_list[4].config(text=main_ui.ow_flex_dive_list[0].get(), fg=theme.set_text_color)
        fields["Dive_9"] = main_ui.ow_flex_dive_list[0].get()
    if main_ui.ow_switch_list[5].get() == 1:
        main_ui.ow_set_date_list[5].config(text=main_ui.ow_flex_dive_list[1].get(), fg=theme.set_text_color)
        fields["Dive"] = main_ui.ow_flex_dive_list[1].get()
    if main_ui.ow_switch_list[6].get() == 1:
        main_ui.ow_set_date_list[6].config(text=main_ui.ow_flex_dive_list[2].get(), fg=theme.set_text_color)
        fields["Dive_2"] = main_ui.ow_flex_dive_list[2].get()
    if main_ui.ow_switch_list[7].get() == 1:
        main_ui.ow_set_date_list[7].config(text=main_ui.ow_flex_dive_list[3].get(), fg=theme.set_text_color)
        fields["Dive_3"] = main_ui.ow_flex_dive_list[3].get()
    if main_ui.ow_switch_list[8].get() == 1:
        main_ui.ow_set_date_list[8].config(text=main_ui.ow_flex_dive_list[4].get(), fg=theme.set_text_color)
        fields["Dive_4"] = main_ui.ow_flex_dive_list[4].get()
    if main_ui.ow_switch_list[9].get() == 1:
        main_ui.ow_set_date_list[9].config(text=main_ui.ow_flex_dive_list[5].get(), fg=theme.set_text_color)
        fields["Dive_5"] = main_ui.ow_flex_dive_list[5].get()
    if main_ui.ow_switch_list[10].get() == 1:
        main_ui.ow_set_date_list[10].config(text=main_ui.ow_flex_dive_list[6].get(), fg=theme.set_text_color)
        fields["Dive_6"] = main_ui.ow_flex_dive_list[6].get()
    if main_ui.ow_switch_list[11].get() == 1:
        main_ui.ow_set_date_list[11].config(text=main_ui.ow_flex_dive_list[7].get(), fg=theme.set_text_color)
        fields["Dive_7"] = main_ui.ow_flex_dive_list[7].get()
    if main_ui.ow_switch_list[12].get() == 1:
        main_ui.ow_set_date_list[12].config(text=main_ui.ow_flex_dive_list[8].get(), fg=theme.set_text_color)
        fields["Dive_8"] = main_ui.ow_flex_dive_list[8].get()
    if main_ui.ow_switch_list[13].get() == 1:
        main_ui.ow_set_date_list[13].config(text=main_ui.ow_flex_dive_list[9].get(), fg=theme.set_text_color)
        fields["Dive_10"] = main_ui.ow_flex_dive_list[9].get()
    if main_ui.ow_switch_list[14].get() == 1:
        all_ow_flex_dives_date = main_ui.ow_cal_list[4].get_date()
        main_ui.ow_set_date_list[14].config(text=all_ow_flex_dives_date, fg=theme.set_text_color)
        fields["Date_4"] = all_ow_flex_dives_date.day
        fields["undefined_127"] = all_ow_flex_dives_date.month
        fields["undefined_128"] = all_ow_flex_dives_date.year
    if main_ui.ow_switch_list[15].get() == 1:
        all_cert_requirements_date = main_ui.ow_cal_list[5].get_date()
        main_ui.ow_set_date_list[15].config(text=all_cert_requirements_date, fg=theme.set_text_color)
        fields["Date_8"] = all_cert_requirements_date.day
        fields["undefined_138"] = all_cert_requirements_date.month
        fields["undefined_139"] = all_cert_requirements_date.year


def generate_pdf(input_path: str):
    """Functions to write 'fields' dictionary to fill 'Record_and_Referral_form' pdf."""
    # input_path = "Record_and_Referral_Form.pdf"
    student_file_name = fields["Student Name"]

    # --- if checkbox are True update 'fields' dictionary
    if main_ui.rdp_check.get() == 1:
        fields["Check Box24"] = "Yes"
    if main_ui.erdpml_check.get() == 1:
        fields["Check Box23"] = "Yes"
    if main_ui.computer_check.get() == 1:
        fields["Check Box22"] = "Yes"
    if main_ui.kr_checkbox_list[0].get() == 1:
        fields["Check Box25"] = "Yes"
    if main_ui.kr_checkbox_list[1].get() == 1:
        fields["Check Box27"] = "Yes"
    if main_ui.kr_checkbox_list[2].get() == 1:
        fields["Check Box29"] = "Yes"
    if main_ui.kr_checkbox_list[3].get() == 1:
        fields["Check Box31"] = "Yes"
    if main_ui.kr_checkbox_list[4].get() == 1:
        fields["Check Box33"] = "Yes"
    if main_ui.kr_checkbox_list[5].get() == 1:
        fields["Check Box35"] = "Yes"
    if main_ui.kd_video_checkbox_list[0].get() == 1:
        fields["Check Box26"] = "Yes"
    if main_ui.kd_video_checkbox_list[0].get() == 1:
        fields["Check Box28"] = "Yes"
    if main_ui.kd_video_checkbox_list[0].get() == 1:
        fields["Check Box30"] = "Yes"
    if main_ui.kd_video_checkbox_list[0].get() == 1:
        fields["Check Box32"] = "Yes"
    if main_ui.kd_video_checkbox_list[0].get() == 1:
        fields["Check Box34"] = "Yes"
    if main_ui.kd_video_checkbox_list[0].get() == 1:
        fields["Check Box36"] = "Yes"

    # --- Get string inputs from Knowledge Development Entries and update 'fields' dictionary

    for entry_box_num in range(len(main_ui.kd_exam_entry_list)):  # this is a fix to get placeholder text
        main_ui.kd_exam_entry_list[entry_box_num]._placeholder_text_active = False

    fields["undefined_32"] = main_ui.kd_exam_entry_list[0].get()
    fields["undefined_38"] = main_ui.kd_exam_entry_list[1].get()
    fields["undefined_44"] = main_ui.kd_exam_entry_list[2].get()
    fields["undefined_50"] = main_ui.kd_exam_entry_list[3].get()
    fields["undefined_58"] = main_ui.kd_exam_entry_list[4].get()
    fields["undefined_63"] = main_ui.kd_exam_entry_list[5].get()

    # --- Save pdf file name

    save_path = config["save path"]["student_record_path"]
    output_path = f"{save_path}/{student_file_name}_Student_Record_Form_{today.day}_{today.month}_{today.year}.pdf"
    # --- Write pdf
    try:
        fillpdfs.write_fillable_pdf(input_path, output_path, fields)
    except FileNotFoundError:
        messagebox.showerror(message="File path not found. Choose new file path")


def new_student(ui: object):
    """Allow users to add Student Diver Information"""
    student_window = Toplevel(ui)
    student_window.geometry(f"{600}x{600}")
    student_window.title("Instructor Paperwork Assistant")
    student_window.config(pady=20, padx=20, background=theme.background_color)
    student_window.iconbitmap("assets/logo.ico")

    student_window.grid_rowconfigure(1, weight=1)
    student_window.grid_columnconfigure(0, weight=1)
    student_frame = customtkinter.CTkFrame(student_window, fg_color=theme.frame_color)
    student_frame.grid(row=1, column=0, columnspan=3, rowspan=10, padx=40, pady=(0, 40), sticky="nsew")
    student_frame.grid_columnconfigure(2, weight=1)
    student_frame.grid_columnconfigure(0, weight=1)
    student_frame.grid_columnconfigure(1, weight=1)
    student_info_label = tkinter.Label(student_window, text="Add Student Information", font=TITLE_HEADER_FONT,
                                       background=theme.background_color)
    student_info_label.grid(row=0, column=0, sticky="sw", padx=40)

    student_f_name_label = tkinter.Label(student_frame, text="First Name:", background=theme.frame_color,
                                         font=STANDARD_FONT)
    student_f_name_label.grid(column=0, row=0, sticky="e", pady=(30, 0), padx=2)
    student_f_name_entry = customtkinter.CTkEntry(student_frame, width=30, height=25,
                                                  text_color=theme.text_color,
                                                  fg_color=theme.listbox_color,
                                                  border_color=theme.main_button_color)
    student_f_name_entry.grid(column=1, row=0, columnspan=3, padx=(0, 30), pady=(30, 2), sticky="ew")

    student_l_name_label = tkinter.Label(student_frame, text="Last Name:", background=theme.frame_color,
                                         font=STANDARD_FONT)
    student_l_name_label.grid(column=0, row=1, sticky="e", pady=2)
    student_l_name_entry = customtkinter.CTkEntry(student_frame, width=30, height=25,
                                                  text_color=theme.text_color,
                                                  fg_color=theme.listbox_color,
                                                  border_color=theme.main_button_color)
    student_l_name_entry.grid(column=1, row=1, columnspan=3, padx=(0, 30), pady=(2), sticky="ew")

    dob_label = tkinter.Label(student_frame, text="DOB: (DD/MM/YYYY)", background=theme.frame_color, font=STANDARD_FONT)
    dob_label.grid(column=0, row=2, sticky="e", padx=(30, 0))
    dob_entry = customtkinter.CTkEntry(student_frame, width=15, height=25,
                                       text_color=theme.text_color,
                                       fg_color=theme.listbox_color,
                                       border_color=theme.main_button_color)
    dob_entry.grid(column=1, row=2, sticky="ew", pady=2)

    student_email_label = tkinter.Label(student_frame, text="Email:", background=theme.frame_color, font=STANDARD_FONT)
    student_email_label.grid(row=3, column=0, sticky="e")
    student_email_entry = customtkinter.CTkEntry(student_frame, width=30, height=25,
                                                 text_color=theme.text_color,
                                                 fg_color=theme.listbox_color,
                                                 border_color=theme.main_button_color)
    student_email_entry.grid(row=3, column=1, columnspan=3, sticky="ew", padx=(0, 30), pady=2)
    student_phone_label = tkinter.Label(student_frame, text="Phone:", background=theme.frame_color, font=STANDARD_FONT)
    student_phone_label.grid(row=4, column=0, sticky="e", pady=5)
    student_phone_entry = customtkinter.CTkEntry(student_frame, width=30, height=25,
                                                 text_color=theme.text_color,
                                                 fg_color=theme.listbox_color,
                                                 border_color=theme.main_button_color)
    student_phone_entry.grid(row=4, column=1, columnspan=3, padx=(0, 30), sticky="ew")

    sex_label = tkinter.Label(student_frame, text="Sex", padx=1, background=theme.frame_color, font=STANDARD_FONT)
    sex_label.grid(row=5, column=0, sticky="e")
    sex_check_var = tkinter.IntVar()
    sex_radio_male = tkinter.Radiobutton(student_frame, text="Male", variable=sex_check_var, value=1,
                                         background=theme.frame_color, font=STANDARD_FONT)
    sex_radio_male.grid(row=5, column=1, sticky="w", padx=(10, 0))
    sex_radio_female = tkinter.Radiobutton(student_frame, text="Female", variable=sex_check_var, value=2,
                                           background=theme.frame_color, font=STANDARD_FONT)
    sex_radio_female.grid(row=6, column=1, sticky="w", padx=(10, 0))
    mailing_label = tkinter.Label(student_frame, text="Mailing Address", background=theme.frame_color,
                                  font=STANDARD_FONT)
    mailing_label.grid(row=7, column=0, sticky="e", pady=(20, 5))
    street_label = tkinter.Label(student_frame, text="Street:", background=theme.frame_color, font=STANDARD_FONT)
    street_label.grid(row=8, column=0, sticky="e", pady=2)
    street_entry = customtkinter.CTkEntry(student_frame, width=30, height=25,
                                          text_color=theme.text_color,
                                          fg_color=theme.listbox_color,
                                          border_color=theme.main_button_color)
    street_entry.grid(row=8, column=1, columnspan=3, padx=(0, 30), sticky="ew", pady=2)
    city_label = tkinter.Label(student_frame, text="City:", background=theme.frame_color, font=STANDARD_FONT)
    city_label.grid(row=9, column=0, sticky="e")
    city_entry = customtkinter.CTkEntry(student_frame, height=25,
                                        text_color=theme.text_color,
                                        fg_color=theme.listbox_color,
                                        border_color=theme.main_button_color)
    city_entry.grid(row=9, column=1, sticky="ew", pady=2)
    province_label = tkinter.Label(student_frame, text="Province:", background=theme.frame_color, font=STANDARD_FONT)
    province_label.grid(row=10, column=0, sticky="e")
    province_entry = customtkinter.CTkEntry(student_frame, height=25,
                                            text_color=theme.text_color,
                                            fg_color=theme.listbox_color,
                                            border_color=theme.main_button_color)
    province_entry.grid(row=10, column=1, sticky="ew", pady=2)
    country_label = tkinter.Label(student_frame, text="Country:", background=theme.frame_color, font=STANDARD_FONT)
    country_label.grid(row=11, column=0, sticky="e")
    country_entry = customtkinter.CTkEntry(student_frame, height=25,
                                           text_color=theme.text_color,
                                           fg_color=theme.listbox_color,
                                           border_color=theme.main_button_color)
    country_entry.grid(row=11, column=1, sticky="ew", pady=2)
    postal_label = tkinter.Label(student_frame, text="Postal:", background=theme.frame_color, font=STANDARD_FONT)
    postal_label.grid(row=12, column=0, sticky="e")
    postal_entry = customtkinter.CTkEntry(student_frame, height=25,
                                          text_color=theme.text_color,
                                          fg_color=theme.listbox_color,
                                          border_color=theme.main_button_color)
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

        main_ui.list_box_student.insert("end", f"{student_f_name_entry.get()} {student_l_name_entry.get()}")

        student_dict_global.update(new_student_data)
        student_window.destroy()

    # --- Add Student Button
    student_button = customtkinter.CTkButton(student_frame, text="Add Student", command=update_student,
                                             fg_color=theme.main_button_color, text_color=theme.main_button_text_color,
                                             hover_color=theme.main_button_color_hover
                                             )
    student_button.grid(column=2, row=13, columnspan=3, sticky="e", pady=30, padx=30)


def update_instructor_menu():
    """update instructor option menu"""
    with open(INSTRUCTOR_DATA, "r") as inst:
        instructor_info = json.load(inst)
    instructor_list_menu = []

    for instructor in instructor_info.keys():
        instructor_list_menu.append(instructor)

    main_ui.list_box.configure(values=instructor_list_menu)


# @speed_calc_decorator
def new_instructor(ui):
    """Allows users to add a New Instructor"""
    # instructor_window = customtkinter.CTk()
    instructor_window = Toplevel(ui)
    instructor_window.geometry("700x500")
    instructor_window.title("Add Instructor Information")
    instructor_window.iconbitmap("assets/logo.ico")

    instructor_window.config(pady=50, padx=50, background=theme.background_color)
    instructor_window.grid_columnconfigure(0, weight=1)

    add_instructor_label = tkinter.Label(instructor_window, text="Add Instructor", font=TITLE_HEADER_FONT,
                                         background=theme.background_color)
    add_instructor_label.grid(row=0, column=0, sticky="w", padx=10)

    instructor_frame = customtkinter.CTkFrame(instructor_window, fg_color=theme.frame_color)
    instructor_frame.grid(row=1, column=0, ipadx=20)
    instructor_frame.grid_columnconfigure(0, weight=1)

    instructor_name_label = tkinter.Label(instructor_frame, text="PADI Instructor:", font=STANDARD_FONT,
                                          background=theme.frame_color)
    instructor_name_label.grid(column=0, row=0, sticky="e", pady=(20, 2))
    instructor_name_entry = customtkinter.CTkEntry(instructor_frame, height=25,
                                                   text_color=theme.text_color,
                                                   fg_color=theme.listbox_color,
                                                   border_color=theme.main_button_color)
    instructor_name_entry.grid(column=1, row=0, columnspan=2, sticky="ew", pady=(20, 2))
    initials_label = tkinter.Label(instructor_frame, text="Initials", font=STANDARD_FONT, background=theme.frame_color)
    initials_label.grid(column=0, row=1, sticky="e", pady=2)
    initials_entry = customtkinter.CTkEntry(instructor_frame, height=25,
                                            text_color=theme.text_color,
                                            fg_color=theme.listbox_color,
                                            border_color=theme.main_button_color)
    initials_entry.grid(column=1, row=1, sticky="ew", pady=2)
    padi_number_label = tkinter.Label(instructor_frame, text="PADI Number:", font=STANDARD_FONT,
                                      background=theme.frame_color)
    padi_number_label.grid(row=3, column=0, sticky="e", pady=2)
    padi_number_entry = customtkinter.CTkEntry(instructor_frame, height=25,
                                               text_color=theme.text_color,
                                               fg_color=theme.listbox_color,
                                               border_color=theme.main_button_color)
    padi_number_entry.grid(row=3, column=1, sticky="ew", pady=2)
    store_number_label = tkinter.Label(instructor_frame, text="PADI Store Number s-:", font=STANDARD_FONT,
                                       background=theme.frame_color)
    store_number_label.grid(row=4, column=0, sticky="e", pady=2)
    store_number_entry = customtkinter.CTkEntry(instructor_frame, height=25,
                                                text_color=theme.text_color,
                                                fg_color=theme.listbox_color,
                                                border_color=theme.main_button_color)
    store_number_entry.grid(row=4, column=1, sticky="ew", pady=2)
    phone_label = tkinter.Label(instructor_frame, text="Phone:", font=STANDARD_FONT, background=theme.frame_color)
    phone_label.grid(row=5, column=0, sticky="e", pady=2)
    phone_entry = customtkinter.CTkEntry(instructor_frame, height=25,
                                         text_color=theme.text_color,
                                         fg_color=theme.listbox_color,
                                         border_color=theme.main_button_color)
    phone_entry.grid(row=5, column=1, columnspan=2, sticky="ew", pady=2)
    instructor_email_label = tkinter.Label(instructor_frame, text="Email:", font=STANDARD_FONT,
                                           background=theme.frame_color)
    instructor_email_label.grid(row=6, column=0, sticky="e", pady=2)
    instructor_email_entry = customtkinter.CTkEntry(instructor_frame, height=25,
                                                    text_color=theme.text_color,
                                                    fg_color=theme.listbox_color,
                                                    border_color=theme.main_button_color)
    instructor_email_entry.grid(row=6, column=1, columnspan=2, sticky="ew", pady=2)
    instructor_password_label = tkinter.Label(instructor_frame, text="Password:", font=STANDARD_FONT,
                                              background=theme.frame_color)
    instructor_password_label.grid(row=7, column=0, sticky="e", pady=2)
    instructor_password_entry = customtkinter.CTkEntry(instructor_frame, show="*", height=25,
                                                       text_color=theme.text_color,
                                                       fg_color=theme.listbox_color,
                                                       border_color=theme.main_button_color)
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
            with open(INSTRUCTOR_DATA, "r") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            with open(INSTRUCTOR_DATA, "w") as data_file:
                json.dump(new_data, data_file, indent=4)
        else:
            data.update(new_data)
            with open(INSTRUCTOR_DATA, "w") as data_file:
                json.dump(data, data_file, indent=4)

        # --- Refresher Instructor Listbox
        try:
            with open(INSTRUCTOR_DATA, "r") as data_file:
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
                                              fg_color=theme.switch_off_color,
                                              progress_color=theme.switch_on_color,
                                              button_hover_color=theme.switch_hover_color,
                                              button_color=theme.switch_button_color)
    password_switch.select()
    password_switch.grid(row=7, column=3, sticky="ew", padx=(5, 20))

    # --- Add Instructor Button
    instructor_button = customtkinter.CTkButton(instructor_frame, text="Add Instructor",
                                                fg_color=theme.main_button_color,
                                                text_color=theme.main_button_text_color,
                                                hover_color=theme.main_button_color_hover,
                                                command=update_instructor)
    instructor_button.grid(column=2, row=8, pady=(20))


def remove_inst(deleted_instructor):
    """delete selected instructor"""
    with open(INSTRUCTOR_DATA, "r") as data:
        inst_info = json.load(data)
        del inst_info[deleted_instructor]

    with open(INSTRUCTOR_DATA, "w") as data:
        json.dump(inst_info, data, indent=4)

    main_ui.list_box.set("")
    update_instructor_menu()


def set_student():
    """Update 'fields' dictionary and "Set Instructor" label with student info."""
    index = main_ui.list_box_student.curselection()
    global student_dict_global
    student = main_ui.list_box_student.get(index)
    main_ui.student_set_label.configure(text=student, fg=theme.set_text_color)
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
    if main_ui.cw_switch_list[0].get() == 1:
        for switches in main_ui.cw_switch_list:
            switches.deselect()

    else:
        for switches in main_ui.cw_switch_list:
            switches.select()


def select_all_kd():
    """Toggle all Knowledge Development Checkboxes"""
    if main_ui.kd_switch_list[0].get() == 1:
        for switches in main_ui.kd_switch_list:
            switches.deselect()
        for kr in main_ui.kr_checkbox_list:
            kr.deselect()
        for video in main_ui.kd_video_checkbox_list:
            video.deselect()
    else:
        for switches in main_ui.kd_switch_list:
            switches.select()
        for kr in main_ui.kr_checkbox_list:
            kr.select()
        for video in main_ui.kd_video_checkbox_list:
            video.select()


def select_all_ow():
    """Toggle all Open Water Checkboxes"""
    if main_ui.ow_switch_list[0].get() == 1:
        for switches in main_ui.ow_switch_list:
            switches.deselect()
    else:
        for switches in main_ui.ow_switch_list:
            switches.select()


def select_all():
    """Toggle all switches and checkboxes"""
    select_all_cw()
    select_all_kd()
    select_all_ow()
    if main_ui.ow_switch_list[0].get() == 1:
        main_ui.select_all_button.configure(text="Unselect All")
        main_ui.main_switch_cw.select()
        main_ui.main_switch_kd.select()
        main_ui.main_switch_ow.select()
    else:
        main_ui.select_all_button.configure(text="Select All")
        main_ui.main_switch_cw.deselect()
        main_ui.main_switch_kd.deselect()
        main_ui.main_switch_ow.deselect()
        main_ui.rdp_check.deselect()
        main_ui.erdpml_check.deselect()
        main_ui.computer_check.deselect()


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
        with open("/config/config.ini", "w") as path:
            config.write(path)


def import_student():
    """read excel file and import student data"""
    student_path = filedialog.askopenfilename()
    try:
        student_data = pandas.read_excel(student_path)
    except ValueError:
        messagebox.showerror(message="wrong file type. Support for excel files only")

    student_dict = student_data.to_dict(orient="records")

    # try:
    #     for info in student_dict:
    #         full_name = f"{info['first_name']} {info['last_name']}"
    #         new_student_data = {
    #             full_name: {
    #                 'first_name': info['first_name'],
    #                 'last_name': info['last_name'],
    #                 'date_of_birth': info["date_of_birth"],
    #                 'sex': info['sex'],
    #                 'phone': info['phone'],
    #                 'email': info['email'],
    #                 'street_address': info['street_address'],
    #                 'city': info['city'],
    #                 'province': info['province'],
    #                 'postal': info['postal'],
    #                 'country': info['country'],
    #             }
    #         }
    #         student_dict_global.update(new_student_data)
    #         main_ui.list_box_student.insert("end", full_name)
    # except KeyError:
    #     messagebox.showerror(message="incorrect file format.  See help 'importing student data")

    # TODO complete student dataclass refactor
    # student data class refactor

    try:
        student_dataclass_list = []
        for info in student_dict:
            imported_student_data = Student(
                first_name=info['first_name'],
                last_name=info['last_name'],
                date_of_birth=info["date_of_birth"],
                sex=info['sex'],
                phone=info['phone'],
                email=info['email'],
                street_address=info['street_address'],
                city=info['city'],
                province=info['province'],
                postal=info['postal'],
                country=info['country'],
            )
            student_dataclass_list.append(imported_student_data)
            main_ui.list_box_student.insert("end", f"{imported_student_data.first_name} "
                                                   f"{imported_student_data.last_name}")

        # for students in student_dataclass_list:
        #     print(students.first_name)
        #     print(students.last_name)
        #     print(students.date_of_birth)
        #     print(students.sex)
        #     print(students.phone)
        #     print(students.email)
        #     print(students.street_address)
        #     print(students.city)
        #     print(students.province)
        #     print(students.postal)
        #     print(students.country)

    except Exception as e:
        print(e)


def refresher_main_combobox():
    with open(DIVE_TEMPLATE_DATA, "r") as data:
        template = json.load(data)

    key_list = []

    for temps in template.keys():
        key_list.append(temps)

    main_ui.date_rule_box.configure(values=key_list)


def clear_dict_values():
    """clears dictionary fields for pdf form"""
    global fields
    fields = fillpdfs.get_form_fields("assets/Record_and_Referral_Form.pdf")


def reset_all():
    """resets main UI"""
    [set_date.configure(text="Set Date", fg=theme.reset_main_text_color) for set_date in main_ui.cw_set_date_list]
    [set_date.configure(text="Set Date", fg=theme.reset_main_text_color) for set_date in main_ui.kd_set_date_list]
    [set_date.configure(text="Set Date", fg=theme.reset_main_text_color) for set_date in main_ui.ow_set_date_list]
    [set_inst.configure(text="Set Instructor", fg=theme.reset_main_text_color) for set_inst in
     main_ui.cw_set_instructor_list]
    [set_inst.configure(text="Set Instructor", fg=theme.reset_main_text_color) for set_inst in
     main_ui.kd_set_instructor_list]
    [set_inst.configure(text="Set Instructor", fg=theme.reset_main_text_color) for set_inst in
     main_ui.ow_set_instructor_list]
    [quiz.delete(0, "end") for quiz in main_ui.kd_exam_entry_list]
    [flex.delete(0, "end") for flex in main_ui.ow_flex_dive_list]
    [flex.configure(placeholder_text="") for flex in main_ui.ow_flex_dive_list]
    [switches.select() for switches in main_ui.cw_switch_list]
    [switches.select() for switches in main_ui.kd_switch_list]
    [switches.select() for switches in main_ui.ow_switch_list]
    main_ui.main_switch_ow.select()
    main_ui.main_switch_cw.select()
    main_ui.main_switch_kd.select()
    [kr_check.select() for kr_check in main_ui.kr_checkbox_list]
    [vid_check.select() for vid_check in main_ui.kd_video_checkbox_list]
    main_ui.rdp_check.deselect()
    main_ui.erdpml_check.deselect()
    main_ui.computer_check.deselect()
    [cw_dates.set_date(today) for cw_dates in main_ui.cw_cal_list]
    [kd_dates.set_date(today) for kd_dates in main_ui.kd_cal_list]
    [ow_dates.set_date(today) for ow_dates in main_ui.ow_cal_list]
    main_ui.student_set_label.config(text="Set Student", font=TITLE_HEADER_FONT, background=theme.frame_color,
                                     fg=theme.reset_main_text_color)
    clear_dict_values()


def report_bug():
    """email support 'brendan.development@pm.me'"""
    webbrowser.open("mailto:brendan.development@pm.me")


# --------------------------- MAIN UI SETUP ------------------------------ #
class MainUI(customtkinter.CTk):
    def __init__(self, confined_water_labels: list, knowledge_development_labels: list, open_water_labels: list, theme):
        super().__init__()
        self.config(pady=(20), padx=30,
                    bg=theme.background_color)
        self.title("Instructor Assistant")
        self.geometry(f"{1750}x{970}+100+0")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.iconbitmap("assets/logo.ico")
        # self._set_appearance_mode("system")
        # --- Student Listbox
        self.student_lb_frame = customtkinter.CTkFrame(master=self, fg_color=theme.frame_color, corner_radius=8,
                                                       bg_color=theme.background_color)
        self.student_lb_frame.grid(row=0, column=0, pady=10, ipadx=10, ipady=10, sticky="nsew", padx=10)
        self.student_lb_frame.grid_columnconfigure(0, weight=1)
        self.student_label = tkinter.Label(self.student_lb_frame, text="Student Diver:", bg=theme.frame_color,
                                           font=TITLE_HEADER_FONT)
        self.student_label.grid(row=0, column=0, sticky="w", padx=(20, 0), pady=(5, 0))
        self.student_set_label = tkinter.Label(self.student_lb_frame, text="Set Student", bg=theme.frame_color,
                                               font=TITLE_HEADER_FONT)
        self.student_set_label.grid(row=0, column=0, columnspan=2, padx=(80, 0), pady=(5, 0))
        self.list_box_student = tkinter.Listbox(self.student_lb_frame, bg=theme.listbox_color,
                                                font=STANDARD_FONT)
        self.list_box_student.grid(row=1, column=0, rowspan=3, columnspan=2, padx=(20, 30), pady=(10, 0), sticky="ew")
        self.add_student = customtkinter.CTkButton(self.student_lb_frame, text="Add Student",
                                                   command=lambda: new_student(self),
                                                   fg_color=theme.main_button_color,
                                                   text_color=theme.main_button_text_color,
                                                   hover_color=theme.main_button_color_hover)
        self.add_student.grid(row=1, column=2, padx=(0, 30))
        self.set_student = customtkinter.CTkButton(self.student_lb_frame, text="Set Student",
                                                   command=set_student,
                                                   fg_color=theme.main_button_color,
                                                   text_color=theme.main_button_text_color,
                                                   hover_color=theme.main_button_color_hover)
        self.set_student.grid(row=2, column=2, padx=(0, 30))
        self.import_student = customtkinter.CTkButton(self.student_lb_frame, text="Import Student",
                                                      command=import_student,
                                                      fg_color=theme.main_button_color,
                                                      text_color=theme.main_button_text_color,
                                                      hover_color=theme.main_button_color_hover)
        self.import_student.grid(row=3, column=2, padx=(0, 30))

        # --- Instructor Option Menu
        self.instructor_lb_frame = customtkinter.CTkFrame(master=self, fg_color=theme.frame_color, corner_radius=8,
                                                          bg_color=theme.background_color)
        self.instructor_lb_frame.grid(row=1, column=0, rowspan=1, sticky="nsew", padx=10, pady=10, ipadx=10, ipady=10)
        self.instructor_lb_frame.grid_columnconfigure(0, weight=1)
        self.instructor_label = tkinter.Label(self.instructor_lb_frame, text="PADI Instructor:", bg=theme.frame_color,
                                              font=TITLE_HEADER_FONT)
        self.instructor_label.grid(row=0, column=0, sticky="w", padx=(20, 0))

        # --- Import Instructor information from .json
        self.instructor_list_menu = []
        try:
            with open(INSTRUCTOR_DATA, "r") as data_file:
                instructor_info = json.load(data_file)
                for instructor in instructor_info.keys():  # update list box
                    self.instructor_list_menu.append(instructor)
        except FileNotFoundError:
            print("No Instructor File Found")

        self.list_box = customtkinter.CTkOptionMenu(self.instructor_lb_frame, values=self.instructor_list_menu,
                                                    width=155,
                                                    fg_color=theme.background_color,
                                                    text_color=theme.text_color,
                                                    button_color=theme.main_button_color,
                                                    button_hover_color=theme.main_button_color_hover,
                                                    dropdown_fg_color=theme.background_color,
                                                    dropdown_text_color=theme.text_color,
                                                    dropdown_hover_color=theme.frame_color
                                                    )
        self.list_box.grid(row=0, column=1, padx=(0, 80), pady=20)
        self.add_inst_button = customtkinter.CTkButton(self.instructor_lb_frame, text="Add Instructor",
                                                       command=lambda: new_instructor(self),
                                                       fg_color=theme.main_button_color,
                                                       text_color=theme.main_button_text_color,
                                                       hover_color=theme.main_button_color_hover)
        self.add_inst_button.grid(row=0, column=2, padx=(0, 30))
        self.set_inst_button = customtkinter.CTkButton(self.instructor_lb_frame, text="Set Instructor",
                                                       command=lambda: set_instructor(self),
                                                       fg_color=theme.main_button_color,
                                                       text_color=theme.main_button_text_color,
                                                       hover_color=theme.main_button_color_hover)
        self.set_inst_button.grid(row=1, column=1, padx=(0, 80))
        self.del_inst_button = customtkinter.CTkButton(self.instructor_lb_frame, text="Delete Instructor",
                                                       command=lambda: remove_inst(self.list_box.get()),
                                                       fg_color=theme.main_button_color,
                                                       text_color=theme.main_button_text_color,
                                                       hover_color=theme.main_button_color_hover)
        self.del_inst_button.grid(row=1, column=2, padx=(0, 30))

        # --------------------------- CONFINED WATER ------------------------ #

        self.confined_water_frame = customtkinter.CTkFrame(self, fg_color=theme.frame_color, corner_radius=8,
                                                           bg_color=theme.background_color)
        self.confined_water_frame.grid(column=0, row=2, padx=10, pady=10, sticky="nsew", ipadx=10, ipady=10)

        self.confined_water_frame.grid_columnconfigure(4, weight=1)
        self.confined_water_frame.grid_columnconfigure(2, weight=1)

        self.main_switch_cw = customtkinter.CTkSwitch(self.confined_water_frame, text="",
                                                      command=select_all_cw,
                                                      fg_color=theme.master_switch_off_color,
                                                      progress_color=theme.master_switch_on_color,
                                                      button_hover_color=theme.master_switch_hover_color,
                                                      button_color=theme.master_switch_button_color,
                                                      width=65)
        self.main_switch_cw.select()
        self.main_switch_cw.grid(row=0, column=3, columnspan=2, stick="w")

        # Confined Water Labels
        self.confined_water_section = tkinter.Label(self.confined_water_frame, text="Confined Water",
                                                    bg=theme.frame_color,
                                                    font=TITLE_HEADER_FONT)
        self.confined_water_section.grid(row=0, column=0, pady=10)

        for cw_l in range(15):
            cw_label = tkinter.Label(self.confined_water_frame, text=confined_water_labels[cw_l], bg=theme.frame_color,
                                     font=STANDARD_FONT)
            cw_label.grid(row=cw_l + 1, column=0, padx=(20, 0), pady=2, sticky="e")

        # Confined Water Calendar
        self.cw_cal_list = []
        for cw_c in range(15):
            cw_cal = DateEntry(self.confined_water_frame, selectmode="day", font=STANDARD_FONT)
            cw_cal.grid(row=cw_c + 1, column=1, padx=5)
            self.cw_cal_list.append(cw_cal)

        # Confined Water Set Instructor Label
        self.cw_set_instructor_list = []
        for cw_inst in range(15):
            cw_set_inst = tkinter.Label(self.confined_water_frame, text="Set Instructor", bg=theme.frame_color,
                                        font=STANDARD_FONT)
            cw_set_inst.grid(row=cw_inst + 1, column=2, padx=10)
            self.cw_set_instructor_list.append(cw_set_inst)

        # Confined Water Set Date Labels
        self.cw_set_date_list = []
        for cw_date in range(15):
            cw_set_date = tkinter.Label(self.confined_water_frame, text="Set Date", bg=theme.frame_color,
                                        font=STANDARD_FONT)
            cw_set_date.grid(row=cw_date + 1, column=4, padx=(0, 30), sticky="w")
            self.cw_set_date_list.append(cw_set_date)

        # Confined Water Switches
        self.cw_switch_list = []
        for cw_switch in range(15):
            cw_main_switch = customtkinter.CTkSwitch(self.confined_water_frame, text="",
                                                     fg_color=theme.switch_off_color,
                                                     progress_color=theme.switch_on_color,
                                                     button_hover_color=theme.switch_hover_color,
                                                     button_color=theme.switch_button_color,
                                                     width=65
                                                     )
            cw_main_switch.grid(row=cw_switch + 1, column=3)
            cw_main_switch.select()
            self.cw_switch_list.append(cw_main_switch)

        # --------------------------- KNOWLEDGE DEVELOPMENT ----------------- #

        self.knowledge_development_frame = customtkinter.CTkFrame(self, fg_color=theme.frame_color,
                                                                  corner_radius=8, bg_color=theme.background_color)
        self.knowledge_development_frame.grid(row=0, column=1, rowspan=2, padx=20, pady=10, sticky="nsew", columnspan=2,
                                              ipadx=10,
                                              ipady=10)

        # self.knowledge_development_frame.grid_columnconfigure(2, weight=1)
        # self.knowledge_development_frame.grid_columnconfigure(4, weight=1)

        self.knowledge_development_section = tkinter.Label(self.knowledge_development_frame,
                                                           text="Knowledge Development",
                                                           bg=theme.frame_color,
                                                           font=TITLE_HEADER_FONT)
        self.knowledge_development_section.grid(row=0, column=0, sticky="w", pady=10, padx=(20, 0), columnspan=2)

        self.main_switch_kd = customtkinter.CTkSwitch(self.knowledge_development_frame, text="",
                                                      command=select_all_kd,
                                                      fg_color=theme.master_switch_off_color,
                                                      progress_color=theme.master_switch_on_color,
                                                      button_color=theme.master_switch_button_color,
                                                      button_hover_color=theme.master_switch_hover_color,
                                                      width=65
                                                      )
        self.main_switch_kd.select()
        self.main_switch_kd.grid(row=2, column=3, )

        # --- RDP or eRDPml or Computer
        self.course_option_label = tkinter.Label(self.knowledge_development_frame, text="Course Option:",
                                                 bg=theme.frame_color,
                                                 font=STANDARD_FONT, )
        self.course_option_label.grid(row=1, column=3, pady=(0, 10))
        self.rdp_check = customtkinter.CTkCheckBox(self.knowledge_development_frame, text="RDP", checkbox_width=20,
                                                   checkbox_height=20,
                                                   fg_color=theme.switch_on_color,
                                                   hover_color=theme.switch_hover_color,
                                                   border_color=theme.switch_on_color,
                                                   text_color=theme.text_color
                                                   )

        self.rdp_check.grid(row=1, column=5, pady=(0, 10))

        self.erdpml_check = customtkinter.CTkCheckBox(self.knowledge_development_frame, text="eRDPml",
                                                      checkbox_width=20,
                                                      checkbox_height=20,
                                                      fg_color=theme.switch_on_color,
                                                      hover_color=theme.switch_hover_color,
                                                      border_color=theme.switch_on_color,
                                                      text_color=theme.text_color
                                                      )
        self.erdpml_check.grid(row=1, column=6, pady=(0, 10))

        self.computer_check = customtkinter.CTkCheckBox(self.knowledge_development_frame, text="Computer",
                                                        checkbox_width=20,
                                                        checkbox_height=20,
                                                        fg_color=theme.switch_on_color,
                                                        hover_color=theme.switch_hover_color,
                                                        border_color=theme.switch_on_color,
                                                        text_color=theme.text_color
                                                        )
        self.computer_check.grid(row=1, column=7, pady=(0, 10))
        self.kr_complete = tkinter.Label(self.knowledge_development_frame, text="Knowledge", bg=theme.frame_color,
                                         font=STANDARD_FONT)
        self.kr_complete.grid(row=2, column=4, padx=(0, 5), columnspan=2)
        self.pass_exam = tkinter.Label(self.knowledge_development_frame, text="Quiz/Exam", bg=theme.frame_color,
                                       font=STANDARD_FONT)
        self.pass_exam.grid(row=2, column=5, columnspan=2, padx=(15, 0))
        self.video_complete = tkinter.Label(self.knowledge_development_frame, text="Video", bg=theme.frame_color,
                                            font=STANDARD_FONT)
        self.video_complete.grid(row=2, column=6, columnspan=2, padx=(20, 0))

        # Knowledge Development string
        for kd_s in range(7):
            kd_string = tkinter.Label(self.knowledge_development_frame, text=knowledge_development_labels[kd_s],
                                      font=STANDARD_FONT, background=theme.frame_color)
            kd_string.grid(row=kd_s + 3, column=0, padx=(50, 0), pady=2, sticky="e")

        # Knowledge Development Calendar
        self.kd_cal_list = []
        for kd_c in range(7):
            kd_cal = DateEntry(self.knowledge_development_frame, selectmode="day", font=STANDARD_FONT)
            kd_cal.grid(row=kd_c + 3, column=1, padx=7, pady=2)
            self.kd_cal_list.append(kd_cal)

        # Knowledge Development Set Instructor Label
        self.kd_set_instructor_list = []
        for kd_inst in range(7):
            kd_set_inst = tkinter.Label(self.knowledge_development_frame, text="Set Instructor", bg=theme.frame_color,
                                        font=STANDARD_FONT)
            kd_set_inst.grid(row=kd_inst + 3, column=2, padx=20)
            self.kd_set_instructor_list.append(kd_set_inst)

        # Knowledge Development Set Date Labels
        self.kd_set_date_list = []
        for kd_date in range(7):
            kd_set_date = tkinter.Label(self.knowledge_development_frame, text="Set Date", bg=theme.frame_color,
                                        font=STANDARD_FONT)
            kd_set_date.grid(row=kd_date + 3, column=4, padx=(0, 20))
            self.kd_set_date_list.append(kd_set_date)

        # Knowledge Development Switches
        self.kd_switch_list = []
        for kd_switch in range(7):
            kd_main_switch = customtkinter.CTkSwitch(self.knowledge_development_frame, text="",
                                                     fg_color=theme.switch_off_color,
                                                     progress_color=theme.switch_on_color,
                                                     button_hover_color=theme.switch_hover_color,
                                                     button_color=theme.switch_button_color,
                                                     width=65
                                                     )
            kd_main_switch.grid(row=kd_switch + 3, column=3)
            kd_main_switch.select()
            self.kd_switch_list.append(kd_main_switch)

        # --- Knowledge Quiz/Exam Checkbox
        self.kr_checkbox_list = []
        for kd_box in range(7):
            kd_check_box = customtkinter.CTkCheckBox(self.knowledge_development_frame, text="", checkbox_width=20,
                                                     checkbox_height=20,
                                                     fg_color=theme.switch_on_color,
                                                     hover_color=theme.switch_hover_color,
                                                     border_color=theme.switch_on_color,

                                                     )
            kd_check_box.grid(row=kd_box + 3, column=5, padx=(5, 0))
            kd_check_box.select()
            self.kr_checkbox_list.append(kd_check_box)

        self.kd_video_checkbox_list = []
        for kd_vid in range(7):
            kd_vid_box = customtkinter.CTkCheckBox(self.knowledge_development_frame, text="", checkbox_width=20,
                                                   checkbox_height=20,
                                                   fg_color=theme.switch_on_color,
                                                   hover_color=theme.switch_hover_color,
                                                   border_color=theme.switch_on_color,

                                                   )

            kd_vid_box.grid(row=kd_vid + 3, column=7, padx=(0, 5))
            kd_vid_box.select()
            self.kd_video_checkbox_list.append(kd_vid_box)

        self.kd_exam_entry_list = []
        for kd_exam in range(6):
            kd_exam_entry = customtkinter.CTkEntry(self.knowledge_development_frame, width=70, height=25,
                                                   text_color=theme.text_color,
                                                   fg_color=theme.listbox_color,
                                                   border_color=theme.main_button_color,
                                                   )
            kd_exam_entry.grid(row=kd_exam + 3, column=5, columnspan=2, padx=(25, 5))
            self.kd_exam_entry_list.append(kd_exam_entry)

        # --------------------------- OPEN WATER FLEX ENTRY ----------------- #

        self.open_water_frame = customtkinter.CTkFrame(self, fg_color=theme.frame_color,
                                                       corner_radius=8, bg_color=theme.background_color)
        self.open_water_frame.grid(column=1, row=2, rowspan=1, stick="nsew", padx=(20, 10), pady=10, ipadx=10, ipady=10)

        # self.open_water_frame.grid_columnconfigure(4, weight=1)
        # self.open_water_frame.grid_columnconfigure(2, weight=1)

        self.open_water_section = tkinter.Label(self.open_water_frame, text="Open Water", bg=theme.frame_color,
                                                font=TITLE_HEADER_FONT)
        self.open_water_section.grid(row=0, column=0, sticky="w", pady=10, padx=(40, 0), columnspan=2)

        # Main Switch
        self.main_switch_ow = customtkinter.CTkSwitch(self.open_water_frame, text="",
                                                      command=select_all_ow,
                                                      fg_color=theme.master_switch_off_color,
                                                      progress_color=theme.master_switch_on_color,
                                                      button_color=theme.master_switch_button_color,
                                                      button_hover_color=theme.master_switch_hover_color,
                                                      width=65
                                                      )
        self.main_switch_ow.select()
        self.main_switch_ow.grid(row=0, column=3, columnspan=1)

        for ow_s in range(16):
            ow_string = tkinter.Label(self.open_water_frame, text=open_water_labels[ow_s], font=STANDARD_FONT,
                                      background=theme.frame_color)
            ow_string.grid(row=ow_s + 1, column=0, padx=(40, 0), sticky="e", pady=2)

        self.ow_cal_list = []
        for ow_c in range(16):
            if 3 < ow_c < 14:
                pass
            else:
                ow_cal = DateEntry(self.open_water_frame, selectmode="day", font=STANDARD_FONT)
                ow_cal.grid(row=ow_c + 1, column=1, padx=5)
                self.ow_cal_list.append(ow_cal)

        # Open Water Set Instructor Label
        self.ow_set_instructor_list = []
        for ow_inst in range(16):
            ow_set_inst = tkinter.Label(self.open_water_frame, text="Set Instructor", bg=theme.frame_color,
                                        font=STANDARD_FONT)
            ow_set_inst.grid(row=ow_inst + 1, column=2, padx=20)
            self.ow_set_instructor_list.append(ow_set_inst)

        # Open Water Set Date Labels
        self.ow_set_date_list = []
        for ow_date in range(16):
            ow_set_date = tkinter.Label(self.open_water_frame, text="Set Date", bg=theme.frame_color,
                                        font=STANDARD_FONT)
            ow_set_date.grid(row=ow_date + 1, column=4)
            self.ow_set_date_list.append(ow_set_date)

        # Open Water Switches
        self.ow_switch_list = []
        for ow_switch in range(16):
            ow_main_switch = customtkinter.CTkSwitch(self.open_water_frame, text="",
                                                     fg_color=theme.switch_off_color,
                                                     progress_color=theme.switch_on_color,
                                                     button_hover_color=theme.switch_hover_color,
                                                     button_color=theme.switch_button_color,
                                                     width=65
                                                     )
            ow_main_switch.grid(row=ow_switch + 1, column=3, padx=(15, 10))
            ow_main_switch.select()
            self.ow_switch_list.append(ow_main_switch)

        # Dive flex entry boxes
        self.ow_flex_dive_list = []
        for flex_c in range(16):
            if 3 < flex_c < 14:
                flex_cal = customtkinter.CTkEntry(self.open_water_frame, width=40, height=15,
                                                  text_color=theme.text_color,
                                                  fg_color=theme.listbox_color,
                                                  border_color=theme.main_button_color)

                flex_cal.grid(row=flex_c + 1, column=1, padx=5)
                self.ow_flex_dive_list.append(flex_cal)

        # --------------------------- RIGHT BUTTON MENU ------------------------- #

        self.right_frame = customtkinter.CTkFrame(self, fg_color=theme.frame_color, corner_radius=8,
                                                  bg_color=theme.background_color)
        self.right_frame.grid(row=2, column=2, sticky="nsew", padx=(10, 20), pady=10, )

        self.choose_template_label = tkinter.Label(self.right_frame, text="Choose Template:", font=STANDARD_FONT,
                                                   bg=theme.frame_color)
        self.choose_template_label.grid(row=0, column=0, pady=(20, 5))

        key_list = []
        try:
            with open(DIVE_TEMPLATE_DATA, "r") as data_file:
                data = json.load(data_file)
                for keys in data.keys():
                    key_list.append(keys)

        except FileNotFoundError:
            print("template file no found")

        self.date_rule_box = customtkinter.CTkOptionMenu(self.right_frame, values=key_list, width=155,
                                                         fg_color=theme.background_color,
                                                         text_color=theme.text_color,
                                                         button_color=theme.main_button_color,
                                                         button_hover_color=theme.main_button_color_hover,
                                                         dropdown_fg_color=theme.background_color,
                                                         dropdown_text_color=theme.text_color,
                                                         dropdown_hover_color=theme.frame_color
                                                         )
        self.date_rule_box.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.set_date_rule_button = customtkinter.CTkButton(self.right_frame, text="Set Template",
                                                            command=execute_template,
                                                            fg_color=theme.main_button_color,
                                                            text_color=theme.main_button_text_color,
                                                            hover_color=theme.main_button_color_hover)
        self.set_date_rule_button.grid(row=2, column=0, pady=(5, 10))

        self.set_date_button = customtkinter.CTkButton(self.right_frame, text="New Template",
                                                       command=lambda: new_template(self),
                                                       fg_color=theme.main_button_color,
                                                       text_color=theme.main_button_text_color,
                                                       hover_color=theme.main_button_color_hover)
        self.set_date_button.grid(row=3, column=0, pady=(0, 70))

        self.set_date_button = customtkinter.CTkButton(self.right_frame, text="Set Date/Dive",
                                                       command=set_date,
                                                       fg_color=theme.main_button_color,
                                                       text_color=theme.main_button_text_color,
                                                       hover_color=theme.main_button_color_hover)
        self.set_date_button.grid(row=4, column=0, pady=(0, 10))

        self.refresh_main = customtkinter.CTkButton(master=self.right_frame, text="Reset All",
                                                    command=reset_all,
                                                    fg_color=theme.main_button_color,
                                                    text_color=theme.main_button_text_color,
                                                    hover_color=theme.main_button_color_hover)
        self.refresh_main.grid(row=5, column=0, pady=(0, 10))

        self.select_all_button = customtkinter.CTkButton(master=self.right_frame, text="Unselect All",
                                                         command=select_all,
                                                         fg_color=theme.main_button_color,
                                                         text_color=theme.main_button_text_color,
                                                         hover_color=theme.main_button_color_hover)
        self.select_all_button.grid(row=6, column=0, pady=(0, 10))

        self.select_elearning_button = customtkinter.CTkButton(master=self.right_frame, text="Elearning",
                                                               command=or_elearning_select,
                                                               fg_color=theme.main_button_color,
                                                               text_color=theme.main_button_text_color,
                                                               hover_color=theme.main_button_color_hover)
        self.select_elearning_button.grid(row=7, column=0, pady=(0, 70))

        self.gen_pfd_button = customtkinter.CTkButton(self.right_frame, text="Generate PDF",
                                                      command=lambda: generate_pdf(STUDENT_AND_REFERRAL_FORM),
                                                      fg_color=theme.main_button_color,
                                                      text_color=theme.main_button_text_color,
                                                      hover_color=theme.main_button_color_hover)
        self.gen_pfd_button.grid(row=8, column=0)

        # --------------------------- FILE MENU ----------------------------- #

        self.menubar = Menu(self)
        # --- Adding File Menu and commands
        self.file = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=self.file)
        self.file.add_command(label='Start New',
                              command=reset_all
                              )
        self.file.add_separator()
        self.file.add_command(label='Exit', command=self.destroy)
        # --- Adding Edit Menu and commands
        self.edit = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Edit', menu=self.edit)
        self.edit.add_command(label='Choose PDF Save Path',
                              command=choose_save_path
                              )
        # self.edit.add_command(label='New Template',
        #                       command=new_template
        #                       )
        # - add themes in future
        # --- Settings
        # settings = Menu(menubar, tearoff=False)
        # menubar.add_cascade(label="Settings", menu=settings)
        # sub_menu = Menu(settings, tearoff=False)
        # sub_menu.add_command(label='Light', command=lambda: theme_update("light_theme"))
        # sub_menu.add_command(label='Sea', command=lambda: theme_update("sea_theme"))
        # settings.add_cascade(label='Theme', menu=sub_menu)
        # --- Adding Help Menu
        self.help_ = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Help', menu=self.help_)
        self.help_.add_command(label='Report a Issue', command=report_bug)
        self.help_.add_separator()
        self.help_.add_command(label='About Instructor Assistant',
                               command=lambda: webbrowser.open("https://github.com/BAndresen/instructor_assistant"))

        # --- Display Menu
        self.config(menu=self.menubar)


if __name__ == "__main__":
    with open("config/themes.json", "r") as file:
        theme_dict = json.load(file)
    # Configure file path for completed pdf

    config = configparser.ConfigParser()
    config.read("config/config.ini")
    config_theme = config["style"]["theme"]

    if config["new_user"].getboolean("new_user"):
        default_desktop_save_path = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")
        config["save path"]["student_record_path"] = default_desktop_save_path
        config["new_user"]["new_user"] = "False"

    with open("config/config.ini", "w") as configfile:
        config.write(configfile)

    # pdf fields
    with open("config/pdf_form_fields.json") as data:
        fields = json.load(data)

    theme = Theme(config_theme, theme_dict)
    main_ui = MainUI(CONFINED_WATER_LABELS, KNOWLEDGE_DEVELOPMENT_LABELS, OPEN_WATER_LABELS, theme)

    main_ui.mainloop()
