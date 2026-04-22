using KPS.PetroUI.Shell.ViewModels;
using KPS.PetroUI.Shell.Views;
using Microsoft.Extensions.DependencyInjection;

namespace KPS.PetroUI.Shell;

public static class DependencyInjection
{
    public static IServiceCollection AddPetroShell(this IServiceCollection services)
    {
        services.AddSingleton<MainWindow>();
        services.AddSingleton<MainWindowViewModel>();
        services.AddTransient<LoginWindow>();
        services.AddTransient<LoginViewModel>();
        return services;
    }
}
