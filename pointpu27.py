print("โปรแกรมคำนวณคะแนนรวมและระดับเกรด")
point1 = int(input("คะแนนวิชาคณิตศาสตร์"))
point2 = int(input("คะแนนวิชาวิทยาศาสตร์"))
point3 = int(input("คะแนนวิชาคอมพิวเตอร์"))
total_point = point1+point2+point3
average = total_point/3

if average < 60:
    print("คะแนนรวมของคุณ = ", total_point)
    print("คะแนนเฉลี่ย 3 วิชา = ", average)
    print("ควรปรับปรุง")
elif average  < 80:
    print("ผ่าน")
else:
    print("ดีเยี่ยม")
