import tkinter as tk
from pyrogram import Client
from pyrogram import errors
#import tkinter.simpledialog as sd


phone_number = ""
api_id =    # your api_id (8 digits)
api_hash = ""  # your api_hash
username = ""

def main():
   
    root = tk.Tk()
    
    root.title("Welcome")
    root.geometry("380x400")
    
    app = Client(username, api_id=api_id, api_hash=api_hash, phone_number=phone_number)

    btn1 = tk.Button(root, text="Get code", command=lambda: auth(app))
    btn1.pack()
    entry = tk.Entry(root)
    entry.pack()
    # creating button
    btn2 = tk.Button(root, text="Send code", command=lambda: signin(app,entry.get()))
    btn2.pack()
    
    # running the main loop
    root.mainloop()


def auth(app):
    global sent_code
  
    # app.disconnect()
    try:
        app.connect()
    except OSError.ConnectionError:
        print("Rate limit of connections is exceeded. Choose another application to sign in.")
    
    try:
        sent_code = app.send_code(phone_number)
    except (errors.exceptions.not_acceptable_406.PhoneNumberInvalid, errors.exceptions.bad_request_400.ApiIdInvalid):
        print("The phone number or api_id is invalid.")

    #userInput = sd.askinteger('Verification Code','CODE')
    #signed_in = app.sign_in(phone_number, sent_code.phone_code_hash, str(userInput))

def signin(app,userInput):
    signed_in = app.sign_in(phone_number, sent_code.phone_code_hash, str(userInput))
    return signed_in

if __name__ == '__main__':
    main()