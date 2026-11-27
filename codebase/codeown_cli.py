"""Điểm vào cho hook và extension khi không đứng trong thư mục codebase/.

  python codebase/codeown_cli.py <lệnh> ...   ==   (cd codebase && python -m codeown <lệnh> ...)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codeown.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
