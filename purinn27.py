print("โปรมแกรมตรวจจับความเร็ว\n")
speed = int(input("กรุณาใส่ความเร็วของคุณ (กม./ชม.): "))
if speed <= 80:
    print("ปลอดภัย")
elif speed <= 100:
    print("เตือน")
elif speed <= 120:
    print("เสี่ยงถูกปรับ")
elif speed > 120:
    print("ผิดกฎหมาย - ปรับเงินทันที")
    