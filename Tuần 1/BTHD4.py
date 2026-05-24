# Viết chương trình tính tổng các số từ 0 đến n mà là bội của 3 hoặc 5.
def main():
    n = int(input("Nhập n: "))
    tong = sum(i for i in range(n + 1) if i % 3 == 0 or i % 5 == 0)
    print(f"Tổng các số từ 0 đến {n} là bội của 3 hoặc 5: {tong}")

if __name__ == "__main__":
    main()
