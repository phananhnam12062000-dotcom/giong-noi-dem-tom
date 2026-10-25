import os
import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_or_update_excel(
    file_path: str,
    pond_name: str,
    staff_name: str,
    weight_records: list, # [{'stt': 1, 'weight': 35.0, 'gender': 'Đực', 'time': '16:00:05'}, ...]
    batch_records: list,  # [{'stt': 1, 'batch_name': 'Mẻ 1', 'count': 10, 'cumulative': 10, 'time': '16:01:00'}, ...]
    total_batch_count: int
):
    """
    Creates or updates the Excel report with two professionally styled sheets.
    """
    wb = Workbook()
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)

    # Styles
    title_font = Font(name='Arial', size=15, bold=True, color='FFFFFF')
    title_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')

    meta_label_font = Font(name='Arial', size=11, bold=True, color='333333')
    meta_val_font = Font(name='Arial', size=11, color='1F4E79', bold=True)
    meta_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

    header_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

    summary_box_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
    summary_box_font = Font(name='Arial', size=11, bold=True, color='1F4E79')

    thin_border_side = Side(border_style="thin", color="D9D9D9")
    box_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    header_border = Border(
        left=Side(style='thin', color='FFFFFF'),
        right=Side(style='thin', color='FFFFFF'),
        top=Side(style='medium', color='1F4E79'),
        bottom=Side(style='medium', color='1F4E79')
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # ==================== SHEET 1: CÂN TRỌNG LƯỢNG & GIỚI TÍNH ====================
    ws1 = wb.create_sheet(title="Can_Trong_Luong_Gioi_Tinh")
    ws1.views.sheetView[0].showGridLines = True

    # Title
    ws1.merge_cells('A1:D1')
    cell1 = ws1['A1']
    cell1.value = "BÁO CÁO CÂN TRỌNG LƯỢNG & PHÂN LOẠI GIỚI TÍNH TÔM"
    cell1.font = title_font
    cell1.fill = title_fill
    cell1.alignment = align_center
    ws1.row_dimensions[1].height = 40

    # Metadata
    ws1['A3'] = "Tên Ao Nuôi / Mã Lô:"
    ws1['A3'].font = meta_label_font
    ws1['B3'] = pond_name if pond_name else "Chưa đặt tên ao"
    ws1['B3'].font = meta_val_font

    ws1['C3'] = "Thời Gian Xuất:"
    ws1['C3'].font = meta_label_font
    ws1['D3'] = now_str
    ws1['D3'].font = meta_val_font

    ws1['A4'] = "Nhân Viên Thực Hiện:"
    ws1['A4'].font = meta_label_font
    ws1['B4'] = staff_name if staff_name else "Chưa nhập nhân viên"
    ws1['B4'].font = meta_val_font

    # Summary statistics calculation
    total_weighed = len(weight_records)
    avg_weight = sum(r['weight'] for r in weight_records) / total_weighed if total_weighed > 0 else 0
    male_count = sum(1 for r in weight_records if r['gender'] == 'Đực')
    female_count = sum(1 for r in weight_records if r['gender'] == 'Cái')
    unknown_count = sum(1 for r in weight_records if r['gender'] not in ('Đực', 'Cái'))

    # Summary block in Sheet 1
    ws1.merge_cells('A6:D6')
    s_cell = ws1['A6']
    s_cell.value = f"THỐNG KÊ NHANH: Tổng mẫu: {total_weighed} con | Trọng lượng TB: {avg_weight:.1f}g | Đực: {male_count} con | Cái: {female_count} con | Chưa rõ: {unknown_count} con"
    s_cell.font = summary_box_font
    s_cell.fill = summary_box_fill
    s_cell.alignment = align_center
    ws1.row_dimensions[6].height = 25

    # Table Header
    headers1 = ["STT", "Trọng Lượng (g)", "Giới Tính", "Thời Gian Ghi Nhận"]
    for col_idx, h in enumerate(headers1, 1):
        c = ws1.cell(row=8, column=col_idx)
        c.value = h
        c.font = header_font
        c.fill = header_fill
        c.alignment = align_center
        c.border = header_border
    ws1.row_dimensions[8].height = 26

    # Data rows
    row_curr = 9
    for r in weight_records:
        ws1.cell(row=row_curr, column=1, value=r['stt']).alignment = align_center
        ws1.cell(row=row_curr, column=2, value=r['weight']).alignment = align_right
        ws1.cell(row=row_curr, column=3, value=r['gender']).alignment = align_center
        ws1.cell(row=row_curr, column=4, value=r['time']).alignment = align_center

        for c_idx in range(1, 5):
            ws1.cell(row=row_curr, column=c_idx).border = box_border
            ws1.cell(row=row_curr, column=c_idx).font = Font(name='Arial', size=10)
        row_curr += 1

    # Auto column width for Sheet 1
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 15)

    # ==================== SHEET 2: ĐẾM SỐ LƯỢNG CỘNG DỒN ====================
    ws2 = wb.create_sheet(title="Dem_So_Luong_Cong_Don")
    ws2.views.sheetView[0].showGridLines = True

    # Title
    ws2.merge_cells('A1:E1')
    cell2 = ws2['A1']
    cell2.value = "BÁO CÁO ĐẾM SỐ LƯỢNG TÔM CỘNG DỒN TỐC ĐỘ CAO"
    cell2.font = title_font
    cell2.fill = title_fill
    cell2.alignment = align_center
    ws2.row_dimensions[1].height = 40

    # Metadata
    ws2['A3'] = "Tên Ao Nuôi / Mã Lô:"
    ws2['A3'].font = meta_label_font
    ws2['B3'] = pond_name if pond_name else "Chưa đặt tên ao"
    ws2['B3'].font = meta_val_font

    ws2['D3'] = "Thời Gian Xuất:"
    ws2['D3'].font = meta_label_font
    ws2['E3'] = now_str
    ws2['E3'].font = meta_val_font

    ws2['A4'] = "Nhân Viên Thực Hiện:"
    ws2['A4'].font = meta_label_font
    ws2['B4'] = staff_name if staff_name else "Chưa nhập nhân viên"
    ws2['B4'].font = meta_val_font

    # Summary box
    ws2.merge_cells('A6:E6')
    s2_cell = ws2['A6']
    total_valid_batches = len([b for b in batch_records if b.get('action') != 'UNDO'])
    s2_cell.value = f"TỔNG SỐ TÔM ĐÃ ĐẾM: {total_batch_count} con  |  Tổng số mẻ: {total_valid_batches} mẻ"
    s2_cell.font = Font(name='Arial', size=13, bold=True, color='C00000')
    s2_cell.fill = summary_box_fill
    s2_cell.alignment = align_center
    ws2.row_dimensions[6].height = 30

    # Table Header
    headers2 = ["STT", "Mã Mẻ", "Số Lượng Mỗi Mẻ (Con)", "Tổng Tích Lũy (Con)", "Thời Gian Ghi Nhận"]
    for col_idx, h in enumerate(headers2, 1):
        c = ws2.cell(row=8, column=col_idx)
        c.value = h
        c.font = header_font
        c.fill = header_fill
        c.alignment = align_center
        c.border = header_border
    ws2.row_dimensions[8].height = 26

    # Data rows
    row_curr = 9
    for r in batch_records:
        ws2.cell(row=row_curr, column=1, value=r['stt']).alignment = align_center
        ws2.cell(row=row_curr, column=2, value=r['batch_name']).alignment = align_center
        ws2.cell(row=row_curr, column=3, value=r['count']).alignment = align_right
        ws2.cell(row=row_curr, column=4, value=r['cumulative']).alignment = align_right
        ws2.cell(row=row_curr, column=5, value=r['time']).alignment = align_center

        for c_idx in range(1, 6):
            cell = ws2.cell(row=row_curr, column=c_idx)
            cell.border = box_border
            cell.font = Font(name='Arial', size=10)
            if r.get('action') == 'UNDO':
                cell.fill = PatternFill(start_color='FFEEEE', end_color='FFEEEE', fill_type='solid')
                cell.font = Font(name='Arial', size=10, color='999999', strike=True)

        row_curr += 1

    # Auto column width for Sheet 2
    for col in ws2.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws2.column_dimensions[col_letter].width = max(max_len + 4, 18)

    wb.save(file_path)
    return True

