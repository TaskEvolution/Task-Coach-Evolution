sleep(2)
if exists ("1386056187843.png"):
    click("1386056206027.png")
assert exists ("1385718239031.png")
sleep(2)
type(Key.INSERT)
sleep(1)
type("New Task 1" + Key.ENTER)
sleep(1)
assert exists ("1385986718455.png")
type(Key.DELETE)
sleep(1)
if not exists("1385764911450.png"):
   print("Fail")
else:
   click("1385765016616.png")
   sleep(2)
   if exists("1385986728875.png"):
        print("Fail, task is not deleted")
   else:
        print("Success in deleting the task")      