import base64
import json
import os
from datetime import datetime


class File:
    def __init__(self, filename, database=None):
        self.filename = filename
        self.database = database                                    ## Compose database object to file object
        with open(filename, "rb") as Input_File:
            self.content = base64.encodestring(Input_File.read())   ## Encode byte string to Base64 formatted string
        self.is_tracked = False                                     ## Set initial status to untracked
        self.filesize = os.stat(filename).st_size
        for repo in database.data['repository']:
            if repo['filename'] == self.filename:
                self.is_tracked = True                              ## Set file's status to tracked
                self.repo = repo                                    ## Compose repository object to file object

    def revert(self):
        try:
            if self.is_tracked:
                if self.repo['metadata']:
                    self.repo['metadata'].pop()
                    self.database.save()
                    return "Revert changes successfully"
                elif not self.repo['metadata']:                                         ## Check if stack is empty
                    repo_index = self.database.data['repository'].index(self.repo)      ## Find index of the repository
                    self.database.data['repository'].pop(repo_index)                    ## Remove repository from database
                    self.database.save()
                    return "File removed from repository"
        except RuntimeError:
            return "Runtime error, the file doesn't exist in our repository!"

    def update(self):
        if self.is_tracked and self.repo['metadata']:
            revision = self.repo['metadata']
            new_content = base64.decodestring(revision[-1]['contents'])     ## Decode Base64 encoded string
            try:
                with open(self.filename, "wb") as tracked_file:
                    tracked_file.write(new_content)                         ## Write new content to file
                    return "File updated successfully!"
            except (RuntimeError, IOError):
                return "Error: file does not exist!"
        else:
            return "No changes are made"

    def add(self, message=""):
        repository = dict(filename=self.filename, metadata=[])      ## Construct local repository object
        metadata = {'contents': self.content,
                    'datetime': str(datetime.now()),
                    'message': message,
                    'size': self.filesize}                          ## Construct local metadata object
        if self.is_tracked:
            try:
                if self.repo['metadata'][-1]['contents'] != self.content and self.repo['metadata'][-1]['size'] != self.filesize:
                    self.repo['metadata'].append(metadata)          ## Push new revision to metadata stack
                    self.database.save()
                    return "Successful Commit!"
                else:
                    return "No changes were made"
            except IndexError:
                return "Error: the list is corrupted"
        else:
            repository['metadata'].append(metadata)
            self.database.data['repository'].append(repository)     ## Add repository object to the database
            self.database.save()
            return "First commit successful!"


class Database:
    def __init__(self):
        try:
            with open("db.json", "rb") as db:
                self.data = json.load(db)       ## Load JSON document from file
        except (RuntimeError, IOError):
            raise (RuntimeError, IOError)

    def save(self):
        try:
            with open("db.json", "wb") as db:
                json.dump(self.data, db)        ## Serialize database oject and store them in a file
        except (RuntimeError, IOError):
            return "Error: database file not found"

    @property
    def getFileNames(self):
        return list(repository['filename'] for repository in self.data['repository'])
