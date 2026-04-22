# KPS PetroUI — Architecture

## Layers

```
┌──────────────────────────────────────────────┐
│  KPS.PetroUI.App            (WPF entry)       │
│   ├─ DI bootstrap / Serilog / IConfiguration  │
│   └─ Composition root                         │
├──────────────────────────────────────────────┤
│  KPS.PetroUI.Shell          (Main window)     │
│   ├─ MainWindow + AvalonDock                  │
│   ├─ Sidebar / Toolbar / StatusBar controls   │
│   ├─ LoginWindow                              │
│   └─ MVVM ViewModels                          │
├──────────────────────────────────────────────┤
│  Modules/*                  (Feature tabs)    │
│   ├─ Modules.Jobs    (List + CRUD + Complete) │
│   ├─ Modules.Reports (FastReport, PDF)        │
│   └─ Modules.Settings                         │
├──────────────────────────────────────────────┤
│  KPS.PetroUI.Infrastructure (Services impl)   │
├──────────────────────────────────────────────┤
│  KPS.PetroUI.DAL            (EF Core 8)       │
├──────────────────────────────────────────────┤
│  KPS.PetroUI.Core           (Models / ifaces) │
└──────────────────────────────────────────────┘
```

## Navigation

Sidebar items bind to `MainWindowViewModel.NavigationItems`. Selecting an item raises
`OpenDocument(key, title)`, which asks every registered `IDocumentFactory` whether it can
handle the key. The first match constructs the control (a `UserControl` bound to its
ViewModel) and a `DockDocument` is added to `OpenDocuments`. AvalonDock renders each
document as a tab inside the central pane.

Modules register themselves via `AddXModule()` extension methods in their own assemblies,
keeping the Shell project agnostic of feature modules.

## Auth

`IAuthService` currently accepts a seeded `admin`/`admin` user (plaintext hash prefix).
Phase 5 will swap this out for BCrypt and real user management.

## Data

`PetroDbContext` configures entities via `IEntityTypeConfiguration<T>` in
`KPS.PetroUI.DAL.Configuration`. Generic `Repository<T>` handles CRUD, with focused
interfaces (`IJobRepository`, `IUserRepository`) for queries that need `Include` or
lookup by natural key.
