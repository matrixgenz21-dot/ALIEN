# KPS PetroUI — Deployment Guide (draft)

This guide will be completed in Phase 6. Current notes:

## Prerequisites on each client
- Windows 10 21H2 or newer / Windows 11
- .NET 8 Desktop Runtime (x64)
- SQL Server access (LocalDB for dev; full SQL Server for prod)

## Publishing

```
dotnet publish src/KPS.PetroUI.App/KPS.PetroUI.App.csproj `
    -c Release -r win-x64 --self-contained false `
    -o out/KPS.PetroUI
```

For a self-contained single-file:

```
dotnet publish src/KPS.PetroUI.App/KPS.PetroUI.App.csproj `
    -c Release -r win-x64 --self-contained true `
    -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true `
    -o out/KPS.PetroUI-SelfContained
```

## Database

Phase 2 ships EF Core migrations. Run against the target server once:

```
dotnet ef database update --project src/KPS.PetroUI.DAL --startup-project src/KPS.PetroUI.App
```

Connection string must be provided via User Secrets (dev) or environment variable
`ConnectionStrings__PetroDb` (prod).

## Auto-updater

Phase 6 will select between Squirrel.Windows and NetSparkleUpdater and document the
update-server layout.
