from sikuli import *
import TaskcoachMain
def deletetion():
    TaskcoachMain.setUp()
    
    click("1385764883070.png")
    type(Key.DELETE)
    sleep(1)
    if not exists("1385764911450.png"):
        print("Fail")
    else:
        click("1385765016616.png")
        sleep(2)
        if exists("1385765071388.png"):
            print("Fail")
        else:
            print("Success in deleting the task")
    TaskcoachMain.closeApp()        