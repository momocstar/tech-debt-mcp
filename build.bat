@echo off
REM 构建 tech-debt-mcp 可执行文件 (Windows)

echo === Tech-Debt-MCP 构建脚本 ===

REM 检查 Python
python --version

REM 安装构建依赖
echo.
echo 步骤 1/3: 安装构建依赖...
pip install pyinstaller -q

REM 安装项目依赖
echo 步骤 2/3: 安装项目依赖...
pip install -r requirements.txt -q

REM 构建
echo 步骤 3/3: 构建可执行文件...
pyinstaller tech-debt-mcp.spec --clean

echo.
echo === 构建完成 ===
echo 可执行文件位置: dist\tech-debt-mcp.exe
echo.
echo 使用方法 - 更新 MCP 配置:
echo.
echo {
echo   "mcpServers": {
echo     "tech-debt": {
echo       "command": "C:\\path\\to\\tech-debt-mcp\\dist\\tech-debt-mcp.exe",
echo       "env": {
echo         "CKJM_JAR": "C:\\path\\to\\tech-debt-mcp\\ckjm-1.9.jar",
echo         "SONARQUBE_URL": "http://sonar.example.com",
echo         "SONARQUBE_TOKEN": "your_token_here",
echo         "ANTHROPIC_API_KEY": "your_api_key_here"
echo       }
echo     }
echo   }
echo }

pause