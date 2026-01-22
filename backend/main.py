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
from autoInspect import AutoInspector

import sys
from plc import SLMP_PLC
from tkinter import messagebox


class AnomalibDetection(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("green")
        

        self.root = ctk.CTk()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.title("PMX AI AOI")
        self.root.geometry("1300x850")

        self.file_name = datetime.now().strftime('%m-%d-%Y')
        with open(self.file_name, mode="w", newline="") as file:
            writer=csv.writer(file)
            writer.writerow(["ISN", "AnomalyScore", "R", "G", "B", "Result"])

        self.setup_gui()
        self.root.mainloop()
        self.is_scanning_online = False
        #self.autoinspector = AutoInspector(self.is_scanning_online)

    def setup_gui(self):
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tab_frame = ctk.CTkTabview(self.main_frame)
        self.tab_frame.pack(pady=10, padx=10, fill="both", expand=True)

        tab_manual = self.tab_frame.add("Manual revision")
        tab_auto = self.tab_frame.add("AutoInspect")
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
        
    #MANUAL TAB

        upper_panel = ctk.CTkFrame(tab_manual, corner_radius=10)
        upper_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)

        left_panel1 = ctk.CTkFrame(tab_manual, corner_radius=10)
        left_panel1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_panel1.grid_rowconfigure((0,1), weight=1)
        left_panel1.grid_columnconfigure((0,1), weight=1)
        
        right_panel1 = ctk.CTkFrame(tab_manual, corner_radius=10)
        right_panel1.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_panel1.grid_rowconfigure((0,1), weight=1)
        right_panel1.grid_columnconfigure((0,1), weight=1)

        label_result = ctk.CTkLabel(tab_manual, text="Result:", font=("Arial", 16)).grid(row=1, column=2, pady=10, padx=10)
        self.button_res = ctk.CTkButton(tab_manual, text="", width=90, height=80, fg_color="gray", state=ctk.DISABLED)
        self.button_res.grid(row=1, column=3, pady=10, padx=10)

        self.folder_path = ctk.StringVar()
        entry_label = ctk.CTkLabel(upper_panel, text="Select folder path", font=("Arial", 14)).grid(row=0, column=0)
        self.manual_folder_entry = ctk.CTkEntry(upper_panel, textvariable=self.folder_path, width=300)
        self.manual_folder_entry.grid(row=1, column=0)

        self.button_openf = ctk.CTkButton(upper_panel, text="Open", command=self.openfolder, width= 60)
        self.button_openf.grid(row=1, column=1)

        #self.button_start = ctk.CTkButton(left_panel1, text="Start", command=self.StartInspection, width= 60)
        #self.button_start.grid(row=1, column=1)
        
        self.score_label = ctk.CTkLabel(right_panel1, text="", font=("Arial", 16))
        self.score_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.isn_label = ctk.CTkLabel(right_panel1, text="", font=("Arial", 16))
        self.isn_label.grid(row=1, column=0, columnspan=2, pady=10)

        self.bgr_label = ctk.CTkLabel(right_panel1, text="", font=("Arial", 16))
        self.bgr_label.grid(row=2, column=0, columnspan=2, pady=80)

        self.button_pre = ctk.CTkButton(right_panel1, text="←", command=self.prevpic, width= 60)
        self.button_pre.grid(row=3, column=0)

        self.button_nex = ctk.CTkButton(right_panel1, text="→", command=self.nextpic, width= 60)
        self.button_nex.grid(row=3, column=1)

        self.canvas_width =int(self.screen_width*0.4)
        self.canvas_height = int(self.screen_height*0.3)

        self.canvas = ctk.CTkCanvas(left_panel1, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.grid(row=2, column=0, columnspan=2,sticky="s")

        self.canvas_width1 = int(self.screen_width*0.2)
        self.canvas_height1 = int(self.screen_height*0.27)

        self.canvas1 = ctk.CTkCanvas(left_panel1, width = self.canvas_width1, height=self.canvas_height1, bg="white")
        self.canvas1.grid(row=3, column=1, sticky="nsw", padx=20, pady=10)

        self.progress_bar = ctk.CTkProgressBar(left_panel1, width=self.canvas_width, height=10)
        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=(5, 10))
        self.progress_bar.set(0)
    

    #AUTO TAB

        upper_panel2 = ctk.CTkFrame(tab_auto, corner_radius=10)
        upper_panel2.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)

        left_panel2 = ctk.CTkFrame(tab_auto, corner_radius=10)
        left_panel2.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_panel2.grid_rowconfigure((0,1), weight=1)
        left_panel2.grid_columnconfigure((0,1), weight=1)
        
        right_panel2 = ctk.CTkFrame(tab_auto, corner_radius=10)
        right_panel2.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_panel2.grid_rowconfigure((0,1), weight=1)
        right_panel2.grid_columnconfigure((0,1), weight=1)

        label_result1 = ctk.CTkLabel(tab_auto, text="Result:", font=("Arial", 16)).grid(row=1, column=2, pady=10, padx=10)
        self.button_res1 = ctk.CTkButton(tab_auto, text="", width=90, height=80, fg_color="gray", state=ctk.DISABLED)
        self.button_res1.grid(row=1, column=3, pady=10, padx=10)

        self.folder_path_auto = ctk.StringVar()
        entry_label1 = ctk.CTkLabel(upper_panel2, text="Select folder path", font=("Arial", 14)).grid(row=0, column=0)
        self.manual_folder_entry1 = ctk.CTkEntry(upper_panel2, textvariable=self.folder_path_auto, width=300)
        self.manual_folder_entry1.grid(row=1, column=0)

        #self.button_openf1 = ctk.CTkButton(upper_panel2, text="Open", command=self.openfolderAuto, width= 60)
        #self.button_openf1.grid(row=1, column=1)

        self.button_start = ctk.CTkButton(left_panel2, text="Start", command=self.start_scan_thread_online, width= 60)
        self.button_start.grid(row=1, column=1, sticky="nsw", padx=20, pady=10, columnspan=2)
        
        self.score_label1 = ctk.CTkLabel(right_panel2, text="                             ", font=("Arial", 16))
        self.score_label1.grid(row=0, column=0, columnspan=2, pady=10)

        self.isn_label1 = ctk.CTkLabel(right_panel2, text="                   ", font=("Arial", 16))
        self.isn_label1.grid(row=1, column=0, columnspan=2, pady=10)

        self.bgr_label1 = ctk.CTkLabel(right_panel2, text="                    ", font=("Arial", 16))
        self.bgr_label1.grid(row=2, column=0, columnspan=2, pady=80)

        self.canvas_width2 =int(self.screen_width*0.5)
        self.canvas_height2 = int(self.screen_height*0.3)

        self.canvas2 = ctk.CTkCanvas(left_panel2, width=self.canvas_width2, height=self.canvas_height2, bg="white")
        self.canvas2.grid(row=2, column=0, columnspan=2,sticky="s")

        self.canvas_width3 = int(self.screen_width*0.2)
        self.canvas_height3 = int(self.screen_height*0.27)

        self.canvas3 = ctk.CTkCanvas(left_panel2, width = self.canvas_width3, height=self.canvas_height3, bg="white")
        self.canvas3.grid(row=3, column=1, sticky="nsw", padx=20, pady=10)
    
    #TAB CONFIG

        self.switch_plc = ctk.CTkSwitch(tab_config, onvalue=1, offvalue=0, text="PLC Alarm")
        self.switch_plc.grid(row=0, column=0, padx=10, pady=10)
        self.switch_plc.select()

        self.open_config()
        self.openfolderAuto()
    
    def open_config(self):
        #Abrir configuracion
        with open("config.json", "r") as f:
            self.file_config = json.load(f)

        componentes = self.file_config["Components"]
        print("componentes encontrados para inspeccionar:", componentes)

        #Cargar modelo OpenVINO
        weights_path = Path.cwd()/"weights"
        self.openvino_model_path = weights_path/"openvino" /"model.bin"

        print("OpenVino model exits:", self.openvino_model_path.exists())
        print("OpenVino path", self.openvino_model_path)
            

    def openfolder(self):
        global image_paths, current_index
        manual_folder_path = filedialog.askdirectory()
        if manual_folder_path:
            self.folder_path.set(manual_folder_path)
            if self.folder_path:
                image_paths = [os.path.join(manual_folder_path, f) for f in os.listdir(manual_folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                current_index =0
                self.showImage()
    
    def start_scan_thread_online(self):
        self.is_scanning_online = True
        thread = threading.Thread(target=self.StartInspection, daemon=True)
        thread.start()
    
    def openfolderAuto(self):
        self.auto_folder_path = self.config["Folder_path"]
        #self.auto_folder_path = filedialog.askdirectory()
        if self.auto_folder_path:
            self.folder_path_auto.set(self.auto_folder_path)
            if self.folder_path_auto:
                print("auto folder", self.auto_folder_path)
                print("folder path", self.folder_path_auto)

    def StartInspection(self):
        try:
            folder_path = self.auto_folder_path
            print("El folder seleccionado es", folder_path)
            while self.is_scanning_online:

                self.autoinspector = AutoInspector(self.openvino_model_path, self.file_config, self.is_scanning_online)
                self.output_image, self.roi, self.r_mean, self.g_mean, self.b_mean, self.ISNs, self.score, self.result = self.autoinspector.getPath(self.auto_folder_path)
                self.save_log(self.r_mean, self.g_mean, self.b_mean, self.ISNs, self.score, self.result)
                self.update_ui()
                if self.result == "NG":
                    self.save_log_online (self.roi, self.r_mean, self.g_mean, self.b_mean, self.ISNs, self.score)
                    #activar memoria plc
                    self.check_plc = self.switch_plc.get()
                    if self.check_plc == 1:
                        print("memoria enviada a PLC")
                        self.myPLC.activeAddress(815)
        except Exception as e:
            print(f"Error realizando inferencia: {e}")
            self.autoinspector = AutoInspector(self.openvino_model_path, self.file_config, self.is_scanning_online)


    def update_ui(self):

        #primer canvas 
        img_pil2 = self.output_image.resize((self.canvas_width2, self.canvas_height2))
        self.tk_img2 = ImageTk.PhotoImage(img_pil2)
        self.canvas2.delete("all")
        self.canvas2.create_image(0,0, anchor="nw", image=self.tk_img2)

        #segundo canvas roi
        img_res3 = cv2.resize(self.roi,(self.canvas_width3, self.canvas_height3))
        img_pil3 = Image.fromarray(img_res3)
        self.tk_img3 = ImageTk.PhotoImage(img_pil3)
        self.canvas3.delete("all")
        self.canvas3.create_image(0,0, anchor="nw", image=self.tk_img3)

        self.bgr_label1.configure(text=f"  R:{self.r_mean} , G:{self.g_mean} , B: {self.b_mean}")
        self.score_label1.configure(text=f"{self.score} %")
        self.isn_label1.configure(text=self.ISNs)
        if self.result == "NG":
            self.button_res1.configure(text="NG", fg_color = "red")
        else:
            self.button_res1.configure(text="OK", fg_color = "green")


    def save_log_online (self, roi, r_mean, g_mean, b_mean, ISNs, score):
        log_dir = str(self.file_config["log_path"])
        print("log_dir", log_dir)
        if os.path.exists(log_dir):
            log_folder = os.path.join(log_dir, ISNs)
            os.makedirs(log_folder, exist_ok=True)
            print("log folder", log_folder)

            csv_path = os.path.join(log_folder, f"{ISNs}_NG.csv")
            img_fail_path = os.path.join(log_folder, f"{ISNs}_NG.jpg")
            roi2 = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            cv2.imwrite(img_fail_path, roi2)
            try:

                with open(csv_path, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["ISN", "Score", "r_mean", "g_mean", "b_mean"])
                    writer.writerow([ISNs, score, r_mean, g_mean, b_mean])
            except Exception as e:
                print("Error al intentar escribir el log", e)


    def analyzePic(self, image_paths):
        isn = image_paths.split("\\")
        ISNn = isn[-1:]
        isnFinal = ISNn[0]
        #print("ISN Final", isnFinal)

        image = Image.open(image_paths)
        box = (1085, 1200, 3894, 2433)
        image_snip = image.crop(box)

        #hacer inferencia
        inferencer = OpenVINOInferencer(
            path=self.openvino_model_path,
            device="CPU",
        )
        #obtener predicciones
        predictions= inferencer.predict(image=image_snip)
        scoreArr = predictions.pred_score[0]
        score = f"{(scoreArr[0]*100):.2f}"
        print("prediction", score)

        #Guardar solo imagen de anomalia
        vizualizer2 = ImageVisualizer(
            fields=[""],
            overlay_fields=[("image",["anomaly_map"])],
            text_config={"size":14},

        )
        output_anomalyimg = vizualizer2.visualize(predictions)
        output_anomalyimg.save("output_anomaly.png")
        #Visualizar todas los modos de la inferencia 
        visualizer = ImageVisualizer()
        output_image = visualizer.visualize(predictions)

        '''#cargar areas de recorte de roi
        area = self.file_config["ROIs"]
        x1 = area["x1"]
        y1 = area["y1"]
        x2 = area["x2"]
        y2 = area["y2"]'''

        #Recorte con OpenCV [y1:y2, x1:x2]
        imroi = cv2.imread("output_anomaly.png")
        #roi= imroi[y1:y2, x1:x2]
        roi2 = cv2.cvtColor(imroi, cv2.COLOR_BGR2RGB)

        #Analisis con openCV en el ROI 
        mean_color = cv2.mean(roi2)[:3]
        r_mean, g_mean, b_mean = mean_color
        print(f"Promedio BGR: {mean_color}")

        score_limit = str(self.config["scorelimit"])

        #if b_mean < 210 and r_mean > 150 and g_mean > 230:
        if score > score_limit:
            result = "NG"
        else:
            result = "OK"
        
        return output_image, roi2, f"{r_mean:.2f}", f"{g_mean:.2f}", f"{b_mean:.2f}", isnFinal, score, result
    
    def showImage(self):
        global current_index
        if not image_paths:
            return
        img_path = image_paths[current_index]
        output_image,roi, r_mean, g_mean, b_mean, ISNs, score, result = self.analyzePic(img_path)
        self.save_log(r_mean,g_mean,b_mean, ISNs, score, result)

        #primer canvas
        img_pil = output_image.resize((self.canvas_width, self.canvas_height))
        self.tk_img = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(0,0, anchor="nw", image=self.tk_img)

        #segundo canvas roi
        img_res = cv2.resize(roi,(self.canvas_width1, self.canvas_height1))
        img_pil1 = Image.fromarray(img_res)
        self.tk_img1 = ImageTk.PhotoImage(img_pil1)
        self.canvas1.delete("all")
        self.canvas1.create_image(0,0, anchor="nw", image=self.tk_img1)

        progress = (current_index + 1) / len(image_paths)
        self.progress_bar.set(progress)

        self.bgr_label.configure(text=f"  R:{r_mean} , G:{g_mean} , B: {b_mean}")
        self.score_label.configure(text=f"{score} %")
        self.isn_label.configure(text=ISNs)
        if result == "NG":
            self.button_res.configure(text="NG", fg_color = "red")
        else:
            self.button_res.configure(text="OK", fg_color = "green")

    
    def save_log(self, r_mean, g_mean, b_mean, ISNs, score, result):
        
        with open(self.file_name, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([ISNs, score, r_mean, g_mean, b_mean, result])

    def nextpic(self):
        global current_index
        if image_paths and current_index < len(image_paths) - 1:
            current_index += 1
            self.showImage()

    def prevpic(self):
        global current_index
        if image_paths and current_index > 0:
            current_index -= 1
            self.showImage()
        

if __name__ == "__main__":
    AnomalibDetection()