if __name__ == '__main__':
    test_weights = [
        {'stt': 1, 'weight': 35.0, 'gender': 'Đực', 'time': '16:01:05'},
        {'stt': 2, 'weight': 42.5, 'gender': 'Cái', 'time': '16:01:12'},
        {'stt': 3, 'weight': 50.0, 'gender': 'Đực', 'time': '16:01:20'},
        {'stt': 4, 'weight': 38.0, 'gender': 'Chưa rõ', 'time': '16:01:30'},
    ]
    test_batches = [
        {'stt': 1, 'batch_name': 'Mẻ 1', 'count': 5, 'cumulative': 5, 'time': '16:02:00', 'action': 'ADD'},
        {'stt': 2, 'batch_name': 'Mẻ 2', 'count': 10, 'cumulative': 15, 'time': '16:02:10', 'action': 'ADD'},
        {'stt': 3, 'batch_name': 'Mẻ 3', 'count': 15, 'cumulative': 30, 'time': '16:02:25', 'action': 'ADD'},
    ]
    test_path = "C:\\Users\\Asus\\.gemini\\antigravity\\scratch\\shrimp_counter_app\\Bao_Cao_Tom_Test.xlsx"
    create_or_update_excel(
        test_path,
        pond_name="Ao Số 3 - Khu A",
        staff_name="Nguyễn Văn A",
        weight_records=test_weights,
        batch_records=test_batches,
        total_batch_count=30
    )
    print(f"Exported successfully to {test_path}!")
