#from sikuli import *
#import TaskcoachMain



#def pdf ():
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
type('a',KEY_ALT)
sleep(2)
Region(565,486,246,40).click("1385720208610.png")
sleep(2)
type("test1" + Key.ENTER)
sleep(2)
if exists("1385727577034.png"):
   click("1385727597476.png")
click("1385560224304.png")
type("cmd")
sleep(2)
type(Key.ENTER)
sleep(1)
type("start test1.pdf" + Key.ENTER)
sleep(3)
if("1385718839786.png"):
    print("Yeah, PDF loaded")
else:
    print("Fail...")

#closeApp()

#def closeApp():
sleep(1)
click("1385770367703.png")