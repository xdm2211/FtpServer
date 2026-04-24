$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot

$venvPath = Join-Path $projectRoot "venv"
$activateScript = Join-Path $venvPath "Scripts\\Activate.ps1"
$sourceFile = Join-Path $projectRoot "ftpServer.py"

if (-not (Test-Path -LiteralPath $sourceFile)) {
    throw "未找到源文件: $sourceFile"
}

if (-not (Test-Path -LiteralPath $activateScript)) {
    throw "未找到虚拟环境激活脚本: $activateScript"
}

$versionPattern = '^\s*appVersion\s*=\s*"v(\d+)\.(\d+)(?:\.(\d+))?"\s*$'
$versionLine = Select-String -Path $sourceFile -Pattern $versionPattern | Select-Object -First 1
if (-not $versionLine) {
    throw "未找到符合格式的 appVersion 行。"
}

$match = [regex]::Match($versionLine.Line, $versionPattern)
if (-not $match.Success) {
    throw "无法解析版本号: $($versionLine.Line)"
}

$major = $match.Groups[1].Value
$minor = $match.Groups[2].Value
$patch = $match.Groups[3].Value

if ([string]::IsNullOrEmpty($patch)) {
    $productVersion = "$major.$minor.0.0"
}
else {
    $productVersion = "$major.$minor.$patch.0"
}
$expectedVenv = [System.IO.Path]::GetFullPath($venvPath)
$currentVenv = $null

if ($env:VIRTUAL_ENV) {
    $currentVenv = [System.IO.Path]::GetFullPath($env:VIRTUAL_ENV)
}

if ($currentVenv -ne $expectedVenv) {
    . $activateScript
}

$commonArgs = @(
    ".\\ftpServer.py"
    "--windows-icon-from-ico=.\\ftpServer.ico"
    "--standalone"
    "--lto=yes"
    "--python-flag=-O"
    "--enable-plugin=tk-inter"
    "--windows-console-mode=disable"
    "--company-name=JARK006"
    "--product-name=ftpServer"
    "--file-version=$productVersion"
    "--product-version=$productVersion"
    "--file-description=FtpServer Github@JARK006"
    "--copyright=Copyright (C) 2023-2026 Github@JARK006"
)

Write-Host "使用虚拟环境: $env:VIRTUAL_ENV"
Write-Host "打包版本号: $productVersion"
Write-Host "开始打包单文件版本..."
& python -m nuitka @commonArgs --onefile
if ($LASTEXITCODE -ne 0) {
    throw "单文件版本打包失败。"
}

Write-Host "开始打包单目录版本..."
& python -m nuitka @commonArgs
if ($LASTEXITCODE -ne 0) {
    throw "单目录版本打包失败。"
}

Write-Host "打包完成。"
