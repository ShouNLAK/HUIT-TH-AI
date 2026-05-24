# Viết chương trình tính tiền thuê Taxi. Biết rằng, mỗi khách hàng tính 2 và 1.5 cho 1km.
def tinh_tien_taxi(km):
    if km <= 0:
        return 0
    elif km <= 1:
        return 2
    else:
        return 2 + (km - 1) * 1.5

if __name__ == "__main__":
    km = float(input("Nhập số km: "))
    print(f"Tiền taxi cho {km} km là: {tinh_tien_taxi(km)}")
