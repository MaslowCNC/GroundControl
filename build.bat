python -m PyInstaller --clean --win-private-assemblies --onefile GroundControl.spec
rmdir build /s /Q
rmdir .\dist\GroundControl\gcodeForTesting /s /Q