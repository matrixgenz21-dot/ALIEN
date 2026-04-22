using CommunityToolkit.Mvvm.ComponentModel;

namespace KPS.PetroUI.Shell.ViewModels;

public abstract class ViewModelBase : ObservableObject
{
    [ObservableProperty] private bool _isBusy;
    [ObservableProperty] private string? _statusMessage;
}
