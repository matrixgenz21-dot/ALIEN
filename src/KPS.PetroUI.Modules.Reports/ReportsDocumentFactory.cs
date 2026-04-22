using KPS.PetroUI.Shell.Services;
using KPS.PetroUI.Shell.Views;

namespace KPS.PetroUI.Modules.Reports;

public sealed class ReportsDocumentFactory : IDocumentFactory
{
    public bool CanCreate(string key) => key.StartsWith("reports.", StringComparison.Ordinal);

    public object Create(string key, object? parameter)
        => new PlaceholderView { Message = "Reports module — Phase 4 deliverable.\nWill host FastReport preview + export controls." };
}

public static class ReportsDependencyInjection
{
    public static Microsoft.Extensions.DependencyInjection.IServiceCollection AddReportsModule(
        this Microsoft.Extensions.DependencyInjection.IServiceCollection services)
    {
        services.AddSingleton<IDocumentFactory, ReportsDocumentFactory>();
        return services;
    }
}
