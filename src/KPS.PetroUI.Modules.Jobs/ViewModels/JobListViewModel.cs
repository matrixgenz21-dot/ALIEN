using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.Core.Models;
using Microsoft.Extensions.Logging;

namespace KPS.PetroUI.Modules.Jobs.ViewModels;

public partial class JobListViewModel : ObservableObject
{
    private readonly IJobService _jobs;
    private readonly ILogger<JobListViewModel> _log;

    public ObservableCollection<Job> Jobs { get; } = new();

    [ObservableProperty] private bool _isBusy;

    public JobListViewModel(IJobService jobs, ILogger<JobListViewModel> log)
    {
        _jobs = jobs;
        _log = log;
        _ = LoadAsync();
    }

    [RelayCommand]
    public async Task LoadAsync()
    {
        IsBusy = true;
        try
        {
            Jobs.Clear();
            foreach (var job in await _jobs.ListAsync())
                Jobs.Add(job);
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Failed to load jobs");
        }
        finally
        {
            IsBusy = false;
        }
    }
}
