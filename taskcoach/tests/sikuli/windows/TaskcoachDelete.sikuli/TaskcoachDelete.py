#from sikuli import *
#import TaskcoachMain
#def deletetion():
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
        print("Restoring the task...")
        type('z', Key.CTRL)
        sleep(1)
#closeApp()

#def closeApp():
sleep(1)
click("1385770367703.png")       