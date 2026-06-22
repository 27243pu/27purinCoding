print("โปรแกรมคำนวณคะแนนรวม\n")
math = int(input("ใส่คะแนนวิชาคณิตศาสตร์: "))
scienc = int(input("ใส่คะแนนวิชาวิทยาศาสตร์: "))
english = int(input("ใส่คะแนนวิชาภาษาอังกฤษ: "))

total_score = (math + scienc + english)/3
print("\nคะแนนรวมทั้ง3วิชา: ", int(total_score))
print("\nคะแนนเฉลี่ย: ", float(total_score))
if total_score >= 80:
    print("ดีเยี่ยม")
    
elif total_score >= 70:
    print("ผ่าน")

elif total_score >= 60:
    print("พอใช้")

else :
    print("ควรปรับปรุง")
print("จัดทำโดย: Purin27")