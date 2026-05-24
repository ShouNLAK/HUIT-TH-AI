# Cho mảng 2 chiều a có m dòng, n cột chứa số nguyên, viết các hàm sau...
import random

def tao_mang(m, n):
    return [[random.randint(1, 20) for _ in range(n)] for _ in range(m)]

def xuat_dong_k(a, k):
    if 0 <= k < len(a):
        return a[k]
    return []

def xuat_cot_k(a, k):
    if len(a) > 0 and 0 <= k < len(a[0]):
        return [row[k] for row in a]
    return []

def dong_tong_lon_nhat_hon_45(a):
    max_sum = -1
    idx = -1
    for i, row in enumerate(a):
        s = sum(row)
        if s > 45 and s > max_sum:
            max_sum = s
            idx = i
    return idx, max_sum

def cot_tich_nho_nhat(a):
    if not a: return -1
    min_prod = float('inf')
    idx = -1
    for j in range(len(a[0])):
        prod = 1
        for i in range(len(a)):
            prod *= a[i][j]
        if prod < min_prod:
            min_prod = prod
            idx = j
    return idx, min_prod

def xuat_dong_chan_cot_le(a):
    res = []
    for i in range(0, len(a), 2): # dòng chẵn
        for j in range(1, len(a[0]), 2): # cột lẻ
            res.append(a[i][j])
    return res

def tbc_chan_dong_le(a):
    sum_val = 0
    count = 0
    for i in range(1, len(a), 2): # dòng lẻ
        for j in range(len(a[0])):
            if a[i][j] % 2 == 0:
                sum_val += a[i][j]
                count += 1
    return sum_val / count if count > 0 else 0

def tbc_bien(a):
    sum_val = 0
    count = 0
    m = len(a)
    n = len(a[0])
    for i in range(m):
        for j in range(n):
            if i == 0 or i == m-1 or j == 0 or j == n-1:
                sum_val += a[i][j]
                count += 1
    return sum_val / count if count > 0 else 0

def tb_tich_khong_bien(a):
    prod_val = 1
    count = 0
    m = len(a)
    n = len(a[0])
    for i in range(1, m-1):
        for j in range(1, n-1):
            prod_val *= a[i][j]
            count += 1
    return prod_val ** (1/count) if count > 0 else 0

if __name__ == "__main__":
    a = tao_mang(4, 5)
    for row in a:
        print(row)
    print("Dòng 1:", xuat_dong_k(a, 1))
    print("Cột 2:", xuat_cot_k(a, 2))
    print("Dòng tổng > 45 lớn nhất:", dong_tong_lon_nhat_hon_45(a))
    print("Cột có tích nhỏ nhất:", cot_tich_nho_nhat(a))
    print("Phần tử dòng chẵn cột lẻ:", xuat_dong_chan_cot_le(a))
    print("TBC chẵn dòng lẻ:", tbc_chan_dong_le(a))
    print("TBC biên:", tbc_bien(a))
    print("TB tích không biên:", tb_tich_khong_bien(a))
