import report


def test_bo_qua_dong_thieu_amount(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("category,amount\nan,1000\nan,\n", encoding="utf-8")
    assert len(report.load_rows(str(p))) == 1


def test_cong_theo_nhom(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text('category,amount\nan,"1,000"\nan,500\n', encoding="utf-8")
    assert report.total_by_category(report.load_rows(str(p))) == {"an": 1500}
