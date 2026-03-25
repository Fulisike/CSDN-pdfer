# CSDN PDFer - Distribution Guide

## Distribution Package Contents

When you distribute CSDN-PDFer, you need to include these 3 files in the same folder:

```
CSDN-PDFer/
├── CSDN-PDFer.exe      # Main application
├── wkhtmltopdf.exe     # PDF generation engine
└── wkhtmltox.dll       # Required library for PDF generation
```

## How to Build

Run the build script:
```bash
build_exe_simple.bat
```

This will:
1. Build CSDN-PDFer.exe
2. Copy wkhtmltopdf.exe and wkhtmltox.dll to the dist folder
3. Create a complete package in the `dist` folder

## How to Distribute

1. Go to the `dist` folder
2. Copy all 3 files
3. Distribute them together (zip file, folder, etc.)
4. Users just need to extract all files to the same folder and run CSDN-PDFer.exe

## User Requirements

None! The package includes everything needed:
- No Python installation required
- No wkhtmltopdf installation required
- Just extract and run

## Notes

- All 3 files MUST be in the same folder
- The exe will automatically find wkhtmltopdf.exe in its directory
- Do not rename wkhtmltopdf.exe or wkhtmltox.dll
