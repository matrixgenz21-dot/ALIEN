#requires -Version 7
param(
    [ValidateSet("fx", "selfcontained")] [string]$Mode = "fx",
    [string]$OutDir = "out/KPS.PetroUI"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    $proj = "src/KPS.PetroUI.App/KPS.PetroUI.App.csproj"
    if ($Mode -eq "fx") {
        dotnet publish $proj -c Release -r win-x64 --self-contained false -o $OutDir
    } else {
        dotnet publish $proj -c Release -r win-x64 --self-contained true `
            -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true `
            -o $OutDir
    }
}
finally {
    Pop-Location
}
