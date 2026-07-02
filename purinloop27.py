import random
n= int(input("กรุณาใส่ตัวเลข: "))
x = random.randint(1, 100)
count = 1 

while True:
    if n < x:
        print("น้อยเกินไป")
        n = int(input("กรุณาใส่ตัวเลข: "))
        count += 1
    elif n > x:
        print("มากเกินไป")
        n = int(input("กรุณาใส่ตัวเลข: "))
        count += 1
    else:
        print("ถูกต้อง")
        print("คุณทายไปทั้งหมด: ", count, " ครั้ง") 
        break

print("ตัวเลขที่ถูกต้องคือ: ", x)