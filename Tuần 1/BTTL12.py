# Viết chương trình tính tổng các số từ 0 đến 999 mà là bội của 3 hoặc 5.
tong = sum(i for i in range(1000) if i % 3 == 0 or i % 5 == 0)
print("Tổng:", tong)
