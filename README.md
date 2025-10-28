# prodigiAlly
Remote barcode tracking software for windows/mac systems that connects and updates and to local server program



python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "Prodigi Ally - Standard Station" ^
  --icon "MyAppIcon.ico" ^
  --add-data ".\images;images" ^
  .\main.py
