python -m PyInstaller --clean --win-private-assemblies --onefile GroundControl.spec
rmdir build /s /Q
rmdir .\dist\GroundControl\.git /s /Q
rmdir .\dist\GroundControl\build /s /Q
rmdir .\dist\GroundControl\Connection /s /Q
rmdir .\dist\GroundControl\DataStructures /s /Q
rmdir .\dist\GroundControl\Documentation /s /Q
rmdir .\dist\GroundControl\Simulation /s /Q
rmdir .\dist\GroundControl\UIElements /s /Q
robocopy /E ./Documentation ./dist/GroundControl/Documentation
robocopy /E ./gcodeForTesting ./dist/gcodeForTesting
copy "./Launch Ground Control.bat" "./dist/Launch Ground Control.bat"
robocopy /E ./dist ./GroundControl-Windows.Portable.v0.
rmdir .\dist /s /Q