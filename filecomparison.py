import os
import tkinter as tk
from tkinter import filedialog
import tempfile
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class FileInfo:
    """Class to store file information"""
    path: str
    size: int

def select_folder():
    """Opens folder selection dialog and returns the selected path"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(title="Select Folder")
    return folder_path

def get_file_info(folder_path) -> Dict[str, FileInfo]:
    """Gets dictionary of files with their sizes from the specified folder"""
    file_dict = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            # Get relative path from the selected folder
            rel_path = os.path.relpath(file_path, folder_path)
            file_dict[rel_path] = FileInfo(rel_path, size)
    return file_dict

def write_to_temp_file(file_info: Dict[str, FileInfo], prefix: str) -> str:
    """Writes file information to a temporary file"""
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        prefix=prefix,
        suffix='.txt',
        delete=False
    )
    with temp_file as f:
        for file_path, info in file_info.items():
            f.write(f"{info.path}\t{info.size} bytes\n")
    return temp_file.name

def compare_files(files1: Dict[str, FileInfo], files2: Dict[str, FileInfo]) -> tuple[List[str], List[str]]:
    """
    Compares two file dictionaries and returns:
    - List of files in files1 that don't exist in files2
    - List of files that exist in both but have different sizes
    """
    missing_files = []
    size_mismatch_files = []

    for fname1, info1 in sorted(files1.items()):  # Sort for consistent output
        if fname1 not in files2:
            missing_files.append(f"[{os.path.basename(info1.path)} || {info1.path}]")
        else:
            if info1.size != files2[fname1].size:
                size_mismatch_files.append(
                    f"[{os.path.basename(info1.path)} || {info1.path} || {info1.size} bytes vs {files2[fname1].size} bytes]")

    return missing_files, size_mismatch_files

def generate_report(folder1: str, folder2: str, missing_files: List[str], size_mismatch_files: List[str]) -> str:
    """Generates the final report in the specified format"""
    report_filename = "Report-File.txt"
    
    with open(report_filename, 'w') as f:
        f.write("File Comparison Report\n")
        f.write("=====================\n\n")
        
        f.write("Legend:\n")
        f.write(f"Folder 1 name and path = {folder1}\n")
        f.write(f"Folder 2 name and path = {folder2}\n")
        
        f.write("=====================================\n")
        f.write(f"List of Files that exist in {os.path.basename(folder1)} folder (Longer list) ")
        f.write(f"and not in {os.path.basename(folder2)} folder (Short list)\n")
        f.write("=====================================\n")
        
        # Write missing files in the specified format
        for missing_file in missing_files:
            f.write(f"{missing_file}\n")
        
        # Add dots to indicate continuation if there are more files
        if missing_files:
            f.write(".\n" * 4)  # Four dots on separate lines
        
        f.write("\n=====================================\n")
        f.write("List of Files with Different Sizes in Both Folders\n")
        f.write("=====================================\n")
        
        for mismatch_file in size_mismatch_files:
            f.write(f"{mismatch_file}\n")
            
    return report_filename

def main():
    print("Please select the first folder...")
    folder1 = select_folder()
    if not folder1:
        print("No folder selected. Exiting...")
        return

    print("Please select the second folder...")
    folder2 = select_folder()
    if not folder2:
        print("No folder selected. Exiting...")
        return

    # Get file information for both folders
    files1 = get_file_info(folder1)
    files2 = get_file_info(folder2)

    # Write original file lists to temporary files
    temp1_path = write_to_temp_file(files1, 'folder1_')
    temp2_path = write_to_temp_file(files2, 'folder2_')

    # Determine which file list to use as primary comparison
    if len(files1) > len(files2):
        primary_files = files1
        secondary_files = files2
        primary_path = folder1
        secondary_path = folder2
    else:
        primary_files = files2
        secondary_files = files1
        primary_path = folder2
        secondary_path = folder1

    # Compare files
    missing_files, size_mismatch_files = compare_files(primary_files, secondary_files)

    # Generate the final report
    report_path = generate_report(primary_path, secondary_path, missing_files, size_mismatch_files)

    print(f"\nTemporary files have been written to:")
    print(f"Folder 1 contents: {temp1_path}")
    print(f"Folder 2 contents: {temp2_path}")
    print(f"\nFinal report has been generated: {report_path}")

if __name__ == "__main__":
    main()
