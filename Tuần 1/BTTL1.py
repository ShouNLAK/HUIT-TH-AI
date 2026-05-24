# Viết chương trình nhập vào 2 giá trị a, b và tính tổng, hiệu, tích thương của a và b.
def main():
    a = float(input("Nhập a: "))
    b = float(input("Nhập b: "))
    print(f"Tổng: {a + b}")
    print(f"Hiệu: {a - b}")
    print(f"Tích: {a * b}")
    if b != 0:
        print(f"Thương: {a / b}")
    else:
        print("Không thể chia cho 0")

if __name__ == "__main__":
    main()
