import paho.mqtt.client as mqtt_client
import json
import os
import uuid 
from random import uniform, randint
import time
from datetime import datetime, timedelta
import logging
import customtkinter
import threading

# List

user = "Client 6"

# This is set based on messages received from the  client
status = True

# Configure logging so that errors can be seen in the docker log.
logging.basicConfig(level=logging.INFO)

# Get the date & time
# Split it out into date and time seperately, setting their format too
date_and_time = datetime.now()
current_time = date_and_time.strftime("%H:%M")
date = date_and_time.strftime("%d/%m/%Y")

# MQTT broker configuration 
mqtt_Broker = '92.40.190.234' # Public IP of broker to connect to. 
mqtt_Port = 8883 # Non-standard port for security.
client_ID = "Client_" + "6"  #str(uuid.uuid4()) # Set a unique client ID ~ 
mqtt_Username = "Admin"
mqtt_Password = "Server14!"

# MQTT message topic configuration
mqtt_Topic = f'Clients/{client_ID}' # Set the mqtt topic to send its' data to 
mqtt_ReturnTopic = f'Clients/{client_ID}/Response' # Set the topic that messages are recieved on
mqtt_ErrorTopic = f'Clients/{client_ID}/Error' # Set the topic where error messages are sent to

# Output the client id to the log
logging.info(f"Client ID: {client_ID}")

bill_history = []

def update_labels(bill_history:list)->None:
    
    for i,bill in enumerate(bill_history):
        try:
            eval(f"mainWindow.billLog.priceLabel{i+1}.configure(text=get_price(bill))")
        except AttributeError:
            pass

def update_status(status):
    eval(f"mainWindow.statusWidget.statusLabel.configure(text=get_status(status))")
    
# Function to handle received messages
def on_message(client, userdata, message):
    received_message = json.loads(message.payload.decode()) # Decode any message received
    

    if (message.topic == mqtt_ReturnTopic): # Check if the message has been recieved from the same clients ID
        bill_Total = received_message['Bill Total']
        if bill_Total: # Check if Bill Total exists in the message
            logging.info(f'Recieved message:  {bill_Total}') # Act on the received message
            bill_history.append(bill_Total)
            if len(bill_history) > 5:
                bill_history.pop(0)
            update_labels(bill_history)
        else:
            logging.info(f'Recieved message without the bill total, {recieved_message}')

    elif (message.topic == mqtt_ErrorTopic):
        error_Message = received_message['Error']
        if error_Message:
            logging.info(f'Recieved message: {error_Message}')
            update_status(error_Message)
        else:
            logging.info(f'Recieved message with unexpected format, {recieved_message}')

    elif (message.topic == mqtt_ErrorTopic):
        error_Message = received_message['Error Message']
        if error_Message: # Check if there is an error message
            logging.info(f'Error: {error_Message}') # Output the error message if one is found
        else:
            logging.info(f'Invalid message format')
    else:
        logging.info(f'Invalid Message: Not from client')
        # If the message is not from either topic do nothing

def get_date (days_ago):
    today = datetime.now()
    target_date = today - timedelta(days=days_ago)
    return target_date.strftime("%d/%m/%Y")

# The function that handles receiving outputting the price from the server
def get_price (days_ago_price):
    return str(days_ago_price)

# Handling the status
def get_status (status):
    return str(status)

class billLog_Frame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Widgets
        self.dateLabel1 = customtkinter.CTkLabel(self, font=("Consolas" ,11), text=get_date(4))
        self.dateLabel1.grid(row=0, column=0, padx=20, pady=(15,0), sticky="nw")
        self.priceLabel1 = customtkinter.CTkLabel(self, font=("Consolas" ,14), text_color="#636fe3", text=get_price("Null"))
        self.priceLabel1.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="sw")
        
        self.dateLabel2 = customtkinter.CTkLabel(self, font=("Consolas" ,11), text=get_date(3))
        self.dateLabel2.grid(row=0, column=1, padx=20, pady=(15,0), sticky="nw")
        self.priceLabel2 = customtkinter.CTkLabel(self, font=("Consolas" ,14), text_color="#636fe3", text=get_price("Null"))
        self.priceLabel2.grid(row=1, column=1, padx=20, pady=(0,15), sticky="sw")

        self.dateLabel3 = customtkinter.CTkLabel(self, font=("Consolas" ,11), text=get_date(2))
        self.dateLabel3.grid(row=0, column=2, padx=20, pady=(15,0), sticky="nw")
        self.priceLabel3 = customtkinter.CTkLabel(self, font=("Consolas" ,14), text_color="#636fe3", text=get_price("Null"))
        self.priceLabel3.grid(row=1, column=2, padx=20, pady=(0,15), sticky="sw")

        self.dateLabel4 = customtkinter.CTkLabel(self, font=("Consolas" ,11), text=get_date(1))
        self.dateLabel4.grid(row=0, column=3, padx=20, pady=(15,0), sticky="nw")
        self.priceLabel4 = customtkinter.CTkLabel(self,  font=("Consolas" ,14), text_color="#636fe3", text=get_price("Null"))
        self.priceLabel4.grid(row=1, column=3, padx=20, pady=(0,15), sticky="sw")

        self.dateLabel5 = customtkinter.CTkLabel(self, font=("Consolas" ,11), text=get_date(0))
        self.dateLabel5.grid(row=0, column=4, padx=20, pady=(15,0), sticky="nw")
        self.priceLabel5 = customtkinter.CTkLabel(self, font=("Consolas" ,14), text_color="#636fe3", text=get_price("Null"))
        self.priceLabel5.grid(row=1, column=4, padx=20, pady=(0,15), sticky="sw")

