# refine-project

<div align="center" style="margin: 30px;">
    <a href="https://refine.dev">
    <img alt="refine logo" src="https://refine.ams3.cdn.digitaloceanspaces.com/readme/refine-readme-banner.png">
    </a>
</div>
<br/>

This [Refine](https://github.com/refinedev/refine) project was generated with [create refine-app](https://github.com/refinedev/refine/tree/master/packages/create-refine-app).

______________________________________________________________________

## 📋 Mô tả các màn hình chính trên Frontend

### 1. Dashboard (ダッシュボード)

- Đường dẫn: `/dashboard`
- Chức năng:
  - Thống kê nhanh: số học sinh, số lớp, điểm trung bình.
  - 4 biểu đồ Pie tổng hợp: phân bố giới tính, phân bố điểm trung bình, tỷ lệ có/không có 特記事項, số học sinh đạt ≥90 điểm từng môn.
  - Biểu đồ đường: So sánh điểm Toán và Quốc ngữ.
  - Biểu đồ cột: So sánh điểm Khoa học và Xã hội.
  - Biểu đồ phân tán: Mối liên hệ giữa điểm Toán và Khoa học.
  - Bảng tổng hợp kết quả học tập của học sinh.

### 2. Danh sách học sinh (生徒一覧)

- Đường dẫn: `/students`
- Chức năng:
  - Hiển thị bảng danh sách học sinh với các trường: 学籍番号, 氏名, 性別, クラス, 特記事項.
  - Lấy dữ liệu từ backend qua provider.

### 3. Danh sách giáo viên (教員一覧)

- Đường dẫn: `/teachers`
- Chức năng:
  - Hiển thị bảng danh sách giáo viên với các trường: 教員番号, 氏名, 性別, 担当科目, 特記事項.
  - Lấy dữ liệu từ backend qua API.

### 4. Sidebar/Menu

- Điều hướng nhanh tới các màn hình: Dashboard, Danh sách học sinh, Danh sách giáo viên.

______________________________________________________________________

## Getting Started

A React Framework for building internal tools, admin panels, dashboards & B2B apps with unmatched flexibility ✨

Refine's hooks and components simplifies the development process and eliminates the repetitive tasks by providing industry-standard solutions for crucial aspects of a project, including authentication, access control, routing, networking, state management, and i18n.

## Available Scripts

### Running the development server.

```bash
    npm run dev
```

### Building for production.

```bash
    npm run build
```

### Running the production server.

```bash
    npm run start
```

## Learn More

To learn more about **Refine**, please check out the [Documentation](https://refine.dev/docs)

- **REST Data Provider** [Docs](https://refine.dev/docs/core/providers/data-provider/#overview)
- **Ant Design** [Docs](https://refine.dev/docs/ui-frameworks/mui/tutorial/)
- **Custom Auth Provider** [Docs](https://refine.dev/docs/core/providers/auth-provider/)

## Công nghệ sử dụng

- Next.js, React, Ant Design, Refine, ECharts (echarts-for-react), Axios

## Lưu ý sử dụng

- Đảm bảo backend đã bật CORS và chạy trên cổng phù hợp (mặc định: 8000).
- Để hiển thị biểu đồ Pie 3D thực sự, cần cài thêm `echarts-gl` và cấu hình nâng cao.
- Giao diện mặc định tiếng Nhật, có thể tùy chỉnh lại wording trong các file page tương ứng.

## Cấu trúc thư mục chính

- `src/app/dashboard/page.tsx`: Trang dashboard tổng hợp.
- `src/app/students/page.tsx`: Trang danh sách học sinh.
- `src/app/teachers/page.tsx`: Trang danh sách giáo viên.
- `src/providers/`: Các provider lấy dữ liệu từ backend.
- `src/config/api.ts`: Cấu hình endpoint backend.

## License

MIT
