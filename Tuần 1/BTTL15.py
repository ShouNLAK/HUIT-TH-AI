class SINHVIEN:
    def __init__(self, msv, ten, nam_sinh, dtb):
        self.msv = msv[:10]
        self.ten = ten[:20]
        self.nam_sinh = int(nam_sinh)
        self.dtb = float(dtb)

def so_sv_len_lop(mang_sv):
    return sum(1 for sv in mang_sv if sv.dtb >= 5)

def xuat_sv_20_tuoi(mang_sv):
    # Giả sử năm hiện tại là 2024
    for sv in mang_sv:
        if 2024 - sv.nam_sinh == 20:
            print(sv.ten)

def dem_sv_dai_hoc(mang_sv):
    # mã sinh viên chứa 2 ký tự DH ở vị trí 2,3 (index 2, 3 => chuoi[2:4] == "DH")
    return sum(1 for sv in mang_sv if len(sv.msv) >= 4 and sv.msv[2:4] == "DH")

def dem_sv_ten_lan(mang_sv):
    return sum(1 for sv in mang_sv if "Lan" in sv.ten.split())

def dem_sv_ho_phan(mang_sv):
    return sum(1 for sv in mang_sv if sv.ten.startswith("Phan "))

if __name__ == "__main__":
    svs = [
        SINHVIEN("01DH001", "Nguyễn Văn A", 2004, 7.5),
        SINHVIEN("02DH002", "Phan Thị Lan", 2004, 4.0),
        SINHVIEN("03CD001", "Lê Lan", 2005, 8.0)
    ]
    print("Số SV lên lớp:", so_sv_len_lop(svs))
    print("SV 20 tuổi (2004):")
    xuat_sv_20_tuoi(svs)
    print("Số SV hệ ĐH:", dem_sv_dai_hoc(svs))
    print("Số SV tên Lan:", dem_sv_ten_lan(svs))
    print("Số SV họ Phan:", dem_sv_ho_phan(svs))
