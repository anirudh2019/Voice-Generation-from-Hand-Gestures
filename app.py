from PIL import Image, ImageTk
import tkinter as tk
import cv2
import numpy as np
from spylls.hunspell import Dictionary
from string import ascii_uppercase
import mediapipe as mp 
import joblib
import pyttsx3

engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate',rate - 50)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
dictionary = Dictionary.from_files('en_US')


def data_clean(landmark):
    data = landmark[0]
    try:
      data = str(data)
      data = data.strip().split('\n')
      garbage = ['landmark {', '  visibility: 0.0', '  presence: 0.0', '}']
      without_garbage = []
      for i in data:
          if i not in garbage:
              without_garbage.append(i)
      clean = []
  
      for i in without_garbage:
          i = i.strip()
          clean.append(i[2:])
      finalClean = [ ]
      for i in range(0, len(clean)):
           if (i+1) % 3 != 0:
               finalClean.append(float(clean[i]))
      return([finalClean])
    except:
      return(np.zeros([1,63], dtype=int)[0])


class Application:
    def __init__(self):
        self.draw = True
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.gest_detector = joblib.load('model.pkl')
        self.hland_detector = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        
        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        for i in ascii_uppercase:
          self.ct[i] = 0
        print("Loaded model from disk")
        
        self.root = tk.Tk()
        self.root.title("Sign language to Text Converter")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("900x900")
        self.panel = tk.Label(self.root)                                    ### Big Image
        self.panel.place(x = 50, y = 60, width = 800, height = 500)
        
        self.T = tk.Label(self.root)
        self.T.place(x=230,y = 15)
        self.T.config(text = "Sign Language to Text",font=("courier",25,"bold"))
        self.panel3 = tk.Label(self.root)                                   # Current SYmbol 
        self.panel3.place(x = 300,y=560)
        self.T1 = tk.Label(self.root)
        self.T1.place(x = 10,y = 560)
        self.T1.config(text="Character :",font=("Courier",25,"bold"))
        self.panel4 = tk.Label(self.root)                                   # Word                            
        self.panel4.place(x = 300,y=620)
        self.T2 = tk.Label(self.root)
        self.T2.place(x = 10,y = 620)
        self.T2.config(text ="Word :",font=("Courier",25,"bold"))
        self.panel5 = tk.Label(self.root)                                   # Sentence
        self.panel5.place(x = 300,y=680)
        self.T3 = tk.Label(self.root)
        self.T3.place(x = 10,y = 680)
        self.T3.config(text ="Sentence :",font=("Courier",25,"bold"))

        self.T4 = tk.Label(self.root)
        self.T4.place(x = 300,y = 740)
        self.T4.config(text = "Suggestions",fg="red",font = ("Courier",25,"bold"))

        self.bt1=tk.Button(self.root, command=self.action1,height = 0,width = 0)
        self.bt1.place(x = 5,y=810)
        #self.bt1.grid(padx = 10, pady = 10)
        self.bt2=tk.Button(self.root, command=self.action2,height = 0,width = 0)
        self.bt2.place(x = 130,y=810)
        #self.panel3.place(x = 10,y=660)
        # self.bt2.grid(row = 4, column = 1, columnspan = 1, padx = 10, pady = 10, sticky = tk.NW)
        self.bt3=tk.Button(self.root, command=self.action3,height = 0,width = 0)
        self.bt3.place(x = 255,y=810)
        # self.bt3.grid(row = 4, column = 2, columnspan = 1, padx = 10, pady = 10, sticky = tk.NW)
        self.bt4=tk.Button(self.root, command=self.action4,height = 0,width = 0)
        self.bt4.place(x = 380,y=810)
        # self.bt4.grid(row = bt1, column = 0, columnspan = 1, padx = 10, pady = 10, sticky = tk.N)
        self.bt5=tk.Button(self.root, command=self.action5,height = 0,width = 0)
        self.bt5.place(x = 505,y=810)
        
        # self.bt5.grid(row = 5, column = 1, columnspan = 1, padx = 10, pady = 10, sticky = tk.N)
        
        self.str=""
        self.word=""
        self.current_symbol="Empty"
        self.video_loop()

    def video_loop(self):
        ok, frame = self.vs.read()
        if ok:
            cv2image = cv2.flip(frame, 1)

            cv2image = self.predict(cv2image)

            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)
            # cv2image = cv2.resize(cv2image, (500,500))
            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
            
            self.panel3.config(text=self.current_symbol,font=("Courier",25))
            self.panel4.config(text=self.word,font=("Courier",25))
            self.panel5.config(text=self.str,font=("Courier",25))
            
            predicts = []
            for sugg in dictionary.suggest(self.word):
                predicts.append(sugg)

            if(len(predicts) > 0):
                self.bt1.config(text=predicts[0],font = ("Courier",20))
            else:
                self.bt1.config(text="")
            if(len(predicts) > 1):
                self.bt2.config(text=predicts[1],font = ("Courier",20))
            else:
                self.bt2.config(text="")
            if(len(predicts) > 2):
                self.bt3.config(text=predicts[2],font = ("Courier",20))
            else:
                self.bt3.config(text="")
            if(len(predicts) > 3):
                self.bt4.config(text=predicts[3],font = ("Courier",20))
            else:
                self.bt4.config(text="")
            if(len(predicts) > 4):
                self.bt5.config(text=predicts[4],font = ("Courier",20))
            else:
                self.bt5.config(text="")
            
        self.root.after(30, self.video_loop)

    def predict(self, image):
        y_pred = "blank"
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hland_detector.process(image)
 
        image.flags.writeable = True
  
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  
        if results.multi_hand_landmarks:
          if self.draw:
            for hand_landmarks in results.multi_hand_landmarks:
                  mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
 
          cleaned_landmark = data_clean(results.multi_hand_landmarks)

          if cleaned_landmark:
            y_pred = self.gest_detector.predict(cleaned_landmark)[0]
            image = cv2.putText(image, y_pred, (50,150), cv2.FONT_HERSHEY_SIMPLEX,  3, (0,0,255), 2, cv2.LINE_AA) 
        
        self.current_symbol = y_pred

        if(self.current_symbol == 'blank'):
            for i in ascii_uppercase:
                self.ct[i] = 0

        self.ct[self.current_symbol] += 1
        if(self.ct[self.current_symbol] > 20):
            for i in ascii_uppercase:
                if i == self.current_symbol:
                    continue
                tmp = self.ct[self.current_symbol] - self.ct[i]
                if tmp < 0:
                    tmp *= -1
                if tmp <= 10:
                    self.ct['blank'] = 0
                    for i in ascii_uppercase:
                        self.ct[i] = 0
                    return image

            self.ct['blank'] = 0
            for i in ascii_uppercase:
                self.ct[i] = 0
            if self.current_symbol == 'blank':
                if self.blank_flag == 0:
                    self.blank_flag = 1
                    if len(self.str) > 0:
                        self.str += " "
                    self.str += self.word
                    engine.say(self.word)
                    engine.runAndWait()
                    self.word = ""
            else:
                if(len(self.str) > 16):
                    self.str = ""
                self.blank_flag = 0
                self.word += self.current_symbol

        return image
   


    def action1(self):
            predicts = []
            for sugg in dictionary.suggest(self.word):
                predicts.append(sugg)
            if(len(predicts) > 0):
                self.word=""
                self.str+=" "
                self.str+=predicts[0]
                engine.say(predicts[0])
                engine.runAndWait()
    def action2(self):
            predicts = []
            for sugg in dictionary.suggest(self.word):
                predicts.append(sugg)
            if(len(predicts) > 1):
                self.word=""
                self.str+=" "
                self.str+=predicts[1]
                engine.say(predicts[1])
                engine.runAndWait()
    def action3(self):
            predicts = []
            for sugg in dictionary.suggest(self.word):
                predicts.append(sugg)
            if(len(predicts) > 2):
                self.word=""
                self.str+=" "
                self.str+=predicts[2]
                engine.say(predicts[2])
                engine.runAndWait()
    def action4(self):
            predicts = []
            for sugg in dictionary.suggest(self.word):
                predicts.append(sugg)
            if(len(predicts) > 3):
                self.word=""
                self.str+=" "
                self.str+=predicts[3]
                engine.say(predicts[3])
                engine.runAndWait()
    def action5(self):
            predicts = []
            for sugg in dictionary.suggest(self.word):
                predicts.append(sugg)
            if(len(predicts) > 4):
                self.word=""
                self.str+=" "
                self.str+=predicts[4]
                engine.say(predicts[4])
                engine.runAndWait()

    def destructor(self):
        print("Closing Application...")
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()

    
print("Starting Application...")
pba = Application()
pba.root.mainloop()
