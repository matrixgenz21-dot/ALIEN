using KPS.PetroUI.Shell.Services;
using KPS.PetroUI.Shell.Views;

namespace KPS.PetroUI.Modules.Settings;

public sealed class SettingsDocumentFactory : IDocumentFactory
{
    public bool CanCreate(string key) => key == "settings" || key.StartsWith("settings.", StringComparison.Ordinal);

    public object Create(string key, object? parameter)
        => new PlaceholderView { Message = "Settings — Phase 5 deliverable.\nWill expose DB connection, user preferences, theme, and admin tools." };
}

public static class SettingsDependencyInjection
{
    public static Microsoft.Extensions.DependencyInjection.IServiceCollection AddSettingsModule(
        this Microsoft.Extensions.DependencyInjection.IServiceCollection services)
    {
        services.AddSingleton<IDocumentFactory, SettingsDocumentFactory>();
        return services;
    }
}
