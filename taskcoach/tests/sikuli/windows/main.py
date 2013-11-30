import os
dir = r"C:\Task-Coach-Evolution\taskcoach\tests\sikuli"
scripts = ["Taskcoach-DropboxBackup", "Taskcoach-PDFexport", "Taskcoach-TaskDeletion", "Taskcoach-TodayView"]
isPassAll = {}

for script in scripts:
    isPass = False
    scriptPath = os.path.join(dir, script+".sikuli")
    execfile(os.path.join(scriptPath, script+".py"))
    isPassAll[script] = isPass
print isPassAll