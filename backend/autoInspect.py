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
from tkinter import filedialog, messagebox
from datetime import datetime
import time
import csv


class AutoInspector:
    def __init__(self, openvino_model_path, file_config, is_scanning):
        super().__init__()
        self.openvino_model_path = openvino_model_path
        self.file_config = file_config
        self.processed_log = self.file_config["enviados_log"]
        self.score_limit = str(self.file_config["scorelimit"])
        self.start_time = datetime.now()
        self.is_scanning_online = is_scanning

        if os.path.exists(self.processed_log):
            with open(self.processed_log, "r") as f:
                self.processed_folders = set(line.strip() for line in f if line.strip())
        else:
            self.processed_folders = set()

    def analyzePic(self, image_paths):
            #isn = image_paths.split("\\")
            #ISNn = isn[-1:]
            #isnFinal = ISNn[0]
            #print("ISN Final", isnFinal)

            image = Image.open(image_paths)
            print("haciendo recorte")
            box = (1085, 1200, 3894, 2433)
            image_snip = image.crop(box)

            #hacer inferencia
            print("haciendo inferencia")
            inferencer = OpenVINOInferencer(
                path=self.openvino_model_path,
                device="CPU",
            )
            #obtener predicciones
            predictions= inferencer.predict(image=image_snip)
            print("predictions", predictions)
            scoreArr = predictions.pred_score[0]
            score = f"{(scoreArr[0]*100):.2f}"
            print("prediction", score)
            scoreint = float(score)

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

            score_limit = float(self.file_config["scorelimit"])

            #if b_mean < 210 and r_mean > 150 and g_mean > 230:
            if scoreint > score_limit:
                result = "NG"
            else:
                result = "OK"
            
            return output_image, roi2, f"{r_mean:.2f}", f"{g_mean:.2f}", f"{b_mean:.2f}",  score, result


    def get_subfolder(self, path):
        subfolders = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path,f))]
        if not subfolders:
            return None
        return max(subfolders, key=os.path.getmtime)

    def getPath(self, folder_path):
        correlation = self.file_config["Image_correlation"] 

        if not os.path.isdir(folder_path):
            print("Ruta de imagenes no es valida")
            return
        
        self.processed_folders = set()
        while self.is_scanning_online:
            print("Buscando nuevas carpetas en", folder_path)
            time.sleep(2)
            day_folder = self.get_subfolder(folder_path)
            if not day_folder:
                continue
            for isn in os.listdir(day_folder):
                isn_path = os.path.join(day_folder, isn)
                print("ISN PATH", isn_path)
                if not os.path.isdir(isn_path) or isn in self.processed_folders:
                    continue
                try:
                    image_folder = os.path.join(isn_path, "Cam1")
                    creation_time = datetime.fromtimestamp(os.path.getctime(image_folder))
                except Exception as e:
                    print("Creation time cannot be readed", creation_time)
                    continue
                if creation_time > self.start_time:
                    print("Nueva carpeta detectada, esperando termine el proceso de AOI")
                    time.sleep(28)
                    try:
                        is_ok = isn_path+"_PASS"
                        splits = isn.split("_")
                        ISNs1= splits[0]
                        ISNs2= splits[1]
                        ISNs = f"{ISNs1}_{ISNs2}"
                        print("ISNs", ISNs)
                        img_path = os.path.join(is_ok,"Cam1",correlation)
                        #img_path.replace("\\", "/")
                        print("img path", img_path)
                        print(f"Nuevo ISN detectado {isn}")
                        output_image, roi2, r_mean, g_mean, b_mean, score, result = self.analyzePic(img_path)
                        self.processed_folders.add(isn)
                        print("processed", self.processed_folders)
                            

                    except Exception as e:
                        try:
                            print("The unit is NG, processing NG unit")
                            splits = isn.split("_")
                            ISNs1= splits[0]
                            ISNs2= splits[1]
                            ISNs = f"{ISNs1}_{ISNs2}"
                            print("ISNs", ISNs)
                            img_path = os.path.join(image_folder,correlation)
                            #img_path.replace("\\", "/")
                            print("img path", img_path)
                            print(f"Nuevo ISN detectado {isn}")
                            output_image, roi2, r_mean, g_mean, b_mean, score, result = self.analyzePic(img_path)
                            self.processed_folders.add(isn)
                            print("processed", self.processed_folders)
                        except Exception as e:
                            print(f"Error obtaining the picture for {ISNs}")
                            self.processed_folders.add(ISNs)
                           
                        
        
                    return output_image, roi2, r_mean, g_mean, b_mean, ISNs, score, result
                    


        '''correlation = self.file_config["Image_correlation"]  
        ISNs = ""

        for day in os.listdir(folder_path): 
            day = os.path.join(folder_path,day)
            for folder_isn in os.listdir(day): 
                folder_isn = os.path.join(day,folder_isn)
                print("folder", folder_isn)
                for files in os.listdir(folder_isn):
                    print("file", files)
                    if files == "Cam1":
                        cam_folder = os.path.join(folder_isn, "Cam1")
                        print("cam", cam_folder)

                        img_path = os.path.join(cam_folder, correlation)
                        print("IMG PATH", img_path)
                        new_path = img_path.replace("/","\\")
                        partes = new_path.split("\\")
                        ISNs= partes[-3:]
                        print("partes", ISNs)

                        break  


        if img_path is None:
            raise FileNotFoundError(
                f"No se encontró ninguna imagen que contenga '{correlation}' en {folder_path}"
            )


        output_image, roi, r_mean, g_mean, b_mean, score, result = self.analyzePic(img_path)

        return output_image, roi, r_mean, g_mean, b_mean, ISNs, score, result'''

