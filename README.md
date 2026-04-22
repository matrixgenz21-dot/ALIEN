# KPS PetroUI

Modern WPF / .NET 8 replica of the legacy KPS PetroUI petroleum services desktop application. Replaces the original Windows Forms + Infragistics 2012 + Adobe Flash + Crystal Reports stack with a maintainable MVVM architecture built on current, supported components.

## Status

**Phase 1 + Phase 2 scaffold.** Solution, shell, navigation, DI/logging/config, core domain model, and EF Core data layer are in place. Module screens are stubbed. See [`docs/architecture.md`](docs/architecture.md) for the target architecture and [`docs/roadmap.md`](docs/roadmap.md) for phases 3–7.

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | .NET 8 (Windows) |
| UI | WPF + MahApps.Metro + MaterialDesignThemes |
| MVVM | CommunityToolkit.Mvvm |
| DI | Microsoft.Extensions.DependencyInjection |
| Shell / Docking | AvalonDock |
| Data Access | Entity Framework Core 8 + SQL Server |
| Reporting | FastReport OpenSource + QuestPDF |
| Excel | ClosedXML + Microsoft.Office.Interop.Excel (optional legacy) |
| Scanner | Interop.WIA (COM) |
| Logging | Serilog (File + Console) |
| Notifications | Hardcodet.NotifyIcon.Wpf |
| Auto-update | NetSparkleUpdater |
| Testing | xUnit + Moq + FluentAssertions |

## Prerequisites

- **Windows 10/11** (WPF requires Windows to build and run — `net8.0-windows` target)
- **Visual Studio 2022** 17.8+ with the **.NET desktop development** workload, or **JetBrains Rider**
- **.NET 8 SDK** ([download](https://dotnet.microsoft.com/download/dotnet/8.0))
- **SQL Server 2019+** or **SQL Server Express / LocalDB** for the database

## Getting Started

```powershell
# 1. Clone
git clone https://github.com/matrixgenz21-dot/kps-petroui.git
cd kps-petroui

# 2. Restore packages
dotnet restore

# 3. Set the database connection string (User Secrets, dev only)
dotnet user-secrets init --project src/KPS.PetroUI.App
dotnet user-secrets set "ConnectionStrings:PetroDb" "Server=(localdb)\MSSQLLocalDB;Database=PetroDB;Trusted_Connection=True;TrustServerCertificate=True" --project src/KPS.PetroUI.App

# 4. Apply EF Core migrations (creates the database)
dotnet ef database update --project src/KPS.PetroUI.DAL --startup-project src/KPS.PetroUI.App

# 5. Build
dotnet build

# 6. Run
dotnet run --project src/KPS.PetroUI.App
```

Or open `KPS.PetroUI.sln` in Visual Studio 2022, set `KPS.PetroUI.App` as startup project, and press F5.

### Default Login (scaffolding only)

Username: `admin` — Password: `admin`

The login is currently stubbed and accepts any non-empty credentials. Real authentication will be wired up in Phase 5.

## Solution Layout

```
KPS.PetroUI/
├── src/
│   ├── KPS.PetroUI.App/              # WPF entry point, DI bootstrap, config
│   ├── KPS.PetroUI.Shell/            # MainWindow, Login, Sidebar, docking shell
│   ├── KPS.PetroUI.Core/             # Domain models, interfaces, enums, events
│   ├── KPS.PetroUI.Infrastructure/   # Service implementations (Excel, Scanner, Notifications)
│   ├── KPS.PetroUI.DAL/              # EF Core DbContext, entities, repositories, migrations
│   ├── KPS.PetroUI.Modules.Jobs/     # Job management module
│   ├── KPS.PetroUI.Modules.Reports/  # Reporting module
│   ├── KPS.PetroUI.Modules.Settings/ # Settings module
│   └── KPS.PetroUI.Updater/          # Auto-updater utility
└── tests/
    ├── KPS.PetroUI.Core.Tests/
    ├── KPS.PetroUI.DAL.Tests/
    └── KPS.PetroUI.Infrastructure.Tests/
```

## Database Migrations

Common EF Core commands (run from the repo root):

```powershell
# Create a new migration
dotnet ef migrations add <Name> --project src/KPS.PetroUI.DAL --startup-project src/KPS.PetroUI.App

# Apply migrations
dotnet ef database update --project src/KPS.PetroUI.DAL --startup-project src/KPS.PetroUI.App

# Remove the last (un-applied) migration
dotnet ef migrations remove --project src/KPS.PetroUI.DAL --startup-project src/KPS.PetroUI.App
```

Install the EF Core tools once if you don't have them:

```powershell
dotnet tool install --global dotnet-ef
```

## Tests

```powershell
dotnet test
```

## Roadmap

- [x] **Phase 1** — Foundation & Shell (DI, Serilog, Login, AvalonDock MainWindow, Sidebar)
- [x] **Phase 2** — Data Layer & Database (EF Core, entities, repositories, initial migration)
- [ ] **Phase 3** — Job Management Module
- [ ] **Phase 4** — Reporting Module (FastReport + QuestPDF)
- [ ] **Phase 5** — Scanner / Excel / Notifications / Real Auth
- [ ] **Phase 6** — Auto-Updater & Deployment
- [ ] **Phase 7** — Polish, Testing & UAT

See [`docs/roadmap.md`](docs/roadmap.md) for details.

## License

Internal — KPS (Khalifa Petroleum Services). All rights reserved.
