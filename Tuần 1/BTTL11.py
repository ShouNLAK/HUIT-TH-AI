# Tạo mảng số nguyên a với n phần tử và mảng b chỉ chứa các phần tử chẵn của a.
import random
n = 10
a = [random.randint(1, 100) for _ in range(n)]
b = [x for x in a if x % 2 == 0]
print("Mảng a:", a)
print("Mảng b:", b)
