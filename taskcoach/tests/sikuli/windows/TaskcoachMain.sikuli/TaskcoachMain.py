myScriptPath = "C:\\Task-Coach-Evolution\\taskcoach\\tests\\sikuli"
if not myScriptPath in sys.path: sys.path.append(myScriptPath)


import TaskcoachPDFexport
import TaskcoachDropboxBackup
import TaskcoachTodayView
#import TaskcoachDelete

def setUp():
    click("1385560224304.png")
    type("cmd")
    sleep(2)
    type(Key.ENTER)
    sleep(1)
    type("cd .." + Key.ENTER)
    type("cd .." + Key.ENTER)
    type("cd Task-Coach-Evolution" + Key.ENTER)
    type("cd taskcoach" + Key.ENTER)
    type("python taskcoach.py" + Key.ENTER)
    sleep(8)
    assert exists ("1385718239031.png")
    sleep(2)

def closeApp():
    sleep(1)
    click("1385770367703.png")

TaskcoachPDFexport.pdf()
TaskcoachDropboxBackup.dropbox()
TaskcoachTodayView.today()
TaskcoachTaskDeletion.deletion()