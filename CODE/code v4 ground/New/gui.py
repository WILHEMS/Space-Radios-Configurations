import PySimpleGUI as sg
import os.path
from PIL import Image, ImageTk
import io

sg.theme('Dark')   # Add a touch of color
def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    '''
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()'''
    return ImageTk.PhotoImage(img)

file_list_column = [

    [sg.Text(''),
     sg.In(size=(25, 1), enable_events=True, key="_FOLDER_"),
     sg.FolderBrowse(),

     ],
    [
        sg.Listbox(values=[], enable_events=True, key="_FILE LIST_", size=(40, 20))]
]

image_viewer_column = [

    [sg.Text("Choose image to display")],
    [sg.Text(size=(40, 1), key="_TOUT_")],
    [sg.Image(key="_IMAGE_")]

]
layout = [
    [
    sg.Column(file_list_column),
    sg.VSeparator(),
    sg.Column(image_viewer_column)
    ]

]
window=sg.Window("Image Viewer", layout)
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WINDOW_CLOSED:
        break

    elif event == '_FOLDER_':
        folder = values["_FOLDER_"]
        try:
            file_list = os.listdir(folder)
        except:
            file_list= []
        fnames = [f
                  for f in file_list
                  if os.path.isfile(os.path.join(folder,f))
                  and f.lower().endswith((".png", ".gif", ".jpg"))



                  ]
        window["_FILE LIST_"].update(fnames)
    elif event == "_FILE LIST_":
        try:
            fileName = os.path.join(values['_FOLDER_'],values['_FILE LIST_'][0])
            window["_TOUT_"].update(fileName)
            window['_IMAGE_'].update(data=get_img_data(fileName, first=True))
        except:
            pass


window.close()
