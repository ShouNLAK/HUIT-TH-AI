# Viết hàm trộn 2 mảng một chiều thành 1 mảng một chiều (tổng)
def tron_mang_tong(arr1, arr2):
    res = []
    max_len = max(len(arr1), len(arr2))
    for i in range(max_len):
        val1 = arr1[i] if i < len(arr1) else 0
        val2 = arr2[i] if i < len(arr2) else 0
        res.append(val1 + val2)
    return res

a = [1, 2, 3]
b = [4, 5, 6, 7]
print(tron_mang_tong(a, b))
