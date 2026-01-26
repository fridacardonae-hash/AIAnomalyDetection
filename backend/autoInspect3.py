import cv2
import numpy as np
from anomalib.deploy import OpenVINOInferencer
from pathlib import Path
from PIL import Image, ImageTk, ImageFilter
from anomalib.visualization import ImageVisualizer
import json
import cv2
import customtkinter as ctk
import os
from tkinter import filedialog
from datetime import datetime
import time
import csv
import threading


class AutoInspector3:
    def __init__(self, openvino_model_path3, file_config, is_scanning, img_format):
        super().__init__()
        self.openvino_model_path3 = openvino_model_path3
        self.file_config = file_config
        self.img_format = img_format
        #self.processed_log = self.file_config["enviados_log"]
        self.score_limit3 = float(self.file_config["scorelimit3"])
        self.is_scanning_online = is_scanning


    def analyzePic3(self, image_paths):
            #isn = image_paths.split("\\")
            #ISNn = isn[-1:]
            #isnFinal = ISNn[0]
            #print("ISN Final", isnFinal)
        try:
            image = Image.open(image_paths)
            if self.img_format != "JPG":
                print("imagen en diferente formato convirtiendo a jpg")
                img_np = np.array(image, dtype=np.float32)
                img_np = img_np / 255.0
                img_np = np.clip(img_np, 0.0, 1.0)
                img_np = (img_np * 255).astype(np.uint8)
                image = Image.fromarray(img_np, mode = "RGB")
                image = image.filter(ImageFilter.GaussianBlur(radius=0.6))              
                
            
            #x1,y1,x2,y2
            box = (2047, 1313, 3784, 2746)
            print("snipping Coolant2")
            image_snip = image.crop(box)
            #im_res = image_snip.resize((256, 256))

            #hacer inferencia
            inferencer = OpenVINOInferencer(
                path=self.openvino_model_path3,
                device="CPU",
            )
            #obtener predicciones
            predictions= inferencer.predict(image=image_snip)
            #print("predictions", predictions)
            scoreArr = predictions.pred_score[0]
            self.score3 = f"{(scoreArr[0]*100):.2f}"
            scorefloa = float(self.score3)
            print("prediction Coolant 2 ", self.score3)

            #Guardar solo imagen de anomalia
            vizualizer2 = ImageVisualizer(
                fields=[""],
                overlay_fields=[("image",["anomaly_map"])],
                text_config={"size":14},

            )
            output_anomalyimg = vizualizer2.visualize(predictions)
            output_anomalyimg.save("output_anomaly3.png")

            #Visualizar todas los modos de la inferencia 
            visualizer = ImageVisualizer(text_config={"size":16})
            self.output_image3 = visualizer.visualize(predictions)
            self.output_image3.save("output3.png")

            #Recorte con OpenCV [y1:y2, x1:x2]
            imroi = cv2.imread("output_anomaly3.png")
            self.roii3 = cv2.cvtColor(imroi, cv2.COLOR_BGR2RGB)

            if scorefloa > self.score_limit3:
                self.result3 = "NG"
            else:
                self.result3 = "OK"
        except Exception as e:
            print("error haciendo inferencia en Coolant2", e)
            return None, None, "ERROR"
            
        return  self.output_image, self.roii3, self.score3, self.result3

