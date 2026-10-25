# 🦐 HỆ THỐNG QUẢN LÝ VÀ ĐẾM SỐ LƯỢNG TÔM THÔNG MINH BẰNG GIỌNG NÓI TIẾNG VIỆT
*(Smart Vietnamese Voice-Activated Shrimp Counter & Classifier - Google STT & Vietnamese TTS)*

Hệ thống phần mềm máy tính chuyên dụng cho các trại tôm giống và ao nuôi tôm thịt. Tối ưu hóa toàn diện cho môi trường sản xuất thực tế:
- **Nhận diện giọng nói chuẩn tiếng Việt**: Sử dụng Google Speech Recognition trực tuyến (`vi-VN`) kết hợp bảng ánh xạ số tự động, không ngốn CPU, không lag, không lỗi lặp từ.
- **Phát giọng đọc tiếng Việt (TTS)**: Đọc lại chính xác số liệu vừa nhập qua loa/tai nghe (ví dụ: *"Đã lưu 45 gam đực"*, *"Đã thêm 5 con, tổng 55"*).
- **Bộ lọc câu thông minh (Chống nhiễu khi nói chuyện phiếm)**: Tự động phát hiện và bỏ qua các câu hội thoại ngoài ao (như *"hôm nay nắng quá"*, *"cho tôm ăn chưa"*).
- **Thống kê Size tôm tự động**: Tự động tính toán và hiển thị kích cỡ tôm trung bình (con/kg và con/g) trực quan.

---

## 🌟 CÁC TÍNH NĂNG NỔI BẬT

### 1. Cấu Trúc Giao Diện Chung & Micro Rảnh Tay
- **Header quản lý**: Ô nhập trực quan **Tên Ao Nuôi / Mã Lô** và **Tên Nhân Viên**.
- **Nút lớn BẬT/TẮT MICRO**: Lắng nghe liên tục trong background thread, tự ngắt câu nhanh (0.65s).
- **Lọc ồn ao nuôi**: Nút **"🌊 Hiệu Chuẩn Lọc Ồn Ao"** và thanh trượt năng lượng triệt tiêu tiếng sục khí oxy và quạt nước.
- **Tùy chọn bật/tắt & tăng tốc độ đọc lại số liệu (TTS)**:
  - Có thể bật/tắt đọc lại bằng giọng nói ngay trên thanh điều khiển.
  - **Tùy chỉnh tốc độ đọc linh hoạt (Speech Rate)**: Hỗ trợ các mức tốc độ `x1.0 (Chuẩn)`, `x1.2 (Nhanh vừa)`, `x1.3 (Mặc định tối ưu)`, `x1.5 (Rất nhanh)`, `x1.8 (Siêu tốc)` bằng bộ lọc FFmpeg `atempo` giữ nguyên cao độ giọng nói, cực kỳ rõ ràng và dứt khoát. Có thể đổi qua Combobox trên GUI hoặc chỉnh biến `DEFAULT_TTS_SPEED_RATE` trong `app.py`.

### 2. Chế Độ 1: Cân Trọng Lượng & Phân Loại Giới Tính ("Male" / "Female")
- **Bảng dữ liệu**: `STT`, `Trọng Lượng (g)`, `Giới Tính`, `Thời Gian Nhận Diện`.
- **Cú pháp giọng nói thông minh**: `[Số trọng lượng] + [giới tính]`.
  - **Giống Đực**: Nhận diện các từ khóa **"trai", "chai", "đực", "tai"** -> Cột Giới Tính lưu và hiển thị chữ **"Male"**.
    - Ví dụ: *"35 trai"*, *"35 chai"*, *"40 đực"*, *"50 tai"*, *"ba mươi lăm trai"*, *"ba lăm chai"*, *"năm hai đực"*.
  - **Giống Cái**: Nhận diện các từ khóa **"cái", "gái", "ái"** -> Cột Giới Tính lưu và hiển thị chữ **"Female"**.
    - Ví dụ: *"45 cái"*, *"38 gái"*, *"25 ái"*, *"bốn lăm gái"*, *"ba lăm cái"*.
  - **Không đọc giới tính**: Tự động gán là **"Chưa rõ"** (ví dụ *"ba mươi lăm"*, *"45"*).
- **Đọc lại bằng giọng nói**: Tự động phát giọng đọc xác nhận qua tai nghe: *"Đã lưu 35 gam Male"*, *"Đã lưu 45 gam Female"*, *"Đã lưu 50 gam"*.
- **Ô Thống Kê Size Tôm Trung Bình**:
  - Hiển thị ô nổi bật: `🦐 SIZE TÔM TRUNG BÌNH`.
  - Công thức: $\text{Size (con/kg)} = \frac{\text{Tổng số con}}{\text{Tổng trọng lượng (g)}} \times 1000$.
  - Hiển thị chi tiết cả tỷ lệ chuẩn con/kg và con/g để kỹ thuật viên tiện theo dõi.
