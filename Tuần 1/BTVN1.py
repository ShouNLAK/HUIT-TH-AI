# Viết hàm trộn 2 mảng một chiều thành 1 mảng một chiều (min)
def tron_mang_min(arr1, arr2):
    res = []
    max_len = max(len(arr1), len(arr2))
    for i in range(max_len):
        if i < len(arr1) and i < len(arr2):
            res.append(min(arr1[i], arr2[i]))
        elif i < len(arr1):
            res.append(arr1[i])
        else:
            res.append(arr2[i])
    return res

if __name__ == "__main__":
    a = [5, 2, 8]
    b = [4, 9, 6, 7]
    print(tron_mang_min(a, b))
