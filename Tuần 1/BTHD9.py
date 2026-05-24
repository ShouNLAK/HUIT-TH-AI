# Cấu trúc SACH
class SACH:
    def __init__(self, ma_sach, ten_sach, gia_ban, so_luong):
        self.ma_sach = ma_sach[:10]
        self.ten_sach = ten_sach[:20]
        self.gia_ban = float(gia_ban)
        self.so_luong = int(so_luong)

    def __str__(self):
        return f"Mã: {self.ma_sach}, Tên: {self.ten_sach}, Giá: {self.gia_ban}, SL: {self.so_luong}"

def tong_so_luong(mang_sach):
    return sum(s.so_luong for s in mang_sach)

def xuat_sach_sl_lon_hon_10(mang_sach):
    for s in mang_sach:
        if s.so_luong > 10:
            print(s)

if __name__ == "__main__":
    danh_sach = [
        SACH("S01", "Toan", 15.5, 5),
        SACH("S02", "Ly", 20.0, 15),
        SACH("S03", "Hoa", 12.0, 12)
    ]
    print("Tổng số lượng sách:", tong_so_luong(danh_sach))
    print("Sách có số lượng > 10:")
    xuat_sach_sl_lon_hon_10(danh_sach)
