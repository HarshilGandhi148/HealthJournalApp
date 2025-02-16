'''
Health Journal App
Created by Harshil Gandhi
'''

#uses tkinter for GUI, pytesseract for text extraction, and Open CV for image processing
#all of these python modules will need to be installed on the computer of the user
from customtkinter import *
from tkinter import *
import cv2
import pytesseract as tess
import numpy as np
import datetime
from datetime import datetime
from PIL import Image, ImageTk
import re

#import only allowed on windows
try: 
    from ctypes import windll, byref, sizeof, c_int
except:
    pass
    
class HealthJournalApp:
    def __init__(self, root):
        #creates the window
        self.root = root
        
        #width: 1707, height: 1067 - used for adjusting to any screen
        self.width = root.winfo_screenwidth()               
        self.height = root.winfo_screenheight()
        self.BACKGROUND = "#E4E6E4"

        #sets window properties
        self.root.geometry(str(self.width) + "x" + str(self.height))
        self.root.resizable(True, True)
        self.root.configure(bg=self.BACKGROUND)
        self.root.title("")
        self.root.iconbitmap("empty.ico")
        
        #changes color of title bar - only on windows
        TITLE_COLOR = 0x00E4E6E4
        try:
            windll.dwmapi.DwmSetWindowAttribute(windll.user32.GetParent(self.root.winfo_id()), 35, byref(c_int(TITLE_COLOR)), sizeof(c_int))
        except:
            pass
        
        #calories, fats (g), carbs (g), protein (g)
        self.goals = [2000.0, 55.0, 300.0, 120.0]
        self.current = [0.0, 0.0, 0.0, 0.0]
        self.food = []
        self.times = []
        
        #color scheme
        self.LIGHT_BLUE = "#81D4FA"
        self.DARK_BLUE = "#1976D2"
        self.WHITE = "#FFFFFF"
        self.BLACK = "#000000"
        self.GRAY = "#808080"
        self.LIGHT_GRAY = "#D3D3D3"
        
        self.create_widgets()
    
    #creates UI for Log Food page
    def log_food(self):
        #creates a popup window
        self.log_btn = Toplevel(self.root)
        
        #sets window properties
        self.log_width = int((650/1707)*self.width)
        self.log_height = int((820/1067)*self.height)
        self.log_btn.geometry("{}x{}+{}+{}".format(self.log_width, self.log_height, int((self.width - self.log_width)/2), int((self.height - self.log_height)/2)))
        self.log_btn.resizable(False, False)
        self.log_btn.configure(bg=self.LIGHT_BLUE)
        self.log_btn.title("")
        self.log_btn.iconbitmap("empty.ico")
        
        #changes color of title bar - only on windows
        TITLE_COLOR = 0x00FAD481
        try:
            windll.dwmapi.DwmSetWindowAttribute(windll.user32.GetParent(self.log_btn.winfo_id()), 35, byref(c_int(TITLE_COLOR)), sizeof(c_int))
        except:
            pass
        
        #title on Log Food page
        self.log_title = Label(self.log_btn, text="Log Food", bg=self.LIGHT_BLUE, font=("Calibri", 35, "bold"), bd=2, fg = self.BLACK)
        self.log_title.place(relx=((self.log_width - 250)/2)/self.log_width, rely=20/self.log_height, relwidth=250/self.log_width, relheight=55/self.log_height)

        #cancel, done, upload  buttons
        self.log_cancel = CTkButton(self.log_btn, text = "Cancel", fg_color = self.BACKGROUND, font=("Calibri", 30, "bold"), text_color = self.BLACK, hover_color = "#B4B6B4", border_width=0, bg_color=self.LIGHT_BLUE, corner_radius=30, command = lambda: self.log_btn.destroy())
        self.log_cancel.place(relx=30/self.log_width, rely=(self.log_height - 100)/self.log_height, relwidth = 150/self.log_width, relheight = 70/self.log_height)
        
        self.log_done = CTkButton(self.log_btn, text = "Done", fg_color = self.BACKGROUND, font=("Calibri", 30, "bold"), text_color = self.BLACK, hover_color = "#B4B6B4", border_width=0, bg_color=self.LIGHT_BLUE, corner_radius=30, command = self.update_nutrition)
        self.log_done.place(relx=(self.log_width - 180)/self.log_width, rely=(self.log_height- 100)/self.log_height, relwidth = 150/self.log_width, relheight = 70/self.log_height)
        
        self.upload_button= CTkButton(self.log_btn, text = "Upload", fg_color = "green", font=("Calibri", 30, "bold"), text_color = self.BLACK, hover_color = "darkgreen", border_width=0, bg_color=self.LIGHT_BLUE, corner_radius=30, command = self.scan_food)
        self.upload_button.place(relx=((self.log_width - 150)/2)/self.log_width, rely=190/self.log_height, relwidth = 150/self.log_width, relheight = 70/self.log_height)
        
        #name input and label
        self.food_label = Label(self.log_btn, text="Name: ", bg = self.LIGHT_BLUE, font=("Calibri", 25, "bold"), bd = 0, fg = self.BLACK)
        self.food_label.place(relx=((self.log_width - 330)/2)/self.log_width, rely = 100/self.log_height, relwidth = 100/self.log_width, relheight = 60/self.log_height)
        
        self.food_name = CTkEntry(self.log_btn, placeholder_text="Food Name", fg_color = self.WHITE, font=("Calibri", 25, "bold"), text_color = self.BLACK, border_width=3, bg_color=self.LIGHT_BLUE, corner_radius=5, justify = "center", border_color = self.BLACK)
        self.food_name.place(relx=((self.log_width - 330)/2 + 130)/self.log_width, rely=100/self.log_height, relwidth = 200/self.log_width, relheight = 60/self.log_height)

        #box ot display uploaded image
        self.image_label = Label(self.log_btn, text="Selected Image" + "\n" + "will appear here", bg = self.LIGHT_BLUE, font=("Calibri", 20, "bold"), bd=2, relief="solid")
        self.image_label.place(relx=30/self.log_width, rely=290/self.log_height, relwidth = 300/self.log_width, relheight = 400/self.log_height)
        
        #calorie, fats, carbs, protein labels - only enables once image is uploaded, text variable used to limit input to only numeric values
        self.cal_label = Label(self.log_btn, text="Calories: ", bg = self.LIGHT_BLUE, font=("Calibri", 20, "bold"), bd = 0, fg = self.BLACK, anchor = "w")
        self.cal_label.place(relx=340/self.log_width, rely = 290/self.log_height, relwidth = 100/self.log_width, relheight = 20/self.log_height)
        self.cal_input_var = StringVar()
        self.cal_input = Entry(self.log_btn, text = "", readonlybackground = self.LIGHT_BLUE, fg = self.BLACK, font=("Calibri", 20, "bold"), bd=0, bg=self.LIGHT_BLUE, textvariable=self.cal_input_var)
        self.cal_input_var.trace_add("write", lambda a, b, c, var = self.cal_input_var: self.delete_last_char(self.cal_input, self.cal_input_var))
        self.cal_input.configure(state = "readonly")
        self.cal_input.place(relx=445/self.log_width, rely=285/self.log_height, relwidth = 200/self.log_width, relheight = 30/self.log_height)

        self.fats_label = Label(self.log_btn, text="Fat: ", bg = self.LIGHT_BLUE, font=("Calibri", 20, "bold"), bd = 0, fg = self.BLACK, anchor = "w")
        self.fats_label.place(relx=340/self.log_width, rely = 340/self.log_height, relwidth = 45/self.log_width, relheight = 20/self.log_height)
        self.fats_input_var = StringVar()
        self.fats_input = Entry(self.log_btn, text = "", readonlybackground = self.LIGHT_BLUE, fg = self.BLACK, font=("Calibri", 20, "bold"), bd=0, bg=self.LIGHT_BLUE, textvariable=self.fats_input_var)
        self.fats_input_var.trace_add("write", lambda a, b, c, var = self.fats_input_var: self.delete_last_char(self.fats_input, self.fats_input_var))
        self.fats_input.configure(state = "readonly")
        self.fats_input.place(relx=390/self.log_width, rely=335/self.log_height, relwidth = 255/self.log_width, relheight = 30/self.log_height)

        self.carbs_label = Label(self.log_btn, text="Carbohydrates: ", bg = self.LIGHT_BLUE, font=("Calibri", 20, "bold"), bd = 0, fg = self.BLACK, anchor = "w")
        self.carbs_label.place(relx=340/self.log_width, rely = 390/self.log_height, relwidth = 175/self.log_width, relheight = 30/self.log_height)
        self.carbs_input_var = StringVar()
        self.carbs_input = Entry(self.log_btn, text = "", readonlybackground = self.LIGHT_BLUE, fg = self.BLACK, font=("Calibri", 20, "bold"), bd=0, bg=self.LIGHT_BLUE, textvariable=self.carbs_input_var)
        self.carbs_input_var.trace_add("write", lambda a, b, c, var = self.carbs_input_var: self.delete_last_char(self.carbs_input, self.carbs_input_var))
        self.carbs_input.configure(state = "readonly")
        self.carbs_input.place(relx=520/self.log_width, rely=390/self.log_height, relwidth = 125/self.log_width, relheight = 30/self.log_height)
        
        self.protein_label = Label(self.log_btn, text="Protein: ", bg = self.LIGHT_BLUE, font=("Calibri", 20, "bold"), bd = 0, fg = self.BLACK, anchor = "w")
        self.protein_label.place(relx=340/self.log_width, rely = 450/self.log_height, relwidth = 95/self.log_width, relheight = 20/self.log_height)
        self.protein_input_var = StringVar()
        self.protein_input = Entry(self.log_btn, text = "", readonlybackground = self.LIGHT_BLUE, fg = self.BLACK, font=("Calibri", 20, "bold"), bd=0, bg=self.LIGHT_BLUE, textvariable=self.protein_input_var)
        self.protein_input_var.trace_add("write", lambda a, b, c, var = self.protein_input_var: self.delete_last_char(self.protein_input, self.protein_input_var))
        self.protein_input.configure(state = "readonly")
        self.protein_input.place(relx=440/self.log_width, rely=445/self.log_height, relwidth = 205/self.log_width, relheight = 30/self.log_height)
        
    #updates food list, labels, and progress bars
    def update_nutrition(self):
        #only updates if name contains a string
        if (self.food_name.get() != ""):
            self.current[0] += float(self.cal_input.get())
            self.current[1] += float(self.fats_input.get())
            self.current[2] += float(self.carbs_input.get())
            self.current[3] += float(self.protein_input.get())
            
            #updates progress bar and labels
            self.update_labels_and_bars()
            
            #updates foods list
            self.food.append(self.food_name.get())
            self.times.append(str((int(datetime.now().strftime("%H"))) % 12) + ":" + (datetime.now().strftime("%M")))
            
            self.food_list_info.configure(state = "normal")
            self.food_list_info.insert(END, self.times[len(self.times) - 1] + " - " + self.food[len(self.food) - 1])
                
            self.food_list_info.configure(state = "disabled")
            
            if (len(self.food) >= 22):
                self.side_scrollbar.configure(button_color = self.GRAY)
            
            #closes window
            self.log_btn.destroy()
      
    #updates labels and progress bars      
    def update_labels_and_bars(self):
        #updates progress bars
        self.cal_bar.update(self.current[0]/self.goals[0])
        self.fats_bar.update(self.current[1]/self.goals[1])
        self.carbs_bar.update(self.current[2]/self.goals[2])
        self.protein_bar.update(self.current[3]/self.goals[3])
            
        #updates info labels
        self.cal_info.configure(text="Current: " +  str(self.current[0]) + "\n" + "Goal: " + str(self.goals[0]))
        self.fats_info.configure(text="Current: " +  str(self.current[1]) + "g" + "\n" + "Goal: " + str(self.goals[1]) + "g")
        self.carbs_info.configure(text="Current: " +  str(self.current[2]) + "g" + "\n" + "Goal: " + str(self.goals[2]) + "g")
        self.protein_info.configure(text="Current: " +  str(self.current[3]) + "g" + "\n" + "Goal: " + str(self.goals[3]) + "g")

    #displays uploaded image on screen, sends the image to be processed
    def scan_food(self):
        #allows user to pick file
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

        #displays selected image
        if file_path:
            image = cv2.imread(file_path)
            
            #sends image to be processed
            self.process_scanning((tess.image_to_string(self.image_process(image), lang = "eng")).lower())
            
            image = self.resize_image(image, 300/650*self.log_width, 400/820*self.log_height)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            self.image_label.configure(image=image, bd = 0)
            self.image_label.image = image
            self.log_btn.focus_force()
    
    #receives string of text that came from image processing     
    def process_scanning(self, input_str):
        #unlocks text inputs to user (in case a value is not found in processing or is inaccurate)
        self.cal_input.configure(state = "normal", fg = self.BLACK, bd = 2, relief = "solid", bg=self.WHITE)
        self.fats_input.configure(state = "normal", fg = self.BLACK, bd = 2, relief = "solid", bg=self.WHITE)
        self.carbs_input.configure(state = "normal", fg = self.BLACK, bd = 2, relief = "solid", bg=self.WHITE)
        self.protein_input.configure(state = "normal", fg = self.BLACK, bd = 2, relief = "solid", bg=self.WHITE)

        #searches text calorie, fats, carbs, and protein content 
        try:
            cal = re.search(r"calories\s*(\d+(\.\d+)?)", input_str)
            self.cal_input.delete(0, END)
            self.cal_input.insert(0, str(float(cal.group(1))))
        except:
            pass
            
        try:
            fat = re.search(r"al\s*fat\s*(\d+(\.\d+)?)", input_str)
            self.fats_input.configure(state = "normal", fg = self.BLACK)
            self.fats_input.delete(0, END)
            self.fats_input.insert(0, str(float(fat.group(1))))
        except:
            pass
        
        try:
            carbs = re.search(r"carbohydrate\s*(\d+(\.\d+)?)", input_str)
            self.carbs_input.configure(state = "normal", fg = self.BLACK)
            self.carbs_input.delete(0, END)
            self.carbs_input.insert(0, str(float(carbs.group(1))))
        except:
            pass

        try:
            protein = re.search(r"protein\s*(\d+(\.\d+)?)", input_str)
            self.protein_input.configure(state = "normal", fg = self.BLACK)
            self.protein_input.delete(0, END)
            self.protein_input.insert(0, str(float(protein.group(1))))
        except:
            pass
    
    #removes horizontal and vertical lines from given image
    def remove_lines(self, image):
        kernel_size = 500
        
        #creates image with everything but horizontal lines
        kernel = np.ones((1,kernel_size),np.uint8)
        horizontal = 255 - cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        #creates image with everything but vertical lines
        kernel = np.ones((kernel_size,1),np.uint8)
        vertical = 255 - cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        #combines images
        temp = cv2.add(vertical, horizontal)
        return cv2.add(temp, image)
    
    #pre-processes image for text extraction                   
    def image_process(self, image):
        image = self.remove_lines(image)
        
        #converted to black and white
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, image = cv2.threshold(image, 200, 255,cv2.THRESH_BINARY)
        
        kernel = np.ones((1,1),np.uint8)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=1)
        return image
    
    #resizes the image to fit page
    def resize_image(self, image, width, height):
        scale = 1
        resize_width = 0
        resize_height = 0
        
        #checks is image is larger or smaller than page
        if (image.shape[0]/height) > (image.shape[1]/width):
            scale = height/image.shape[0]
        else:
            scale = width/image.shape[1]
            
        resize_width = int(image.shape[1]*scale)
        resize_height = int(image.shape[0]*scale)
        
        #larger than page requires using a different interpolation than smaller than page
        if (image.shape[0]/height > 1) or (image.shape[1]/width > 1):
            resized_image = cv2.resize(image, (resize_width, resize_height), interpolation = cv2.INTER_AREA)
        else:
            resized_image = cv2.resize(image, (resize_width, resize_height), interpolation = cv2.INTER_CUBIC) 
             
        return resized_image

    #creates UI for Edit Goals page
    def edit_goals(self):
        #creates pop-up window
        self.goal = Toplevel(self.root)
        
        #sets window properties
        self.goal_width = int((550/1707)*self.width)
        self.goal_height = int((600/1067)*self.height)
        self.goal.geometry("{}x{}+{}+{}".format(self.goal_width, self.goal_height, int((self.width - self.goal_width)/2), int((self.height - self.goal_height)/2)))
        self.goal.resizable(False, False)
        self.goal.configure(bg=self.LIGHT_BLUE)
        self.goal.title("")
        self.goal.iconbitmap("empty.ico")
        
        #changes color of title bar - only on windows
        TITLE_COLOR = 0x00FAD481
        try:
            windll.dwmapi.DwmSetWindowAttribute(windll.user32.GetParent(self.goal.winfo_id()), 35, byref(c_int(TITLE_COLOR)), sizeof(c_int))
        except:
            pass
        
        #title for page
        goal_title = Label(self.goal, text="Goals", bg=self.LIGHT_BLUE, font=("Calibri", 35, "bold"), bd=2, fg = self.BLACK)
        goal_title.place(relx=((self.goal_width - 150)/2)/self.goal_width, rely=20/self.goal_height, relwidth=150/self.goal_width, relheight=55/self.goal_height)

        #cancel, done buttons
        self.goal_cancel = CTkButton(self.goal, text = "Cancel", fg_color = self.BACKGROUND, font=("Calibri", 30, "bold"), text_color = self.BLACK, hover_color = "#B4B6B4", border_width=0, bg_color=self.LIGHT_BLUE, corner_radius=30, command = lambda: self.goal.destroy())
        self.goal_cancel.place(relx=30/self.goal_width, rely=(self.goal_height- 100)/self.goal_height, relwidth = 150/self.goal_width, relheight = 70/self.goal_height)
        
        self.goal_done = CTkButton(self.goal, text = "Done", fg_color = self.BACKGROUND, font=("Calibri", 30, "bold"), text_color = self.BLACK, hover_color = "#B4B6B4", border_width=0, bg_color=self.LIGHT_BLUE, corner_radius=30, command = self.goal_save)
        self.goal_done.place(relx=(self.goal_width - 180)/self.goal_width, rely=(self.goal_height- 100)/self.goal_height, relwidth = 150/self.goal_width, relheight = 70/self.goal_height)

        #text inputs used for user to change goals, only take in numeric values
        self.cal_goal_label = Label(self.goal, text="Calories: ", bg = self.LIGHT_BLUE, font=("Calibri", 30, "bold"), bd = 0, fg = self.BLACK, anchor = "w")
        self.cal_goal_label.place(relx=30/self.goal_width, rely = 150/self.goal_height, relwidth = 150/self.goal_width, relheight = 30/self.goal_height)
        self.cal_goal_var = StringVar()
        self.cal_goal_input = Entry(self.goal, fg = self.BLACK, font=("Calibri", 30, "bold"), bd=3, bg=self.WHITE, relief="solid", textvariable = self.cal_goal_var)
        self.cal_goal_var.trace_add("write", lambda a, b, c, var = self.cal_goal_var: self.delete_last_char(self.cal_goal_input, self.cal_goal_var))
        self.cal_goal_input.place(relx=185/self.goal_width, rely=150/self.goal_height, relwidth = 200/self.goal_width, relheight = 40/self.goal_height)
        self.cal_goal_input.delete(0, END)
        self.cal_goal_input.insert(0, str(self.goals[0]))

        self.fats_goal_label = Label(self.goal, text="Fat: ", bg = self.LIGHT_BLUE, font=("Calibri", 30, "bold"), bd = 0, fg = self.BLACK, anchor = "w")
        self.fats_goal_label.place(relx=30/self.goal_width, rely = 210/self.goal_height, relwidth = 75/self.goal_width, relheight = 30/self.goal_height)
        self.fats_goal_var = StringVar()
        self.fats_goal_input = Entry(self.goal, text = str(self.goals[1]), fg = self.BLACK, font=("Calibri", 30, "bold"), bd=3, bg=self.WHITE, relief="solid", textvariable = self.fats_goal_var)
        self.fats_goal_var.trace_add("write", lambda a, b, c, var = self.fats_goal_var: self.delete_last_char(self.fats_goal_input, self.fats_goal_var))
        self.fats_goal_input.place(relx=110/self.goal_width, rely=210/self.goal_height, relwidth = 200/self.goal_width, relheight = 40/self.goal_height)
        self.fats_goal_input.delete(0, END)
        self.fats_goal_input.insert(0, str(self.goals[1]))

        self.carbs_goal_label = Label(self.goal, text="Carbohydrates: ", bg = self.LIGHT_BLUE, font=("Calibri", 30, "bold"), bd = 0, fg = self.BLACK, anchor = "w")
        self.carbs_goal_label.place(relx=30/self.goal_width, rely = 270/self.goal_height, relwidth = 260/self.goal_width, relheight = 40/self.goal_height)
        self.carbs_goal_var = StringVar()
        self.carbs_goal_input = Entry(self.goal, text = str(self.goals[2]), fg = self.BLACK, font=("Calibri", 30, "bold"), bd=3, bg=self.WHITE, relief="solid", textvariable = self.carbs_goal_var)
        self.carbs_goal_var.trace_add("write", lambda a, b, c, var = self.carbs_goal_var: self.delete_last_char(self.carbs_goal_input, self.carbs_goal_var))
        self.carbs_goal_input.place(relx=295/self.goal_width, rely=270/self.goal_height, relwidth = 200/self.goal_width, relheight = 40/self.goal_height)
        self.carbs_goal_input.delete(0, END)
        self.carbs_goal_input.insert(0, str(self.goals[2]))
                
        self.protein_goal_label = Label(self.goal, text="Protein: ", bg = self.LIGHT_BLUE, font=("Calibri", 30, "bold"), bd = 0, fg = self.BLACK, anchor = "w")
        self.protein_goal_label.place(relx=30/self.goal_width, rely = 340/self.goal_height, relwidth = 145/self.goal_width, relheight = 30/self.goal_height)
        self.protein_goal_var = StringVar()
        self.protein_goal_input = Entry(self.goal, text = str(self.goals[3]), fg = self.BLACK, font=("Calibri", 30, "bold"), bd=3, bg=self.WHITE, relief="solid", textvariable = self.protein_goal_var)
        self.protein_goal_var.trace_add("write", lambda a, b, c, var = self.protein_goal_var: self.delete_last_char(self.protein_goal_input, self.protein_goal_var))
        self.protein_goal_input.place(relx=180/self.goal_width, rely=340/self.goal_height, relwidth = 200/self.goal_width, relheight = 40/self.goal_height)
        self.protein_goal_input.delete(0, END)
        self.protein_goal_input.insert(0, str(self.goals[3]))
    
    #allows text inputs to only take in numeric values
    def delete_last_char(self, entry, text_variable):
        temp = ""
        for i in range(len(entry.get())):
            if (entry.get()[i]).isdigit():
                temp += (entry.get()[i])
            elif entry.get()[i] == "." and (not "." in entry.get()[:i]):
                temp += (entry.get()[i])
        text_variable.set(temp)
    
    #used to allow users to save their edited goals        
    def goal_save(self):
        #updates goals if inputs aren't empty
        if (self.cal_goal_input.get() != "") and (self.fats_goal_input.get() != "") and (self.carbs_goal_input.get() != "") and (self.protein_goal_input.get() != ""):
            self.goals[0] = float(self.cal_goal_input.get())
            self.goals[1] = float(self.fats_goal_input.get())
            self.goals[2] = float(self.carbs_goal_input.get())
            self.goals[3] = float(self.protein_goal_input.get())
            self.update_labels_and_bars()
            self.goal.destroy()

    #creates all widgets on main window of app
    def create_widgets(self):
        #frames on which widgets are placed on
        self.title_frame = CTkFrame(self.root, fg_color = self.WHITE, border_width=0)
        self.title_frame.place(relx=30/1707, rely=10/1067, relwidth = 365/1707, relheight = 70/1067)
        
        self.menu_frame = CTkFrame(self.root, fg_color = self.WHITE, border_width=0)
        self.menu_frame.place(relx=425/1707, rely=10/1067, relwidth = 605/1707, relheight = 70/1067)

        self.menu_line = CTkFrame(self.root, fg_color = self.DARK_BLUE, border_width=0)
        self.menu_line.place(relx=615/1707, rely=20/1067, relwidth = 5/1707, relheight = 50/1067)
        
        self.main_frame = CTkFrame(self.root, fg_color = self.WHITE, border_width=0)
        self.main_frame.place(relx=30/1707, rely=110/1067, relwidth = 1000/1707, relheight = 927/1067)
        
        self.side_frame = CTkFrame(self.root, fg_color = self.WHITE, border_width=5, border_color = self.GRAY)
        self.side_frame.place(relx=1060/1707, rely=10/1067, relwidth = 617/1707, relheight = 1027/1067)
        self.food_line = CTkFrame(self.root, fg_color = self.GRAY, bg_color = self.GRAY, border_width=0)
        self.food_line.place(relx=1060/1707, rely=100/1067, relwidth = 616/1707, relheight = 5/1067)
        
        self.calorie_frame = CTkFrame(self.root, fg_color = self.LIGHT_GRAY, border_width=0)
        self.calorie_frame.place(relx=60/1707, rely=140/1067, relwidth = 940/1707, relheight = 194.25/1067)
        self.cal_canvas = Canvas(self.root, background=self.LIGHT_GRAY, highlightthickness = 0)
        self.cal_canvas.place(relx=70/1707, rely=150/1067, relwidth = 920/1707, relheight = 174.25/1067)
        
        self.fats_frame = CTkFrame(self.root, fg_color = self.LIGHT_GRAY, border_width=0)
        self.fats_frame.place(relx=60/1707, rely=364.25/1067, relwidth = 940/1707, relheight = 194.25/1067)
        self.fats_canvas = Canvas(self.root, background=self.LIGHT_GRAY, highlightthickness = 0)
        self.fats_canvas.place(relx=70/1707, rely=374.25/1067, relwidth = 920/1707, relheight = 174.25/1067)
        
        self.carbs_frame = CTkFrame(self.root, fg_color = self.LIGHT_GRAY, border_width=0)
        self.carbs_frame.place(relx=60/1707, rely=588.5/1067, relwidth = 940/1707, relheight = 194.25/1067)
        self.carbs_canvas = Canvas(self.root, background=self.LIGHT_GRAY, highlightthickness = 0)
        self.carbs_canvas.place(relx=70/1707, rely=598.5/1067, relwidth = 920/1707, relheight = 174.25/1067)
        
        self.protein_frame = CTkFrame(self.root, fg_color = self.LIGHT_GRAY, border_width=0)
        self.protein_frame.place(relx=60/1707, rely=812.75/1067, relwidth = 940/1707, relheight = 194.25/1067)
        self.protein_canvas = Canvas(self.root, background=self.LIGHT_GRAY, highlightthickness = 0)
        self.protein_canvas.place(relx=70/1707, rely=822.75/1067, relwidth = 920/1707, relheight = 174.25/1067)
        
        #title of app and image
        self.title = CTkLabel(self.root, text="Health Journal", fg_color=self.WHITE, font=("Calibri", 35, "bold"), bg_color=self.WHITE, text_color = self.DARK_BLUE)
        self.title.place(relx=135/1707, rely=20/1067, relwidth=225/1707, relheight=50/1067)
        
        self.title_image = CTkImage(light_image=Image.open("Journal Logo.png"), size = (int(50/433*378),50))
        self.title_img = CTkLabel(self.root, text="", fg_color=self.WHITE, bg_color=self.WHITE, image = self.title_image)
        self.title_img.place(relx=65/1707, rely=20/1067, relwidth=50/1707, relheight=50/1067)
        
        #labels showing day and date
        self.today = datetime.today()
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        self.day = Label(self.root, text=(days_of_week[self.today.weekday()] + ","), bg=self.WHITE, font=("Calibri", 16, "bold"), bd=0, fg = self.DARK_BLUE)
        self.day.place(relx=445/1707, rely=20/1067, relwidth=150/1707, relheight=25/1067)
        
        self.date = Label(self.root, text=self.today.strftime("%B %d"), bg=self.WHITE, font=("Calibri", 16, "bold"), bd =0, fg = self.DARK_BLUE)
        self.date.place(relx=445/1707, rely=45/1067, relwidth=150/1707, relheight=25/1067)
        
        #log and goal buttons
        self.log_btn = CTkButton(self.root, text = "Log Food", fg_color = self.WHITE, font=("Calibri", 23, "bold"), text_color = self.DARK_BLUE, hover_color = self.BACKGROUND, border_width=0, bg_color=self.WHITE, corner_radius=10, command = self.log_food)
        self.log_btn.place(relx=670/1707, rely=20/1067, relwidth=150/1707, relheight=50/1067)
        
        self.goals_btn = CTkButton(self.root, text = "Edit Goals", fg_color = self.WHITE, font=("Calibri", 23, "bold"), text_color = self.DARK_BLUE, hover_color = self.BACKGROUND, border_width=0, bg_color=self.WHITE, corner_radius=10, command = self.edit_goals)
        self.goals_btn.place(relx=850/1707, rely=20/1067, relwidth=150/1707, relheight=50/1067)
        
        #food list
        self.food_list_title = Label(self.root, text="Food Log", fg=self.BLACK, font=("Calibri", 30, "bold"), bd = 0, bg=self.WHITE)
        self.food_list_title.place(relx=1068.5/1707, rely=35/1067, relwidth = 600/1707, relheight = 50/1067)
        
        self.food_list_info = Listbox(self.root, fg=self.BLACK, disabledforeground = self.BLACK, font=("Calibri", 23, "bold"), bd = 0, highlightthickness=0, bg=self.WHITE, justify = LEFT, state = "disabled")
        self.food_list_info.place(relx=1090/1707, rely=120/1067, relwidth = 557/1707, relheight = 910/1067)
        
        #scrollbar is initial hidden but will show when text overflows input
        self.side_scrollbar = CTkScrollbar(self.root, command=self.food_list_info.yview, fg_color = self.WHITE, button_color = self.WHITE)
        self.side_scrollbar.place(relx=1640/1707, rely=110/1067, relwidth = 17/1707, relheight = 910/1067)
        self.food_list_info.config(yscrollcommand = self.side_scrollbar.set) 
        
        #informtation labels and progress bars for calories, fats, carbs, protein
        self.calories = Label(self.root, text="Calories", fg=self.BLACK, font=("Calibri", 25, "bold"), bd = 0, bg=self.LIGHT_GRAY, anchor="w")
        self.calories.place(relx=90/1707, rely=170/1067, relwidth=150/1707, relheight=40/1067)
        self.cal_info = Label(self.root, text="Current: " + str(self.current[0]) + "\n" + "Goal: " + str(self.goals[0]), fg="darkgray", font=("Calibri", 18, "bold"), bd=0, bg=self.LIGHT_GRAY, anchor="nw", justify="left")
        self.cal_info.place(relx=90/1707, rely=210/1067, relwidth=400/1707, relheight=100/1067)
        self.cal_bar = Progress_Bar(self.cal_canvas, 500, 30, 200, 62.5, 10, self.current[0]/self.goals[0])
        
        self.fats = Label(self.root, text="Fats", fg=self.BLACK, font=("Calibri", 25, "bold"), bd = 0, bg=self.LIGHT_GRAY, anchor="w")
        self.fats.place(relx=90/1707, rely=394.25/1067, relwidth=150/1707, relheight=40/1067)
        self.fats_info = Label(self.root, text="Current: " +  str(self.current[1]) + "g\n" + "Goal: " + str(self.goals[1]) + "g", fg="darkgray", font=("Calibri", 18, "bold"), bd = 0, bg=self.LIGHT_GRAY, anchor="nw", justify = "left")
        self.fats_info.place(relx=90/1707, rely=434.25/1067, relwidth=400/1707, relheight=100/1067)
        self.fats_bar = Progress_Bar(self.fats_canvas, 500, 30, 200, 62.5, 10, self.current[1]/self.goals[1])
        
        self.carbs = Label(self.root, text="Carbohydrates", fg=self.BLACK, font=("Calibri", 25, "bold"), bd = 0, bg=self.LIGHT_GRAY, anchor="w")
        self.carbs.place(relx=90/1707, rely=628.5/1067, relwidth=250/1707, relheight=40/1067)
        self.carbs_info = Label(self.root, text="Current: " +  str(self.current[2]) + "g\n" + "Goal: " + str(self.goals[2]) + "g", fg="darkgray", font=("Calibri", 18, "bold"), bd = 0, bg=self.LIGHT_GRAY, anchor="nw", justify = "left")
        self.carbs_info.place(relx=90/1707, rely=668.5/1067, relwidth=400/1707, relheight=100/1067)
        self.carbs_bar = Progress_Bar(self.carbs_canvas, 500, 30, 200, 62.5, 10, self.current[2]/self.goals[2])
        
        self.protein = Label(self.root, text="Protein", fg=self.BLACK, font=("Calibri", 25, "bold"), bd = 0, bg=self.LIGHT_GRAY, anchor="w")
        self.protein.place(relx=90/1707, rely=852.75/1067, relwidth=150/1707, relheight=40/1067)
        self.protein_info = Label(self.root, text="Current: " +  str(self.current[3]) + "g\n" + "Goal: " + str(self.goals[3]) + "g", fg="darkgray", font=("Calibri", 18, "bold"), bd = 0, bg=self.LIGHT_GRAY, anchor="nw", justify = "left")
        self.protein_info.place(relx=90/1707, rely=892.75/1067, relwidth=400/1707, relheight=100/1067)
        self.protein_bar = Progress_Bar(self.protein_canvas, 500, 30, 200, 62.5, 10, self.current[3]/self.goals[3])

#used to create custom progress bar        
class Progress_Bar:
    def __init__(self, canvas, x, y, width, radius, padding, percent):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.radius = radius
        self.padding = padding
        self.percent = percent
        self.update(self.percent)

    #creates a rounded rectangle
    def rounded_rect(self, canvas, x, y, w, radius, **kwargs):
        #radius = height
        canvas.create_oval(x, y, x + 2*radius, y + 2*radius, **kwargs)
        
        # 0.5 accounts for small pixel distortion
        canvas.create_rectangle(x + radius, y, x + radius + w, y + 2*radius + 0.5, **kwargs)
        canvas.create_oval(x + w, y, x + 2*radius + w, y + 2*radius, **kwargs)
    
    #creates progress bar with two rounded rectangles
    def update(self, percent):
        self.percent = percent
        if (self.percent > 1):
            self.percent = 1
        self.rounded_rect(self.canvas, self.x, self.y, self.width, self.radius, fill = "#E4E6E4", width = 0)
        self.rounded_rect(self.canvas, self.x + self.padding, self.y + self.padding, self.width*self.percent, self.radius - self.padding, fill = "#81D4FA", width = 0)

#creates window and GUI
root = Tk()
health_app = HealthJournalApp(root)
root.mainloop()