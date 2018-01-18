import Tkinter
import os
import subprocess
import tkFileDialog
import tkSimpleDialog

from core import File, Database


class mainPage(Tkinter.Tk):
    def __init__(self, parent):             ## Initialize main page and create  window
        Tkinter.Tk.__init__(self, parent)   ## Inherit properties from Tkinter module
        self.parent = parent
        self.initUI()                       ## Initialize graphical elements

    def initUI(self):

        launchButton = Tkinter.Button(self, text=u"Launch File", command=self.launchFile, font=("Arial", 12))
        launchButton.config(width=20, height=2)
        launchButton.place(x=100, y=100)

        addButton = Tkinter.Button(self, text=u"Add File", command=self.addFile, font=("Arial", 12))
        addButton.config(width=20, height=2)
        addButton.place(x=300, y=100)

        revertButton = Tkinter.Button(self, text=u"Revert changes", command=self.revert, font=("Arial", 12))
        revertButton.config(width=20, height=2)
        revertButton.place(x=500, y=400)

        self.fileList = Tkinter.Listbox(self)
        self.fileList.place(x=100, y=200)
        self.fileList.config(width=100)
        self.updatefileList()   ## Dynamically update the elements in the file list
        self.fileList.bind('<<ListboxSelect>>', self.showRevisions)     ## Bind the list to an event

        self.labelMessage = Tkinter.StringVar()     ## Creates a global text variable for label
        label = Tkinter.Label(self, textvariable=self.labelMessage, anchor="w", fg="white", bg="blue",
                              font=("Arial", 12))
        label.place(x=100, y=400)
        self.labelMessage.set("No message")         ## Text variable initially set to default text

        self.labelDate = Tkinter.StringVar()        ## Creates a global text variable for label
        label2 = Tkinter.Label(self, textvariable=self.labelDate, anchor="w", fg="white", bg="blue", font=("Arial", 12))
        label2.place(x=100, y=420)
        self.labelDate.set("No date")               ## Text variable initially set to default text

        self.labelSize = Tkinter.StringVar()        ## Creates a global text variable for label
        label3 = Tkinter.Label(self, textvariable=self.labelSize, anchor="w", fg="white", bg="blue", font=("Arial", 12))
        label3.place(x=100, y=440)
        self.labelSize.set("No size")               ## Text variable initially set to default text

        labelStats = Tkinter.Label(self, text=u"File Stats", font=("Arial", 12))
        labelStats.place(x=100, y=370)

        labelTitle = Tkinter.Label(self, text=u"MyRCS", font=("Arial", 24))
        labelTitle.place(x=550, y=100)

        self.resizable(False, False)                ## Disable resizing the main window
        self.update()                               ## Update elements under main page
        self.geometry(self.geometry())              ## Contain elements in according to main page's configuration

    def updatefileList(self):
        self.fileList.delete(0, Tkinter.END)        ## Delete list from index 0 to last index
        for filenames in Database().getFileNames: self.fileList.insert(Tkinter.END, filenames)
        self.fileList.update_idletasks()            ## Update elements in the list

    def launchFile(self):
        ## Prompts a file dialog with only 2 available file types
        ## Once file is selected, dialog returns the file's path (filename)
        filename = tkFileDialog.askopenfilename(filetypes=[('word files', '.docx'), ('text files', '.txt')])
        ## Splits file's path into a tuple of directory string and extension string
        filepath, file_ext = os.path.splitext(filename)
        if filename:
            if file_ext == ".txt":
                ## Executable file for notepad program
                filepath = "C:/Windows/notepad.exe"
            elif file_ext == ".docx":
                ## Executable file for Microsoft Word program
                filepath = "C:/Program Files (x86)/Microsoft Office/root/Office16/WINWORD.EXE"
            try:
                ## Create sub process
                proc = subprocess.Popen([filepath, filename])
                proc.wait()
            except (OSError, subprocess.CalledProcessError):
                return "Failed, file is damaged or program has crashed!"
            ## Prompts dialog for user to input revision message
            message = tkSimpleDialog.askstring("Commit message", "What are the changes?")
            rcsFile = File(filename, Database())
            rcsFile.add(message)
        ## Update file list with the new changes
        self.updatefileList()

    def addFile(self):
        ## Prompts a file dialog with only 2 available file types
        filename = tkFileDialog.askopenfilename(filetypes=[('text files', '.txt'), ('word files', '.docx')])
        ## Prompts dialog for user to input revision message
        message = tkSimpleDialog.askstring("First commit", "What are the details?")
        rcsFile = File(filename, Database())
        rcsFile.add(message)
        ## Update file list with the new changes
        self.updatefileList()

    def revert(self):
        rcsFile = File(self.fileName, Database())
        rcsFile.revert()
        rcsFile.update()
        ## Update file list with the new changes
        self.updatefileList()

    def showRevisions(self, event):
        ## Assign event handler to a shorter name
        w = event.widget
        try:
            ## Get index of item selected by the cursor and retrieve the value
            index = int(w.curselection()[0])
            value = w.get(index)
        except IndexError:
            pass

        revisionList = Tkinter.Listbox(self)
        revisionList.place(x=580, y=200)
        revisionList.bind('<<ListboxSelect>>', self.Details)

        try:
            for files in Database().data['repository']:
                if files['filename'] == value:
                    for revisions in range(len(files['metadata'])): revisionList.insert(Tkinter.END,
                                                                                        "Revision %d" % revisions)
                    self.fileName = value
                    revisionList.update_idletasks()
        except IndexError:
            pass

    def Details(self, event):
        ## Assign event handler to a shorter name
        revlist = event.widget
        try:
            ## Get index of item selected by the cursor
            index = int(revlist.curselection()[0])
            for files in Database().data['repository']:
                if files['filename'] == self.fileName:
                    ## Set label's text variable given index of a revision
                    self.labelMessage.set(files['metadata'][index]['message'])
                    self.labelDate.set(files['metadata'][index]['datetime'])
                    self.labelSize.set("%d Bytes" % (files['metadata'][index]['size']))
        except IndexError:
            self.labelMessage.set("No Message")
            self.labelDate.set("No Date")
            self.labelSize.set("No Size")


if __name__ == "__main__":
    app = mainPage(None)                    ## Initialize main page
    app.title('MyRCS')                      ## Sets the title of the main window
    app.geometry("%dx%d+0+0" % (800, 500))  ## Configure the size of main window (width = 800 px, height = 500 px)
    app.mainloop()                          ## Start the main loop process