- **Tự động lưu**: Ghi nhận và đồng bộ tức thì vào file Excel `Bao_Cao_Tom.xlsx` (Cột Giới Tính lưu **"Male"** hoặc **"Female"**).

### 3. Chế Độ 2: Đếm Số Lượng Cộng Dồn Tốc Độ Cao
- **Hiển thị số cực lớn**: Ô số **Font 56 bold** hiển thị `TỔNG SỐ TÔM ĐÃ ĐẾM` với hiệu ứng chớp màu xanh neon phản hồi.
- **Bảng ánh xạ dịch từ chữ sang số tự động**:
  - Google trả về chữ: *"sáu"* $\rightarrow$ 6, *"mười"* $\rightarrow$ 10, *"mười lăm"* $\rightarrow$ 15, *"hai lăm"* $\rightarrow$ 25, *"ba lăm"* $\rightarrow$ 35...
  - Google trả về số: *"6"* $\rightarrow$ 6, *"10"* $\rightarrow$ 10, *"15"* $\rightarrow$ 15...
  - Tự động cộng dồn ngay lập tức vào tổng số tôm.
- **Đọc lại bằng giọng nói**: Phát âm thanh xác nhận: *"Đã thêm 5 con, tổng 55"*.
- **Cơ chế sửa sai rảnh tay (Undo)**:
  - Khi bốc nhầm hoặc đọc sai, người dùng chỉ cần hô: **"XÓA"** hoặc **"HỦY"**.
  - Phần mềm tự động trừ bớt số lượng mẻ vừa cộng gần nhất, phát âm thanh lùi nốt và đọc lại: *"Đã hủy 5 con, tổng còn 50"*.

### 4. Lệnh Giọng Nói: "Xóa Dòng Cuối" & "Xóa Sạch Về 0" (Cả Chế Độ 1 & 2)
- **Chức năng 1 - Xóa dòng cuối cùng (Sửa sai rảnh tay)**:
  - Hô: **"XÓA"**, **"HỦY"**, hoặc **"XÓA DÒNG"**.
  - Phần mềm tự động loại bỏ dòng dữ liệu cuối cùng vừa chèn của chế độ đang mở.
  - Phản hồi: Loa AI đọc xác nhận qua TTS: *"Đã xóa dòng cuối"*.
- **Chức năng 2 - Xóa sạch toàn bộ (Reset về 0)**:
  - Hô: **"XÓA HẾT"**, **"XÓA TẤT CẢ"**, hoặc **"RESET"**.
  - Phần mềm xóa sạch sành sanh tất cả các dòng dữ liệu trong bảng, đặt lại Tổng tích lũy số lượng tôm và số mẻ về 0.
  - Phản hồi an toàn: Trước khi xóa sạch, AI đọc loa cảnh báo: *"Đang xóa toàn bộ dữ liệu"*.

### 5. Logic Lọc Câu Nói Chuyện Phiếm Ngoài Ao
- Khi kỹ thuật viên nói chuyện với nhau ngoài ao (ví dụ: *"hôm nay nắng quá"*, *"cho tôm ăn chưa"*, *"đi uống cà phê đi"*):
  - Phần mềm tự động phân tích: nếu câu **không chứa số** và **không chứa các từ khóa chuyên dụng** (`đực`, `cái`, `trai`, `chai`, `tai`, `gái`, `ái`, `xóa`, `hủy`, `reset`, `undo`), hệ thống sẽ **bỏ qua hoàn toàn**, không ghi dữ liệu sai lệch.

### 6. Xuất Báo Cáo Excel Đạt Chuẩn Thẩm Mỹ Chuyên Nghiệp Bậc Cao (openpyxl)
- Nút **"📊 XUẤT BÁO CÁO EXCEL"**:
  - **Thông tin chung (Dòng 1-4)**: Tiêu đề `"BÁO CÁO DỮ LIỆU ĐẾM TÔM THÔNG MINH"` (Font 16 Bold, Navy Blue `#1F4E78`), Tên Ao Nuôi, Nhân Viên Cân, Ngày Giờ Xuất Báo Cáo. Toàn bộ khu vực này tô nền xám nhạt (Light Gray `#F2F2F2`).
  - **Thanh tiêu đề bảng (Header - Dòng 6)**: Chiều cao 26, nền Navy Blue `#1F4E78`, chữ màu trắng, Font Calibri 11 Bold, căn lề giữa.
  - **Dòng dữ liệu (Dòng 7+)**: Chiều cao 20, Font Calibri 10, viền mỏng xám gọn gàng. Cột STT, Giới tính, Thời gian căn giữa; Trọng lượng, Số lượng căn phải và định dạng chuẩn (`0.0` và `#,##0`).
  - **Dòng tổng kết (Total Row)**: Sử dụng công thức Excel (`=AVERAGE(...)` cho trọng lượng TB, `=SUM(...)` cho tổng số tôm), In đậm, có đường gạch chân kép (double) chuẩn kế toán.
  - **Tự động giãn cột (Auto-fit)**: Tự động đo độ dài nội dung để giãn cột an toàn, chống tràn và không bị lỗi hiển thị `"###"`.

