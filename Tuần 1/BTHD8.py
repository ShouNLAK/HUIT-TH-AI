# Tạo một mảng filter chỉ chứa các phần tử chẵn từ mảng gốc.
arr = [1, 2, 3, 4, 5, 6, 7, 8]
even_arr = [x for x in arr if x % 2 == 0]

print("Mảng gốc:", arr)
print("Mảng chẵn:", even_arr)
