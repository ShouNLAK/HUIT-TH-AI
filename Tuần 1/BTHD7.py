# Tạo một array chứa các số nguyên, sau đó tạo một filter array chứa các giá trị lớn hơn 42.
arr = [10, 50, 42, 43, 20, 100, 5]
filtered_arr = [x for x in arr if x > 42]

print("Mảng gốc:", arr)
print("Mảng > 42:", filtered_arr)