class userCard_Frame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.loggedInLabel = customtkinter.CTkLabel(
            self,
            font=("Consolas", 10),
            text_color="#A3A3A3",
            text="You are logged in as:",
            anchor="w"
        )
        self.loggedInLabel.grid(row=0, column=0, padx=20, pady=(15,0), sticky="nsew")

        self.nameLabel = customtkinter.CTkLabel(
            self,
            font=("Consolas", 14),
            text_color="#FFFFF0",
            text=user,
            anchor="w"
        )
        self.nameLabel.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="nsew")

        #self.profilePicture = customtkinter.CTkImage("Icon2.ico")
        #self.profilePicture.grid(row=0, column=1, padx=20, pady=(15,0), sticky="e")

class status_Frame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.statusLabel = customtkinter.CTkLabel(
            self,
            font=("Consolas", 12),
            text_color="#FFFFF0",
            text="Powergrid Status: " + "ONLINE",
            anchor="w"
        )
        self.statusLabel.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="nsew")

        #self.update_status()

    def update_status(self):
        self.statusLabel.configure(text="Powergrid Status: ONLINE")
        self.after(1000, self.update_status)

class timeCard_Frame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.timeLabel = customtkinter.CTkLabel(
            self,
            font=("Helvetica", 60),
            text_color="#555555",
            text="",
            anchor="center"
        )
        self.timeLabel.grid(row=0, column=0, padx=(10, 10), pady=20, sticky="nsew")

        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M")
        self.timeLabel.configure(text=current_time)
        self.after(1000, self.update_time)

class mainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("616x254")
        self.title("Smart Meter: User")
        #self.wm_iconbitmap("Icon2.ico")
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure((0,1), weight=1)
        self.resizable(False, False)

        # Add widgets to app
        # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
        self.billLog = billLog_Frame(self)
        self.billLog.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nsew", columnspan=2)

        self.userCard = userCard_Frame(self)
        self.userCard.grid(row=1, column=1, padx=(0,10), pady=(10,10), sticky="ew")

        self.statusWidget = status_Frame(self)
        self.statusWidget.grid(row=2, column=1, padx=(0,10), pady=(0,10),sticky="ew")

        self.timeCard = timeCard_Frame(self)
        self.timeCard.grid(row=1, column=0, padx=10,pady=(10,10),sticky="nsew", rowspan=2)

        #self.button = customtkinter.CTkButton(self, command=self.button_callback)
        #self.button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

    # Add Methods to app
    def button_callback(self):
        print("Text output")

def mqtt_thread():
    # Set the on_message callback
    client = mqtt_client.Client()
    client.username_pw_set(username=mqtt_Username, password=mqtt_Password)
    client.on_message = on_message

    # Connect to the broker
    client.connect(mqtt_Broker, mqtt_Port)

    # Subscribe to the topic to receive messages
    client.subscribe(mqtt_ReturnTopic)
    client.subscribe(mqtt_ErrorTopic)

    # Start the network loop to enable message reception
    client.loop_start()

    # Tag to store the publish count
    publish_Count = int(0)

    while True: # Main loop
        power_Consumed = uniform(2,7) # Power consumed per 45s in w/h
        #publish_Time = int(randint(5,5))
        publish_Time = int(randint(15,45)) # Publish time randomly generated between 15 and 45 seconds
        timeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        json_Message = { # Create the JSON message
            "Client ID": f"{client_ID}",
            "Message Topic": f"{mqtt_Topic}",
            "Timestamp": f"{timeStamp}",
            "Power Consumed": f"{power_Consumed}",
            "Publish Frequency": publish_Time,
            "Bool": True
        }

        json_string = json.dumps(json_Message)

        client.publish(mqtt_Topic, json_string)
        publish_Count = publish_Count + 1
        logging.info(client_ID)


        logging.info(f"Published message: {publish_Count}, {timeStamp}, Next message will be sent in {publish_Time} seconds.")

        #print(f"publish_Time type: {type(publish_Time)}")  # Debugging line to check the type

        time.sleep(publish_Time)

    # Stop the network loop when exiting the application
    client.loop.stop()

# Create and start the MQTT thread
mqtt_thread = threading.Thread(target=mqtt_thread)
mqtt_thread.start()

# Create and start the main window
mainWindow = mainWindow()
mainWindow.mainloop()
