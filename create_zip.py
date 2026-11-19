import os
import sys
import zipfile

ZIP_NAME = "redlamp_source_code.zip"

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "dataset",
    "pretrain",
    "result",
}

EXCLUDE_EXTENSIONS = {
    ".tex",
    ".md",
    ".bak",
    ".pyc",
    ".tmp",
    ".zip",
}

EXCLUDE_FILES = {
    ZIP_NAME,
    "create_zip.py",
    ".DS_Store",
}

# LaTeX generator scripts in scripts/ (since reports/latex are excluded)
EXCLUDE_SCRIPTS = {
    "latex_ch1_ch2.py",
    "latex_ch3_ch4.py",
    "latex_ch5_ch6_ch7.py",
    "latex_generator_parts.py",
    "make_sigconf.py",
    "generate_ieee_latex_report.py",
    "format_tables.py",
    "fix_formatting.py",
    "update_to_single_seed.py",
}

def should_include_file(root_dir: str, filename: str) -> bool:
    if filename in EXCLUDE_FILES:
        return False
    _, ext = os.path.splitext(filename)
    if ext.lower() in EXCLUDE_EXTENSIONS:
        return False
    norm_root = os.path.normpath(root_dir).replace("\\", "/")
    if norm_root.startswith("./"):
        norm_root = norm_root[2:]
    
    # Exclude latex report generators in scripts
    if norm_root == "scripts" and filename in EXCLUDE_SCRIPTS:
        return False
    
    return True

def create_zip():
    print(f"Creating zip file: {ZIP_NAME}...")
    file_list = []

    for root, dirs, files in os.walk("."):
        # Exclude directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]

        for f in files:
            if should_include_file(root, f):
                file_path = os.path.normpath(os.path.join(root, f))
                # Store in zip with forward slashes and without leading ./
                arcname = file_path.replace("\\", "/")
                if arcname.startswith("./"):
                    arcname = arcname[2:]
                file_list.append((file_path, arcname))

    file_list.sort(key=lambda x: x[1])

    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, arcname in file_list:
            zf.write(file_path, arcname)

    size_mb = os.path.getsize(ZIP_NAME) / (1024 * 1024)
    size_kb = os.path.getsize(ZIP_NAME) / 1024

    print("=" * 70)
    print(f"Zip created successfully: {ZIP_NAME}")
    print(f"Total files: {len(file_list)}")
    print(f"Zip file size: {size_mb:.2f} MB ({size_kb:.1f} KB)")
    print("=" * 70)

    print("\nContents of the zip file:")
    with zipfile.ZipFile(ZIP_NAME, "r") as zf:
        infolist = zf.infolist()
        for info in infolist:
            print(f"  {info.filename:<48} ({info.file_size / 1024:>7.1f} KB -> {info.compress_size / 1024:>7.1f} KB)")

if __name__ == "__main__":
    create_zip()
