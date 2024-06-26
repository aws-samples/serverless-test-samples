# Navigate to root of repo
Push-Location -Path $PSScriptRoot\..\..

$PublishDirectory="$PWD\dist"
$AppDirectory="$PWD\src"

Remove-Item $PublishDirectory -r -Force

Push-Location "$AppDirectory\CdkBedrockDemo"
dotnet publish -c Release -r linux-x64 -p:Version=2.0.0.0 --no-self-contained -o $PublishDirectory/release/publish/CdkBedrockDemo

Write-Output '\nListing published files\n'
Get-ChildItem $PublishDirectory/release/publish/CdkBedrockDemo
Pop-Location
