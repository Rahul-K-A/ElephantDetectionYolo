import torch
import numpy as np
import cv2
from time import time
from playsound import playsound



class MugDetection:
            
    def __init__(self, capture_index, model_name):
        self.capture_index = capture_index
        self.model = self.load_model(model_name)
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

    def get_video_capture(self):
        return cv2.VideoCapture(self.capture_index)

    def load_model(self, model_name):
        if model_name:
            model = torch.hub.load('C:/Users/rahul/Desktop/YoloElephant/DetectSigns/yolov5-master', 'custom', path=model_name, force_reload=True,source="local")
        else:
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        return model
    
    def deter(self):
        playsound("C:/Users/rahul/Desktop/YoloElephant/Bee_Sound.mp3")
        

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        d_labels=[]
        elephant_detected=False

        for i in range(n):
            row = cord[i]
            if row[4] >= 0.0:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
                d_labels.append(self.class_to_label(labels[i]))
        
        if "Elephant" in d_labels:
            elephant_detected= True
            

        return frame,elephant_detected

    def __call__(self):
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame,
        and write the output into a new file.
        :return: void
        """
        cap = self.get_video_capture()
        assert cap.isOpened()
      
        while True:
          
            ret, frame = cap.read()
            assert ret
            
            frame = cv2.resize(frame, (416,416))
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            start_time = time()
            results = self.score_frame(frame)
            frame,elephant_detected = self.plot_boxes(results, frame)
            
            end_time = time()
            fps = 1/np.round(end_time - start_time, 2)
            #print(f"Frames Per Second : {fps}")
             
            cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
            # frame=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            
            cv2.imshow('YOLOv5 Detection', frame)
            
            if elephant_detected:
                self.deter()
            if cv2.waitKey(5) & 0xFF == 27:
                break
      
        cap.release()
        
# Create a new object and execute.
detector = MugDetection(capture_index=0, model_name='best.pt')
detector()

