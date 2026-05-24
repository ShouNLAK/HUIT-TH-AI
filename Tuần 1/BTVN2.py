# Cho ma trận vuông a cấp n...
def tong_tam_giac_tren_cheo_phu(a):
    n = len(a)
    s = 0
    for i in range(n):
        for j in range(n - i):
            s += a[i][j]
    return s

def chuyen_am_thanh_tuyet_doi(a):
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] < 0:
                a[i][j] = abs(a[i][j])
    return a

def thay_chan_bang_x(a, x):
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] % 2 == 0:
                a[i][j] = x
    return a

def kiem_tra_toan_chan(a):
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] % 2 != 0:
                return False
    return True

def kiem_tra_doi_xung(a):
    n = len(a)
    for i in range(n):
        for j in range(i+1, n):
            if a[i][j] != a[j][i]:
                return False
    return True

def cheo_chinh_tang_dan(a):
    n = len(a)
    for i in range(n - 1):
        if a[i][i] >= a[i+1][i+1]:
            return False
    return True

def xuat_tam_giac_duoi_cheo_phu(a):
    n = len(a)
    res = []
    for i in range(n):
        for j in range(n - i - 1, n):
            res.append(a[i][j])
    return res

def cheo_phu_giam_dan(a):
    n = len(a)
    # Các phần tử chéo phụ là a[i][n-1-i]
    for i in range(n - 1):
        if a[i][n-1-i] <= a[i+1][n-1-i-1]:
            return False
    return True

if __name__ == "__main__":
    a = [
        [1, -2, 3],
        [4, 5, -6],
        [7, 8, 9]
    ]
    print("Tổng tam giác trên chéo phụ:", tong_tam_giac_tren_cheo_phu(a))
