#newmain

import cv2
import numpy as np
from anomalib.deploy import OpenVINOInferencer
from pathlib import Path
from PIL import Image, ImageTk
from anomalib.visualization import ImageVisualizer
import json
import cv2
import customtkinter as ctk
import os
from tkinter import filedialog
from datetime import datetime
import csv
import threading
from backend.autoInspect import AutoInspector
from backend.autoInspect2 import AutoInspector2
from backend.autoInspect3 import AutoInspector3
import time
from watchdog.observers import Observer
from backend.watchdog_handleroriginal import AOIWatchdogHandler
import shutil


import sys
from backend.plc import SLMP_PLC
from tkinter import messagebox

class ColorPalette:
    DARK = {
        
        "primary": "#0C2D88",
        "primary_dark": "#4797bdfb",
        "background": "#3395b3",
        "surface": "#BFDAE7",
        #"surface": "#D6EBF1",
        "card": "#E5E8E9",
        "accent": "#5FC7F7",
        "accent_soft": "#5A93A3",
        #"accent_soft": "#A5D8E8",
        "text_primary": "#362C08",
        "text_secondary": "#4B6B73",
        "text_muted": "#8DAAB2",
        "success": "#349407",
        "warning": "#D1E65A",
        "error": "#D63912",
        "border": "#0C2D88"

    }
    DASHBOARD = {
        
        "primary": "#9e905c",
        "primary_light": "#e3d9b3",
        "primary_dark": "#807345",
        "background": "#b0a992",
        "surface": "#011E5E",
        "card": "#2C5D8B",
        "accent": "#D4689A",
        "accent_soft": "#121524",
        "text_primary": "#CBD7DF",
        "text_secondary": "#4B6B73",
        "text_muted": "#8DAAB2",
        "success": "#7FB069",
        "warning": "#F4A261",
        "error": "#E76F51"
    
    }
    @classmethod
    def current_theme(cls):
        return cls.DARK


