sleep(2)
assert exists ("1385718239031.png")
sleep(1)
type('c', KEY_ALT)
sleep(5)
#Requires that you delete your authentication .dat first, since this is the interesting part.
if exists("1386012148519.png"):
    click("1386012178591.png")
    sleep(3)
    assert exists("1386012204689.png")
    sleep(1)
    click("1385765531131.png")
    sleep(1)

print("Successfully uploaded to Google Tasks")
