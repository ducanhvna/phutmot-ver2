import pandas as pd

# Đọc file Excel với tiêu đề ở dòng thứ 2
df = pd.read_excel('Quyphepbuton2024.xlsx', header=1)

# Chọn các cột cần thiết và đổi tên chúng
df = df[[df.columns[0], df.columns[1], df.columns[2], df.columns[3]]]
df.columns = ['code', 'name', 'al', 'cl']

# Loại bỏ các hàng có giá trị 'name' trống, null hoặc false
df = df[df['name'].notnull() & df['name'].astype(bool)]

# Chuyển các giá trị 'al' và 'cl' sang kiểu int
df['al'] = df['al'].astype(int)
df['cl'] = df['cl'].astype(int)

# Chuyển DataFrame sang định dạng JSON
json_data = df.to_json(orient='records', force_ascii=False)

# Lưu dữ liệu JSON vào file
with open('remain2024.json', 'w', encoding='utf-8') as f:
    f.write(json_data)
