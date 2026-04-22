using System.IO;
using System.Windows;
using KPS.PetroUI.Core.Events;
using KPS.PetroUI.DAL;
using KPS.PetroUI.DAL.Context;
using KPS.PetroUI.Infrastructure;
using KPS.PetroUI.Modules.Jobs;
using KPS.PetroUI.Modules.Reports;
using KPS.PetroUI.Modules.Settings;
using KPS.PetroUI.Shell;
using KPS.PetroUI.Shell.Views;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Serilog;
using Serilog.Extensions.Logging;
using CommunityToolkit.Mvvm.Messaging;

namespace KPS.PetroUI.App;

public partial class App : Application
{
    private IHost? _host;
    private IServiceProvider? _services;

    internal IServiceProvider Services =>
        _services ?? throw new InvalidOperationException("Service provider not yet initialised.");

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        Directory.CreateDirectory(Path.Combine(AppContext.BaseDirectory, "logs"));

        var config = new ConfigurationBuilder()
            .SetBasePath(AppContext.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
            .AddJsonFile($"appsettings.{Environment.GetEnvironmentVariable("DOTNET_ENVIRONMENT") ?? "Production"}.json",
                optional: true, reloadOnChange: true)
            .AddUserSecrets<App>(optional: true)
            .AddEnvironmentVariables()
            .Build();

        Log.Logger = new LoggerConfiguration()
            .ReadFrom.Configuration(config)
            .CreateLogger();

        var services = new ServiceCollection();
        ConfigureServices(services, config);
        _services = services.BuildServiceProvider();
        _host = new Host(_services);

        var log = _services.GetRequiredService<ILogger<App>>();
        log.LogInformation("KPS PetroUI starting — v{Version}", config["AppSettings:Version"]);

        ApplyPendingMigrations(log);

        ShowLogin();
    }

    private static void ConfigureServices(IServiceCollection services, IConfiguration config)
    {
        services.AddSingleton<IConfiguration>(config);

        services.AddLogging(builder =>
        {
            builder.ClearProviders();
            builder.AddProvider(new SerilogLoggerProvider(Log.Logger, dispose: true));
        });

        var connectionString = config.GetConnectionString("PetroDb") ?? string.Empty;
        services.AddPetroDataAccess(connectionString);
        services.AddPetroInfrastructure();
        services.AddPetroShell();
        services.AddJobsModule();
        services.AddReportsModule();
        services.AddSettingsModule();
    }

    private void ApplyPendingMigrations(ILogger<App> log)
    {
        try
        {
            using var scope = _services!.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<PetroDbContext>();
            if (db.Database.IsRelational() && db.Database.GetPendingMigrations().Any())
            {
                log.LogInformation("Applying {Count} pending EF Core migration(s)",
                    db.Database.GetPendingMigrations().Count());
                db.Database.Migrate();
            }
        }
        catch (Exception ex)
        {
            log.LogWarning(ex, "Could not apply migrations automatically. Run `dotnet ef database update` manually.");
        }
    }

    private void ShowLogin()
    {
        var login = Services.GetRequiredService<LoginWindow>();
        var ok = login.ShowDialog();
        if (ok != true)
        {
            Shutdown();
            return;
        }

        var main = Services.GetRequiredService<MainWindow>();
        MainWindow = main;
        WeakReferenceMessenger.Default.Register<UserLoggedOutMessage>(this, (_, _) =>
        {
            MainWindow?.Close();
            ShowLogin();
        });
        main.Show();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        Log.CloseAndFlush();
        (_services as IDisposable)?.Dispose();
        base.OnExit(e);
    }

    // Minimal IHost shim so we don't pull in full Microsoft.Extensions.Hosting scaffolding for a desktop app.
    private sealed class Host : IDisposable
    {
        private readonly IServiceProvider _sp;
        public Host(IServiceProvider sp) { _sp = sp; }
        public void Dispose() => (_sp as IDisposable)?.Dispose();
    }
}
