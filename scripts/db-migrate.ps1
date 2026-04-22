#requires -Version 7
<#
.SYNOPSIS
    Adds or applies an EF Core migration for KPS.PetroUI.DAL.
.EXAMPLE
    ./scripts/db-migrate.ps1 -Add InitialCreate
    ./scripts/db-migrate.ps1 -Update
#>
param(
    [string]$Add,
    [switch]$Update,
    [switch]$Remove
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    dotnet tool restore | Out-Null
    $dalProj = "src/KPS.PetroUI.DAL/KPS.PetroUI.DAL.csproj"
    $appProj = "src/KPS.PetroUI.App/KPS.PetroUI.App.csproj"

    if ($Add) {
        dotnet ef migrations add $Add --project $dalProj --startup-project $appProj --output-dir Migrations
    }
    elseif ($Remove) {
        dotnet ef migrations remove --project $dalProj --startup-project $appProj
    }
    elseif ($Update) {
        dotnet ef database update --project $dalProj --startup-project $appProj
    }
    else {
        Write-Host "Usage: -Add <Name> | -Update | -Remove"
    }
}
finally {
    Pop-Location
}
