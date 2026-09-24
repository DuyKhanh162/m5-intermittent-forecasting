# Lối tắt cho nhóm. Windows: nếu không có `make`, chạy trực tiếp lệnh python bên phải.
# Đặt PYTHONUTF8=1 để in tiếng Việt trên console Windows.

export PYTHONUTF8 = 1

.PHONY: setup data data-full test pilot notebook clean

setup:            ## Cài dependency (pin version)
	pip install -r requirements.txt

data:             ## Tải raw + sinh data_long cho MẪU (nhanh, ~30s)
	python scripts/download_data.py
	python -m src.data.build_long --scope sample

data-full:        ## Sinh data_long cho TOÀN BỘ 30.490 chuỗi (nặng, cần RAM)
	python -m src.data.build_long --scope full

test:             ## Chạy unit test (không cần raw data)
	python -m pytest tests/ -q

pilot:            ## Chạy lại smoke-test pipeline pilot từ notebook
	python tests/smoke_test.py

notebook:         ## Dựng lại notebook pilot từ build_notebook.py
	python build_notebook.py

clean:            ## Xoá cache
	python -c "import shutil,glob,os; [shutil.rmtree(p,ignore_errors=True) for p in glob.glob('**/__pycache__',recursive=True)+['.pytest_cache']]"