class AnomalibDetection(ctk.CTk):
    def __init__(self):

        self.theme = ColorPalette.current_theme()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.title("PMX AI AOI")
        self.root.geometry("1590x890")

        self.file_name = datetime.now().strftime('%m-%d-%Y')
        with open(self.file_name, mode="w", newline="") as file:
            writer=csv.writer(file)
            writer.writerow(["ISN", "score_WCon", "score_C1", "score_C2", "resultWCon", "resultC1", "resultC2", "Overall_res"])
        
        #self.start_time = datetime.now()
        self.setup_gui()
        self.root.mainloop()
        self.is_scanning_online = False

    def setup_gui(self):
        self.main_frame = ctk.CTkScrollableFrame(self.root, corner_radius=10, fg_color=self.theme["accent_soft"])
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.upper_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color=self.theme["surface"],  border_color=self.theme["border"], border_width=2)
        self.upper_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.title_label = ctk.CTkLabel(self.upper_frame, text="AIAOI-Anomaly Detection", font=ctk.CTkFont(size=24, weight="bold"),text_color=self.theme["border"] )
        self.title_label.pack(side="left", padx=20, pady=15)

        self.tab_frame = ctk.CTkTabview(self.main_frame, fg_color=self.theme["surface"], border_width=2, border_color=self.theme["border"], corner_radius=15, )
        self.tab_frame.pack(pady=10, padx=10, fill="both", expand=True)


        tab_j7 = self.tab_frame.add("1")
        tab_cool1 = self.tab_frame.add("2")
        tab_cool2 = self.tab_frame.add("3")
        tab_main = self.tab_frame.add("Main")
        tab_config = self.tab_frame.add("Configuration")
        

        with open("config.json", "r") as f:
            self.config = json.load(f)
        try:
            self.puertoPLC = self.config["PLC_PORT"]
        except ValueError:
            messagebox.showerror("Error", "Error PLC_PORT must be an integer number")
            return
        self.IP_PLC = self.config["PLC_IP"]
        self.myPLC = SLMP_PLC(self.IP_PLC, int(self.puertoPLC))   

    #J7 TAB

        left_panel1 = ctk.CTkFrame(tab_j7, corner_radius=15,fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"])
        left_panel1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, rowspan=7)
        left_panel1.grid_rowconfigure((0,1), weight=1)
        left_panel1.grid_columnconfigure((0,1), weight=1)
        
        panel_score = ctk.CTkFrame(tab_j7, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_score.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        panel_score.grid_rowconfigure((0,1), weight=1)
        panel_score.grid_columnconfigure((0,1), weight=1)

        panel_isn = ctk.CTkFrame(tab_j7, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_isn.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
        panel_isn.grid_rowconfigure((0,1), weight=1)
        panel_isn.grid_columnconfigure((0,1), weight=1)

        panel_rgb = ctk.CTkFrame(tab_j7, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_rgb.grid(row=5, column=1, sticky="nsew", padx=10, pady=10)
        panel_rgb.grid_rowconfigure((0,1), weight=1)
        panel_rgb.grid_columnconfigure((0,1), weight=1)

        label_result1 = ctk.CTkLabel(tab_j7, text="Result:", font=("Arial", 16)).grid(row=0, column=2, pady=10, padx=10)
        self.button_res1 = ctk.CTkButton(tab_j7, text="", width=90, height=80, fg_color="gray", state=ctk.DISABLED,  border_width=2, border_color=self.theme["border"], corner_radius=30)
        self.button_res1.grid(row=0, column=3, pady=10, padx=10)

        space0 = ctk.CTkLabel(tab_j7, text="", font=("Arial", 20), height=20).grid(row=0, column=1) 

        score_label1 = ctk.CTkLabel(panel_score, text="Score:", font=("Arial", 16),text_color=self.theme["text_primary"])
        score_label1.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.scorebox = ctk.CTkTextbox(panel_score, width=180, height=40, fg_color=self.theme["surface"], corner_radius=10, border_width=2, border_color=self.theme["border"], state="disabled" )
        self.scorebox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space = ctk.CTkLabel(tab_j7, text="", font=("Arial", 20), height=60).grid(row=2, column=1)

        isn_label1 = ctk.CTkLabel(panel_isn, text="ISN:", font=("Arial", 16),text_color=self.theme["text_primary"])
        isn_label1.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.isnbox = ctk.CTkTextbox(panel_isn, width=180, height=40, fg_color=self.theme["surface"], corner_radius=10, border_width=2, border_color=self.theme["border"], state="disabled" )
        self.isnbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space1 = ctk.CTkLabel(tab_j7, text="", font=("Arial", 20), height=60).grid(row=4, column=1)

        bgr_label1 = ctk.CTkLabel(panel_rgb, text="RGB:", font=("Arial", 16),text_color=self.theme["text_primary"])
        bgr_label1.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.rgbbox = ctk.CTkTextbox(panel_rgb, width=180, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"], state="disabled" )
        self.rgbbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space2 = ctk.CTkLabel(tab_j7, text="", font=("Arial", 20), height=80).grid(row=6, column=1)


        self.canvas_width1 =int(self.screen_width*0.4)
        self.canvas_height1 = int(self.screen_height*0.27)
        self.canvas1 = ctk.CTkCanvas(left_panel1, width=self.canvas_width1, height=self.canvas_height1, bg=self.theme["card"], borderwidth=2)
        self.canvas1.grid(row=2, column=0, columnspan=2, sticky="s", padx=10, pady=10)

        self.canvas_width2 = int(self.screen_width*0.2)
        self.canvas_height2 = int(self.screen_height*0.27)
        self.canvas2 = ctk.CTkCanvas(left_panel1, width = self.canvas_width2, height=self.canvas_height2, bg=self.theme["card"])
        self.canvas2.grid(row=3, column=1, sticky="nsw", padx=20, pady=10)

    #COOL1 TAB

        left_panel2 = ctk.CTkFrame(tab_cool1, corner_radius=15,fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"])
        left_panel2.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, rowspan=7)
        left_panel2.grid_rowconfigure((0,1), weight=1)
        left_panel2.grid_columnconfigure((0,1), weight=1)
        
        panel_score2 = ctk.CTkFrame(tab_cool1, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_score2.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        panel_score2.grid_rowconfigure((0,1), weight=1)
        panel_score2.grid_columnconfigure((0,1), weight=1)

        panel_isn2 = ctk.CTkFrame(tab_cool1, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_isn2.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
        panel_isn2.grid_rowconfigure((0,1), weight=1)
        panel_isn2.grid_columnconfigure((0,1), weight=1)

        panel_rgb2 = ctk.CTkFrame(tab_cool1, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_rgb2.grid(row=5, column=1, sticky="nsew", padx=10, pady=10)
        panel_rgb2.grid_rowconfigure((0,1), weight=1)
        panel_rgb2.grid_columnconfigure((0,1), weight=1)

        label_result2 = ctk.CTkLabel(tab_cool1, text="Result:", font=("Arial", 16)).grid(row=0, column=2, pady=10, padx=10)
        self.button_res2 = ctk.CTkButton(tab_cool1, text="", width=90, height=80, fg_color="gray", state=ctk.DISABLED,  border_width=2, border_color=self.theme["border"], corner_radius=30)
        self.button_res2.grid(row=0, column=3, pady=10, padx=10)

        space01 = ctk.CTkLabel(tab_cool1, text="", font=("Arial", 20), height=20).grid(row=0, column=1) 

        score_label2 = ctk.CTkLabel(panel_score2, text="Score:", font=("Arial", 16),text_color=self.theme["text_primary"])
        score_label2.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.scorebox2 = ctk.CTkTextbox(panel_score2, width=180, height=40, fg_color=self.theme["surface"], corner_radius=10, border_width=2, border_color=self.theme["border"], state="disabled"  )
        self.scorebox2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space02 = ctk.CTkLabel(tab_cool1, text="", font=("Arial", 20), height=60).grid(row=2, column=1)

        isn_label2 = ctk.CTkLabel(panel_isn2, text="ISN:", font=("Arial", 16),text_color=self.theme["text_primary"])
        isn_label2.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.isnbox2 = ctk.CTkTextbox(panel_isn2, width=180, height=40, fg_color=self.theme["surface"], corner_radius=10, border_width=2, border_color=self.theme["border"], state="disabled" )
        self.isnbox2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space03 = ctk.CTkLabel(tab_cool1, text="", font=("Arial", 20), height=60).grid(row=4, column=1)

        bgr_label2 = ctk.CTkLabel(panel_rgb2, text="RGB:", font=("Arial", 16),text_color=self.theme["text_primary"])
        bgr_label2.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.isnbox2 = ctk.CTkTextbox(panel_rgb2, width=180, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"], state="disabled" )
        self.isnbox2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space04 = ctk.CTkLabel(tab_cool1, text="", font=("Arial", 20), height=80).grid(row=6, column=1)


        self.canvas_width3 =int(self.screen_width*0.4)
        self.canvas_height3 = int(self.screen_height*0.27)
        self.canvas3 = ctk.CTkCanvas(left_panel2, width=self.canvas_width3, height=self.canvas_height3, bg=self.theme["card"], borderwidth=2)
        self.canvas3.grid(row=2, column=0, columnspan=2, sticky="s", padx=10, pady=10)

        self.canvas_width4 = int(self.screen_width*0.2)
        self.canvas_height4 = int(self.screen_height*0.27)
        self.canvas4 = ctk.CTkCanvas(left_panel2, width = self.canvas_width4, height=self.canvas_height4, bg=self.theme["card"])
        self.canvas4.grid(row=3, column=1, sticky="nsw", padx=20, pady=10)

    #COOL2 TAB

        left_panel3 = ctk.CTkFrame(tab_cool2, corner_radius=15,fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"])
        left_panel3.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, rowspan=7)
        left_panel3.grid_rowconfigure((0,1), weight=1)
        left_panel3.grid_columnconfigure((0,1), weight=1)
        
        panel_score3 = ctk.CTkFrame(tab_cool2, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_score3.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        panel_score3.grid_rowconfigure((0,1), weight=1)
        panel_score3.grid_columnconfigure((0,1), weight=1)

        panel_isn3 = ctk.CTkFrame(tab_cool2, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_isn3.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
        panel_isn3.grid_rowconfigure((0,1), weight=1)
        panel_isn3.grid_columnconfigure((0,1), weight=1)

        panel_rgb3 = ctk.CTkFrame(tab_cool2, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_rgb3.grid(row=5, column=1, sticky="nsew", padx=10, pady=10)
        panel_rgb3.grid_rowconfigure((0,1), weight=1)
        panel_rgb3.grid_columnconfigure((0,1), weight=1)

        label_result3 = ctk.CTkLabel(tab_cool2, text="Result:", font=("Arial", 16)).grid(row=0, column=2, pady=10, padx=10)
        self.button_res3 = ctk.CTkButton(tab_cool2, text="", width=90, height=80, fg_color="gray", state=ctk.DISABLED,  border_width=2, border_color=self.theme["border"], corner_radius=30)
        self.button_res3.grid(row=0, column=3, pady=10, padx=10)

        space11 = ctk.CTkLabel(tab_cool2, text="", font=("Arial", 20), height=20).grid(row=0, column=1) 

        score_label3 = ctk.CTkLabel(panel_score3, text="Score:", font=("Arial", 16),text_color=self.theme["text_primary"])
        score_label3.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.scorebox3 = ctk.CTkTextbox(panel_score3, width=180, height=40, fg_color=self.theme["surface"], corner_radius=10, border_width=2, border_color=self.theme["border"] , state="disabled" )
        self.scorebox3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space12 = ctk.CTkLabel(tab_cool2, text="", font=("Arial", 20), height=60).grid(row=2, column=1)

        isn_label3 = ctk.CTkLabel(panel_isn3, text="ISN:", font=("Arial", 16),text_color=self.theme["text_primary"])
        isn_label3.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.isnbox3 = ctk.CTkTextbox(panel_isn3, width=180, height=40, fg_color=self.theme["surface"], corner_radius=10, border_width=2, border_color=self.theme["border"], state="disabled" )
        self.isnbox3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space13 = ctk.CTkLabel(tab_cool2, text="", font=("Arial", 20), height=60).grid(row=4, column=1)

        bgr_label3 = ctk.CTkLabel(panel_rgb3, text="RGB:", font=("Arial", 16),text_color=self.theme["text_primary"])
        bgr_label3.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nw")
        self.isnbox3 = ctk.CTkTextbox(panel_rgb3, width=180, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"], state="disabled" )
        self.isnbox3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        space04 = ctk.CTkLabel(tab_cool2, text="", font=("Arial", 20), height=80).grid(row=6, column=1)


        self.canvas_width5 =int(self.screen_width*0.4)
        self.canvas_height5 = int(self.screen_height*0.27)
        self.canvas5 = ctk.CTkCanvas(left_panel3, width=self.canvas_width5, height=self.canvas_height5, bg=self.theme["card"], borderwidth=2)
        self.canvas5.grid(row=2, column=0, columnspan=2, sticky="s", padx=10, pady=10)

        self.canvas_width6 = int(self.screen_width*0.2)
        self.canvas_height6 = int(self.screen_height*0.27)
        self.canvas6 = ctk.CTkCanvas(left_panel3, width = self.canvas_width6, height=self.canvas_height6, bg=self.theme["card"])
        self.canvas6.grid(row=3, column=1, sticky="nsw", padx=20, pady=10)

    #MAIN TAB

        canvas1_panel = ctk.CTkFrame(tab_main, corner_radius=15,fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"])
        canvas1_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        canvas1_panel.grid_rowconfigure((0,1), weight=1)
        canvas1_panel.grid_columnconfigure((0,1), weight=1)

        canvas2_panel = ctk.CTkFrame(tab_main, corner_radius=15,fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"])
        canvas2_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        canvas2_panel.grid_rowconfigure((0,1), weight=1)
        canvas2_panel.grid_columnconfigure((0,1), weight=1)

        canvas3_panel = ctk.CTkFrame(tab_main, corner_radius=15,fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"])
        canvas3_panel.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        canvas3_panel.grid_rowconfigure((0,1), weight=1)
        canvas3_panel.grid_columnconfigure((0,1), weight=1)
        
        panel_score4 = ctk.CTkFrame(tab_main, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_score4.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        panel_score4.grid_rowconfigure((0,1), weight=1)
        panel_score4.grid_columnconfigure((0,1), weight=1)

        panel_score5 = ctk.CTkFrame(tab_main, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_score5.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        panel_score5.grid_rowconfigure((0,1), weight=1)
        panel_score5.grid_columnconfigure((0,1), weight=1)

        panel_score6 = ctk.CTkFrame(tab_main, corner_radius=15, fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], height=60)
        panel_score6.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        panel_score6.grid_rowconfigure((0,1), weight=1)
        panel_score6.grid_columnconfigure((0,1), weight=1)

        right_panel4 = ctk.CTkFrame(tab_main, corner_radius=15,fg_color=self.theme["card"],  border_width=2, border_color=self.theme["border"], width=200)
        right_panel4.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        right_panel4.grid_rowconfigure((0,1), weight=1)
        right_panel4.grid_columnconfigure((0,1), weight=1)

        label_component1 = ctk.CTkLabel(canvas1_panel, text="Wconn 1", font=ctk.CTkFont(size=12, weight="bold"),text_color=self.theme["primary"]).grid(row=0, column=0, pady=(5,0), padx=10, sticky="nsew")    
        self.canvas_width7 =int(self.screen_width*0.34)
        self.canvas_height7 = int(self.screen_height*0.22)
        self.canvas7= ctk.CTkCanvas(canvas1_panel, width=self.canvas_width7, height=self.canvas_height7, bg=self.theme["card"])
        self.canvas7.grid(row=1, column=0,  sticky="s", padx=10, pady=(0,10))

        label_component2 = ctk.CTkLabel(canvas2_panel, text="Cool 1", font=ctk.CTkFont(size=12, weight="bold"),text_color=self.theme["primary"]).grid(row=0, column=0, pady=(5,0), padx=10, sticky="nsew") 
        self.canvas_width8 =int(self.screen_width*0.34)
        self.canvas_height8 = int(self.screen_height*0.22)
        self.canvas8= ctk.CTkCanvas(canvas2_panel, width=self.canvas_width8, height=self.canvas_height8, bg=self.theme["card"])
        self.canvas8.grid(row=1, column=0,  sticky="s",  padx=10, pady=(0,10))

        label_component3 = ctk.CTkLabel(canvas3_panel, text="Cool 2", font=ctk.CTkFont(size=12, weight="bold"),text_color=self.theme["primary"]).grid(row=0, column=0, pady=(5,0), padx=10, sticky="nsew") 
        self.canvas_width9 =int(self.screen_width*0.34)
        self.canvas_height9 = int(self.screen_height*0.22)
        self.canvas9= ctk.CTkCanvas(canvas3_panel, width=self.canvas_width9, height=self.canvas_height9, bg=self.theme["card"])
        self.canvas9.grid(row=1, column=0, sticky="s", padx=10, pady=(0,10)) 

        score_label6 = ctk.CTkLabel(panel_score4, text="Anomaly Score:", font=ctk.CTkFont(size=16),text_color=self.theme["text_primary"])
        score_label6.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky="nw")
        self.scorebox6 = ctk.CTkTextbox(panel_score4, width=150, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"],text_color=self.theme["primary"]  )
        self.scorebox6.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        label_space = ctk.CTkLabel(panel_score4, text="                ", font=("Arial", 20), height=120).grid(row=2, column=0)
        res_label6 = ctk.CTkLabel(panel_score4, text="Result:", font=ctk.CTkFont(size=16, ),text_color=self.theme["text_primary"])
        res_label6.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="nw")
        self.resbox6 = ctk.CTkTextbox(panel_score4, width=150, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"], text_color=self.theme["primary"] )
        self.resbox6.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")


        score_label7 = ctk.CTkLabel(panel_score5, text="Anomaly Score:", font=ctk.CTkFont(size=16, ),text_color=self.theme["text_primary"])
        score_label7.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky="nw")
        self.scorebox7 = ctk.CTkTextbox(panel_score5, width=150, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"], text_color=self.theme["primary"] )
        self.scorebox7.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        label_space1 = ctk.CTkLabel(panel_score5, text="                ", font=("Arial", 20), height=120).grid(row=2, column=0)
        res_label7 = ctk.CTkLabel(panel_score5, text="Result:", font=ctk.CTkFont(size=16, ),text_color=self.theme["text_primary"])
        res_label7.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="nw")
        self.resbox7 = ctk.CTkTextbox(panel_score5, width=150, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"], text_color=self.theme["primary"] )
        self.resbox7.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")


        score_label8 = ctk.CTkLabel(panel_score6, text="Anomaly Score:", font=ctk.CTkFont(size=16, ),text_color=self.theme["text_primary"])
        score_label8.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky="nw")
        self.scorebox8 = ctk.CTkTextbox(panel_score6, width=150, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"],text_color=self.theme["primary"] )
        self.scorebox8.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        label_space2 = ctk.CTkLabel(panel_score6, text="                ", font=("Arial", 20), height=120).grid(row=2, column=0)
        res_label8 = ctk.CTkLabel(panel_score6, text="Result:", font=ctk.CTkFont(size=16, ),text_color=self.theme["text_primary"])
        res_label8.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="nw")
        self.resbox8 = ctk.CTkTextbox(panel_score6, width=150, height=40, fg_color=self.theme["surface"], corner_radius=15, border_width=2, border_color=self.theme["border"],text_color=self.theme["primary"]  )
        self.resbox8.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        label_ISNtext = ctk.CTkLabel(right_panel4, text="ISN:", font=ctk.CTkFont(size=16, weight="bold"),text_color=self.theme["primary"]).grid(row=0, column=0, pady=10, padx=10)
        self.label_ISN = ctk.CTkLabel(right_panel4, text="     ", font=("Arial", 20), text_color=self.theme["primary"] )
        self.label_ISN.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)
        label_space3 = ctk.CTkLabel(right_panel4, text="     ", font=("Arial", 20)).grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        label_overall = ctk.CTkLabel(right_panel4, text="Overall Result:", font=ctk.CTkFont(size=16, weight="bold"),text_color=self.theme["primary"]).grid(row=3, column=0, pady=10, padx=10)
        self.button_res4 = ctk.CTkButton(right_panel4, text="", width=90, height=80, fg_color="gray", state=ctk.DISABLED,corner_radius=30, border_width=2, border_color=self.theme["border"])
        self.button_res4.grid(row=4, column=0, pady=10, padx=10, columnspan=2)      

    
    #TAB CONFIG

        self.switch_plc = ctk.CTkSwitch(tab_config, onvalue=1, offvalue=0, text="PLC Alarm")
        self.switch_plc.grid(row=0, column=0, padx=10, pady=10)
        self.switch_plc.select()
        
        self.model1_ch = ctk.CTkCheckBox(tab_config, onvalue=1, offvalue=0, text="WConn")
        self.model1_ch.grid(row=1, column=0, padx=10, pady=10)
        self.model1_ch.select()
        
        self.model2_ch = ctk.CTkCheckBox(tab_config, onvalue=1, offvalue=0, text="Coolant1")
        self.model2_ch.grid(row=2, column=0, padx=10, pady=10)
        self.model2_ch.select()
        
        self.model3_ch = ctk.CTkCheckBox(tab_config, onvalue=1, offvalue=0, text="Coolant2")
        self.model3_ch.grid(row=3, column=0, padx=10, pady=10)
        self.model3_ch.select()

        self.open_config()
        
    
    def open_config(self):
        #Abrir configuracion
        with open("config.json", "r") as f:
            self.file_config = json.load(f)

        componentes = self.file_config["Components"]
        print("componentes encontrados para inspeccionar:", componentes)

        #Cargar modelos OpenVINO
        weights_path = Path.cwd()/"weights"
        self.openvino_model_path1 = weights_path/"WConn"/"openvino" /"model1.bin"
        self.openvino_model_path2 = weights_path/"Cool1"/"openvino" /"model2.bin"
        self.openvino_model_path3 = weights_path/"Cool2"/"openvino" /"model3.bin"

        self.processed_log = self.file_config["enviados_log"]
        if os.path.exists(self.processed_log):
            with open(self.processed_log, "r") as f:
                self.processed_folders = set(line.strip() for line in f if line.strip())
        else:
            self.processed_folders = set()


        self.auto_folder_path = self.config["Folder_path"]

        print("OpenVino model 1 exits:", self.openvino_model_path1.exists())
        print("OpenVino model 2 exits:", self.openvino_model_path2.exists())
        print("OpenVino model 3 exits:", self.openvino_model_path3.exists())
        #print("OpenVino path", self.openvino_model_path)
        self.is_scanning_online = True
        #self.StartInspection()
        self.start_scan_thread_online()
    
    def start_scan_thread_online(self):
        self.is_scanning_online = True
        thread = threading.Thread(target=self.StartInspection, daemon=True)
        thread.start()

    def Inspection1(self):
        #self.output_image1 = None
        try:
            self.autoinspector = AutoInspector(self.openvino_model_path1, self.file_config, self.is_scanning_online, self.img_format)
            self.output_image1, self.roi1, self.score1, self.result1 = self.autoinspector.analyzePic1(self.img_path)
            
            print("processed with WConn")
        except Exception as e:
            print("Error in Inspection 1", e)
        #return self.output_image1, self.roi1, self.score1, self.result1
    
    def Inspection2(self):
        #self.output_image2 = None
        try:
            self.autoinspector2 = AutoInspector2(self.openvino_model_path2, self.file_config, self.is_scanning_online, self.img_format)
            self.output_image2, self.roi2, self.score2, self.result2 = self.autoinspector2.analyzePic2(self.img_path2)
            
            print("processed with Cool1")
        except Exception as e:
            print("Error in Inspection 2", e)
        #return self.output_image2, self.roi2, self.score2, self.result2

    def Inspection3(self):
        #self.output_image3 = None
        try:
            self.autoinspector3 = AutoInspector3(self.openvino_model_path3, self.file_config, self.is_scanning_online, self.img_format)
            self.output_image3, self.roi3, self.score3, self.result3 = self.autoinspector3.analyzePic3(self.img_path3)
        
            print("processed with Cool2")

        except Exception as e:
            print("Error in Inspection 3", e)
        #return self.output_image3, self.roi3, self.score3, self.result3
        
    def StartInspection(self):
        print("Iniciando watchdog en", self.auto_folder_path)

        self.processed_folders = set()
        self.start_time = datetime.now()

        event_handler = AOIWatchdogHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.auto_folder_path, recursive=True)
        observer.start()

        
        while self.is_scanning_online:
            time.sleep(1)


        observer.stop()
        observer.join()
#reelplazo cam_folder por isn_folder 

    def wait_for_file(self, path, timeout=5):
        start_time = time.time()
        last_size = -1
        while True:
            if os.path.exists(path):
                size = os.path.getsize(path)
                if size == last_size and size > 0:
                    return True
                last_size = size
            if time.time() - start_time > timeout:
                return False
            
            time.sleep(0.2)
                
    def _try_process_isn(self, isn, cam_folder):
        try: 
            self.img_format = " "
            corr1 = self.file_config["Image_correlation1"]
            corr2 = self.file_config["Image_correlation2"]
            corr3 = self.file_config["Image_correlation3"]

            img1 = os.path.join(cam_folder, corr1)
            img2 = os.path.join(cam_folder, corr2)
            img3 = os.path.join(cam_folder, corr3)
            self.img_format = "JPG"

            '''if not os.path.exists(img1) or not os.path.exists(img2) or not os.path.exists(img3):
                corr4 = self.file_config["Image_correlation4"]
                corr5 = self.file_config["Image_correlation5"]
                corr6 = self.file_config["Image_correlation6"]

                img1 = os.path.join(cam_folder, corr4)
                img2 = os.path.join(cam_folder, corr5)
                img3 = os.path.join(cam_folder, corr6)
                self.img_format = "JPEG"'''
                
                #save pictures temporary
                
            temp = Path.cwd()/"tempor"
            temp.mkdir(exist_ok=True)
            destinos = []
            for img, name in [(img1, "img1.jpg"), (img2, "img2.jpg"), (img3, "img3.jpg")]:
                if not self.wait_for_file(img):
                    print((f"{img} bloqueada"))
                    return
                destino = os.path.join(temp, name)
                shutil.copy(img, destino)
                destinos.append(destino)
                if os.path.getsize(destino) ==0:
                    print("Imagen copiada esta vacia")
                    return
                

            '''if not os.path.exists(img1) or not os.path.exists(img2) or not os.path.exists(img3):
                return  
            if not os.path.exists(destino):
                return'''  
            time.sleep(1)
            print(f"Todas las imágenes listas para ISN {isn}")
            print("el formato de la imagen es", self.img_format)
            
            self.processed_folders.add(isn)
            self._process_isn(isn, *destinos)
            #self.after(5, lambda:self._post_process())
        except Exception as e:
            print("No se pudo procesar la imagen", e)
    

    def _process_isn(self, isn, img1, img2, img3):
        print(f"Procesando ISN {isn}")
        self.img_path = img1
        print("procesando imagen", self.img_path)
        
        self.img_path2 = img2
        print("Procesando imagen", self.img_path2)
        
        self.img_path3 = img3
        print("Procesando imagen", self.img_path3)
        
        self.ISNs = isn
        
        
        if self.model1_ch.get()==1:
            self.Inspection1()
            
        if self.model2_ch.get()==1:
            self.Inspection2()
        else:
            self.score2 = "0.0"
            self.result2 = "NA"
            
        if self.model3_ch.get()==1:
            self.Inspection3()
        else:
            self.score3 = "0.0"
            self.result3 = "NA"
            
        self._post_process()

    def _post_process(self):
        if self.model3_ch.get==1:
            if hasattr(self, "roi3"):
                print("Actualizando ui")
                self.update_ui1()
                
                if self.result1 == "NG" or self.result2 == "NG" or self.result3 == "NG":
                #COMENTAR LA LINEA SELF.POP_MESSAGE Y DESCOMENTAR LA LINEA SELF.OVERALL_RES=NG PARA CORRER AUTOMATICAMENTE SIN DOBLE VERIFICACION
                    #self.pop_message()
                    self.overall_res = "NG"
                    self.save_log()
                    self.save_log_online ()
                    self.check_plc = self.switch_plc.get()
                    if self.switch_plc.get() == 1:
                        print("PLC trigger sent")
                        self.myPLC.activeAddress(815)
                else:
                    self.overall_res = "OK"
                    self.save_log()
                    self.save_log_online ()
        else:
            if self.model1_ch.get()==1:
                if hasattr(self, "roi1"):
                    print("Actualizando ui")
                    self.update_ui1()
                    
                    if self.result1 == "NG" or self.result2 == "NG" or self.result3 == "NG":
                    #COMENTAR LA LINEA SELF.POP_MESSAGE Y DESCOMENTAR LA LINEA SELF.OVERALL_RES=NG PARA CORRER AUTOMATICAMENTE SIN DOBLE VERIFICACION
                        #self.pop_message()
                        self.overall_res = "NG"
                        self.save_log()
                        self.save_log_online ()
                        self.check_plc = self.switch_plc.get()
                        if self.switch_plc.get() == 1:
                            print("PLC trigger sent")
                            self.myPLC.activeAddress(815)
                    else:
                        self.overall_res = "OK"
                        self.save_log()
                        #self.save_log_online ()
                
                

    def update_ui1(self):

        if self.model1_ch.get()==1:
            #primer canvas 
            #img_pil7 = Image.open("output1.png")
            #img_pil7 = img_pil7.resize((self.canvas_width7, self.canvas_height7))
            img_pil7 = self.output_image1.resize((self.canvas_width7, self.canvas_height7))
            self.tk_img7 = ImageTk.PhotoImage(img_pil7)
            self.canvas7.delete("all")
            self.canvas7.create_image(0,0, anchor="nw", image=self.tk_img7)
        
        if self.model2_ch.get()==1:
            #SEGUNDO CANVAS
            #img_pil8 = Image.open("output2.png")
            #img_pil8 = img_pil8.resize((self.canvas_width8, self.canvas_height8))
            img_pil8 = self.output_image2.resize((self.canvas_width8, self.canvas_height8))
            self.tk_img8 = ImageTk.PhotoImage(img_pil8)
            self.canvas8.delete("all")
            self.canvas8.create_image(0,0, anchor="nw", image=self.tk_img8)
        
        if self.model3_ch.get()==1:
            #TERCER CANVAS
            #img_pil9 = Image.open("output3.png")
            #img_pil9 = img_pil9.resize((self.canvas_width9, self.canvas_height9))
            img_pil9 = self.output_image3.resize((self.canvas_width9, self.canvas_height9))
            self.tk_img9 = ImageTk.PhotoImage(img_pil9)
            self.canvas9.delete("all")
            self.canvas9.create_image(0,0, anchor="nw", image=self.tk_img9)

        #segundo canvas roi
        '''img_res2 = cv2.resize(self.roi1,(self.canvas_width2, self.canvas_height2)) #la imagen roi no se queda guardada como imagen pillow si no como imagen temporal
        img_pil2 = Image.fromarray(img_res2)
        self.tk_img2 = ImageTk.PhotoImage(img_pil2)
        self.canvas2.delete("all")
        self.canvas2.create_image(0,0, anchor="nw", image=self.tk_img2)'''

        #RESULTADOS
        if self.model1_ch.get()==1:
            self.scorebox6.delete("0.0","end")
            self.scorebox6.insert("0.0", f"{self.score1}%")
            self.resbox6.delete("0.0","end")
            self.resbox6.insert("0.0", f"{self.result1}")
        
        if self.model2_ch.get()==1:
            self.scorebox7.delete("0.0","end")
            self.scorebox7.insert("0.0", f"{self.score2}%")
            self.resbox7.delete("0.0","end")
            self.resbox7.insert("0.0", f"{self.result2}")

        if self.model3_ch.get()==1:
            self.scorebox8.delete("0.0","end")
            self.scorebox8.insert("0.0", f"{self.score3}%")
            self.resbox8.delete("0.0","end")
            self.resbox8.insert("0.0", f"{self.result3}")
        

        self.label_ISN.configure(text=self.ISNs)

        if self.model1_ch.get()==1 and self.model2_ch.get()==1 and self.model3_ch.get()==1:
            if self.result1 == "NG" or self.result2 == "NG" or self.result3 == "NG":
                self.button_res4.configure(text="NG", fg_color = "red")
            else:
                self.button_res4.configure(text="OK", fg_color ="green")
                
        else:
            if self.model2_ch.get()==0 and self.model3_ch.get()==0:
                if self.result1 == "NG":
                    self.button_res4.configure(text="NG", fg_color = "red")
                else:
                    self.button_res4.configure(text="OK", fg_color = "green")

                    

    def pop_message(self):
        response = messagebox.askyesno("Verify NG", "Is this a real NG?")
        
        if response == True:
            self.overall_res = "NG"
            self.result1 = " "
            self.result2 = " "
            self.result3 = " "
            self.save_log()
            self.save_log_online ()
        else:
            self.overall_res = "OK"
            self.save_log()
            self.save_log_online ()



    def save_log_online (self):
        
        log_dir = str(self.file_config["log_path"])
        print("log_dir", log_dir)
        if os.path.exists(log_dir):
            log_folder = os.path.join(log_dir, self.ISNs)
            os.makedirs(log_folder, exist_ok=True)
            print("log folder", log_folder)
            
            csv_path = os.path.join(log_folder, f"{self.ISNs}_NG.csv")
            
            #roi1
            if self.model1_ch.get()==1:
                roi1 = cv2.cvtColor(self.roi1, cv2.COLOR_BGR2RGB)
                img_fail_path1 = os.path.join(log_folder, f"{self.ISNs}_1NG.jpg")
                cv2.imwrite(img_fail_path1, roi1)

            if self.model2_ch.get()==1:
                roi2 = cv2.cvtColor(self.roi2, cv2.COLOR_BGR2RGB)
                img_fail_path2 = os.path.join(log_folder, f"{self.ISNs}_2NG.jpg")
                cv2.imwrite(img_fail_path2, roi2)

            if self.model3_ch.get()==1:
                roi3 = cv2.cvtColor(self.roi3, cv2.COLOR_BGR2RGB)
                img_fail_path3 = os.path.join(log_folder, f"{self.ISNs}_3NG.jpg")
                cv2.imwrite(img_fail_path3, roi3)
            try:

                with open(csv_path, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["ISN", "score_WCon", "score_C1", "score_C2", "resultWCon", "resultC1", "resultC2", "Overall_res"])
                    writer.writerow([self.ISNs, self.score1, self.score2, self.score3, self.result1, self.result2, self.result3, self.overall_res])
            except Exception as e:
                print("Error al intentar escribir el log", e)
    
    def save_log(self):
        
        with open(self.file_name, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self.ISNs, self.score1, self.score2, self.score3, self.result1, self.result2, self.result3, self.overall_res])     

    def on_close(self):
        self.is_scanning_online =False
        self.destroy()

if __name__ == "__main__":
    AnomalibDetection()