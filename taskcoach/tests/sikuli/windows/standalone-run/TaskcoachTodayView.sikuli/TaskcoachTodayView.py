#from sikuli import *
#import TaskcoachMain
#def today():
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
type('t', KEY_CTRL)
sleep(1)
assert exists("1385767412568.png")
sleep(2)
if exists("1385767520171.png"):
    click("1385767532097.png")
elif exists("1385767626226.png"):
    click("1385767642132.png")
print("Successfully showed the TodayView") 
#closeApp()

#def closeApp():
sleep(1)
click("1385770367703.png")