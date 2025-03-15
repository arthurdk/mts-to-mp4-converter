# MTS to MP4 Converter

A simple, multi-threaded application to convert MTS video files to MP4 format using FFmpeg.

## Features

- Easy-to-use graphical interface
- Batch conversion capabilities
- Multi-threaded processing for faster conversions
- Progress tracking and status updates
- Original MTS files are preserved after conversion

## Requirements

- Python 3.6 or higher
- FFmpeg
- Tkinter (included in most Python installations)

## Installation Instructions

### 1. Install Python

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/windows/)
2. Run the installer (make sure to check "Add Python to PATH" during installation)
3. Verify installation by opening Command Prompt and typing: `python --version`

#### macOS
1. Install using Homebrew (recommended):
   ```
   brew install python
   ```
   
   Or download from [python.org](https://www.python.org/downloads/macos/)
2. Verify installation by opening Terminal and typing: `python3 --version`

#### Linux
Most Linux distributions come with Python pre-installed. If not:

1. Debian/Ubuntu:
   ```
   sudo apt update
   sudo apt install python3 python3-pip python3-tk
   ```

2. Fedora:
   ```
   sudo dnf install python3 python3-pip python3-tkinter
   ```

3. Verify installation: `python3 --version`

### 2. Install FFmpeg

#### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) or use a distribution like [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the files and add the `bin` directory to your PATH environment variable
3. Verify installation: `ffmpeg -version`

#### macOS
1. Install using Homebrew:
   ```
   brew install ffmpeg
   ```
2. Verify installation: `ffmpeg -version`

#### Linux
1. Debian/Ubuntu:
   ```
   sudo apt update
   sudo apt install ffmpeg
   ```

2. Fedora:
   ```
   sudo dnf install ffmpeg
   ```

3. Verify installation: `ffmpeg -version`

### 3. Install Tkinter (if not already installed)

#### Windows
Tkinter is included with Python for Windows.

#### macOS
Tkinter should be included with Python installed via Homebrew or python.org. If you encounter issues:

1. **Check if Tkinter is already installed**:
   ```
   python3 -c "import tkinter; tkinter._test()"
   ```
   If a window appears, Tkinter is working correctly.

2. **Install or reinstall with Homebrew**:
   ```
   brew install python-tk
   ```
   or if Python is already installed:
   ```
   brew reinstall python-tk
   ```

3. **If you still have problems**:
   ```
   brew install tcl-tk
   brew reinstall python
   ```

4. **For specific troubleshooting with Tkinter on macOS**:
   - Errors like "No module named '_tkinter'" indicate missing Tkinter binaries
   - Errors like "Segmentation fault: 11" may be due to compatibility issues
   - Try installing a specific Python version: `brew install python@3.9`
   - You might need to configure the path to Homebrew's Tcl/Tk:
     ```
     echo 'export PATH="/usr/local/opt/tcl-tk/bin:$PATH"' >> ~/.zshrc
     export LDFLAGS="-L/usr/local/opt/tcl-tk/lib"
     export CPPFLAGS="-I/usr/local/opt/tcl-tk/include"
     ```

#### Linux
1. Debian/Ubuntu:
   ```
   sudo apt install python3-tk
   ```

2. Fedora:
   ```
   sudo dnf install python3-tkinter
   ```

### 4. Download the Application

1. Download the MTS Converter files
2. Extract the ZIP file (if applicable) to a location of your choice

## Running the Application

### Windows

Option 1: Double-click the `mts_converter_gui.py` file if Python is properly associated with .py files.

Option 2: Open Command Prompt:
```
cd path\to\extracted\folder
python mts_converter_gui.py
```

### macOS

Option 1: Open Terminal:
```
cd /path/to/extracted/folder
python3 mts_converter_gui.py
```

Option 2: Make the script executable and double-click:
```
chmod +x mts_converter_gui.py
```

### Linux

Option 1: Open Terminal:
```
cd /path/to/extracted/folder
python3 mts_converter_gui.py
```

Option 2: Make the script executable and double-click:
```
chmod +x mts_converter_gui.py
```

## Usage Instructions

1. Click "Select MTS Files" to choose the files you want to convert
2. Adjust the number of parallel conversions if desired (default is 75% of CPU cores)
3. Click "Start Conversion" to begin the process
4. Monitor progress in the status area
5. When conversion is complete, the MP4 files will be in the same directory as the original files
6. The original MTS files are preserved and not deleted

## Troubleshooting

- **FFmpeg Not Found**: Make sure FFmpeg is properly installed and in your system PATH
- **Missing Tkinter**: Install the python-tk package for your operating system
- **Permission Issues**: Try running the application with administrator/root privileges
- **Conversion Failures**: Check that the MTS files are valid and not corrupted

## License

This software is provided as-is with no warranties.