---

## 📦 HƯỚNG DẪN ĐÓNG GÓI THÀNH FILE .EXE CÀI ĐẶT DUY NHẤT

Dự án đã được tích hợp sẵn công cụ đóng gói bằng **PyInstaller** (`build.bat` và `build_exe.py`):

1. **Cách tạo file .EXE**:
   - Nhấp đúp chuột vào file **`build.bat`** (hoặc mở Terminal chạy lệnh `python build_exe.py`).
   - PyInstaller sẽ tự động gom toàn bộ thư viện, giao diện GUI, tài nguyên âm thanh cache và cấu hình vào một file thực thi duy nhất.
   - File kết quả nằm tại: **`dist\ShrimpSmartCounter.exe`** (Dung lượng siêu gọn nhẹ ~89 MB, không cần cài đặt Python hay thư viện trên máy đích).

---

## 🌐 HƯỚNG DẪN CHIA SẺ CHO NGƯỜI NUÔI TÔM

### Cách 1: Chia sẻ qua Google Drive (Dễ nhất và phổ biến nhất)
1. **Tải file lên Drive**:
   - Mở trình duyệt vào [Google Drive](https://drive.google.com).
   - Bấm nút **Mới (+)** $\rightarrow$ **Tải tệp lên** $\rightarrow$ Chọn file `dist\ShrimpSmartCounter.exe`.
2. **Lấy link công khai**:
   - Nhấp chuột phải vào file `ShrimpSmartCounter.exe` vừa tải lên $\rightarrow$ Chọn **Chia sẻ (Share)**.
   - Tại mục **Quyền truy cập chung (General Access)**, đổi từ *Hạn chế* sang **"Bất kỳ ai có đường liên kết" (Anyone with the link)** với vai trò là **"Người xem" (Viewer)**.
   - Bấm **Sao chép đường liên kết (Copy Link)**.
3. **Mẹo tạo link tải trực tiếp (1-Click Direct Download)**:
   - Link chia sẻ Google Drive có dạng: `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
   - Bạn chỉ cần copy đoạn mã `FILE_ID` và ghép thành:
     `https://drive.google.com/uc?export=download&id=FILE_ID`
   - Người nuôi tôm chỉ cần bấm vào link là file `.exe` tự động tải về máy tính ngay!

---

### Cách 2: Chia sẻ qua GitHub Releases (Chuyên nghiệp, tốc độ tải cực cao)
1. Vào trang Repository dự án trên GitHub (ví dụ `https://github.com/username/shrimp_counter_app`).
2. Ở cột bên phải, nhấp vào mục **Releases** $\rightarrow$ Bấm **Draft a new release** (hoặc *Create a new release*).
3. Điền thông tin:
   - **Choose a tag**: Nhập tag phiên bản (ví dụ: `v1.0.0`).
   - **Release title**: Ví dụ *"Phần mềm Đếm Tôm Thông Minh bằng Giọng Nói v1.0"*.
   - **Describe this release**: Ghi tóm tắt tính năng (nhận diện giọng nói tiếng Việt, tự động đọc lại, xuất Excel chuyên nghiệp).
4. **Đính kèm file EXE**:
   - Kéo thả file `dist\ShrimpSmartCounter.exe` vào khung *"Attach binaries by dropping them here or selecting them"*.
5. Bấm **Publish release**.
6. **Lấy link**: Chuột phải vào tên file `ShrimpSmartCounter.exe` trong bản Release vừa tạo $\rightarrow$ Chọn **Copy link address**. Người dùng chỉ cần nhấp vào link là tải về ngay với tốc độ tối đa của GitHub CDN.

1. Vào thư mục `shrimp_counter_app` và nhấp đúp vào **`run.bat`**.
2. Nhập thông tin **Ao nuôi** và **Tên nhân viên**.
3. Bấm nút **"🌊 Hiệu Chuẩn Lọc Ồn Ao"** để AI học tiếng quạt nước/sục khí trong 1.5 giây.
4. Bật micro bằng nút **"🎤 BẬT MICRO (RẢNH TAY)"** và bắt đầu làm việc:
   - **Tab 1**: Đọc *"ba mươi lăm đực"*, *"bốn lăm cái"*. Loa sẽ đọc xác nhận *"Đã lưu 35 gam đực"*, ô Size tôm sẽ tự động cập nhật.
   - **Tab 2**: Đọc *"năm"*, *"mười"*, *"mười lăm"*. Loa sẽ đọc xác nhận *"Đã thêm 10 con, tổng 25"*. Nếu cần sửa sai, chỉ cần đọc *"xóa"* hoặc *"hủy"*.
5. Bấm **"📊 XUẤT BÁO CÁO EXCEL"** để lưu file `Bao_Cao_Tom.xlsx`.
