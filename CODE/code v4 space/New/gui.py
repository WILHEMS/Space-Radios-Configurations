import PySimpleGUI as sg
import os.path

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
                  and f.lower().endswith((".png", ".gif"))



                  ]
        window["_FILE LIST_"].update(fnames)
    elif event == "_FILE LIST_":
        try:
            fileName = os.path.join(values['_FOLDER_'],values['_FILE LIST_'][0])
            window["_TOUT_"].update(fileName)
            window['_IMAGE_'].update(filename=fileName)
        except:
            pass


window.close()
