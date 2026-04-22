using KPS.PetroUI.Modules.Jobs.ViewModels;
using KPS.PetroUI.Modules.Jobs.Views;
using KPS.PetroUI.Shell.Services;

namespace KPS.PetroUI.Modules.Jobs;

public sealed class JobsDocumentFactory : IDocumentFactory
{
    private readonly IServiceProvider _sp;

    public JobsDocumentFactory(IServiceProvider sp)
    {
        _sp = sp;
    }

    public bool CanCreate(string key) => key == "jobs.list" || key == "jobs.new";

    public object Create(string key, object? parameter)
    {
        return key switch
        {
            "jobs.list" => new JobListView { DataContext = (JobListViewModel)_sp.GetService(typeof(JobListViewModel))! },
            _ => new JobListView { DataContext = (JobListViewModel)_sp.GetService(typeof(JobListViewModel))! },
        };
    }
}

public static class JobsDependencyInjection
{
    public static Microsoft.Extensions.DependencyInjection.IServiceCollection AddJobsModule(
        this Microsoft.Extensions.DependencyInjection.IServiceCollection services)
    {
        services.AddTransient<JobListViewModel>();
        services.AddSingleton<IDocumentFactory, JobsDocumentFactory>();
        return services;
    }
}
