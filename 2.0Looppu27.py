print("โปรมแกรมสูตรคูณ2.0\n")
n = int(input("ใส่แม่สูตรคูณเริ่มต้น: "))
m = int(input("ใส่แม่สูตรคูณสุดท้าย: "))
for j in range(n, m + 1):
    print(f"\nสูตรคูณของ {j}:")
    for i in range(1, 13):
        print(f"{j} x {i} = {j * i}")

print("\nจัดทำโดย:ภูรินทร์ เกตุชาญ")