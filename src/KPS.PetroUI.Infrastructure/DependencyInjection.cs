using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.Infrastructure.Services;
using Microsoft.Extensions.DependencyInjection;

namespace KPS.PetroUI.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddPetroInfrastructure(this IServiceCollection services)
    {
        services.AddScoped<IJobService, JobService>();
        services.AddScoped<ICustomerService, CustomerService>();
        services.AddScoped<IEmployeeService, EmployeeService>();
        services.AddScoped<IReportService, ReportService>();
        services.AddScoped<IExcelService, ExcelService>();
        services.AddScoped<IScannerService, ScannerService>();
        services.AddScoped<IAutoUpdateService, AutoUpdateService>();
        services.AddScoped<IAuthService, AuthService>();
        services.AddSingleton<INotificationService, NotificationService>();
        return services;
    }
}
