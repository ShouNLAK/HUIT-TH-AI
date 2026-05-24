# Tìm hiểu Pandas và Matplotlib trong Python.
import pandas as pd
import matplotlib.pyplot as plt

def main():
    try:
        # Khởi tạo DataFrame đơn giản
        data = {
            'Năm': [2018, 2019, 2020, 2021, 2022],
            'Doanh Thu': [100, 120, 150, 140, 180]
        }
        df = pd.DataFrame(data)
        print(df)
        
        # Vẽ biểu đồ
        plt.plot(df['Năm'], df['Doanh Thu'], marker='o')
        plt.title('Biểu đồ Doanh Thu qua các năm')
        plt.xlabel('Năm')
        plt.ylabel('Doanh Thu')
        plt.grid(True)
        # plt.show() # Uncomment để hiển thị biểu đồ
        print("Đã tạo biểu đồ thành công!")
    except ImportError:
        print("Cần cài đặt thư viện pandas và matplotlib: pip install pandas matplotlib")

if __name__ == "__main__":
    main()
