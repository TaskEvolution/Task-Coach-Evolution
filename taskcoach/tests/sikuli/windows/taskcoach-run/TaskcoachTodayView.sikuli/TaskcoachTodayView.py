sleep(1)
if exists ("1386056187843.png"):
    click("1386056206027.png")
sleep(1)
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
