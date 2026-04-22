using System.Windows;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using KPS.PetroUI.Core.Events;
using KPS.PetroUI.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace KPS.PetroUI.Shell.ViewModels;

public partial class LoginViewModel : ViewModelBase
{
    private readonly IAuthService _auth;
    private readonly ILogger<LoginViewModel> _log;

    [ObservableProperty] private string _userName = "admin";
    [ObservableProperty] private string _errorMessage = string.Empty;
    [ObservableProperty] private bool _hasError;

    public LoginViewModel(IAuthService auth, ILogger<LoginViewModel> log)
    {
        _auth = auth;
        _log = log;
    }

    [RelayCommand]
    private async Task LoginAsync(object? parameter)
    {
        HasError = false;
        ErrorMessage = string.Empty;
        IsBusy = true;
        try
        {
            // The PasswordBox sends its SecurePassword-backed string via parameter from XAML.
            var password = parameter as string ?? string.Empty;
            var user = await _auth.LoginAsync(UserName, password);
            if (user is null)
            {
                HasError = true;
                ErrorMessage = "Invalid username or password.";
                return;
            }

            WeakReferenceMessenger.Default.Send(new UserLoggedInMessage(user));
            LoginSucceeded?.Invoke();
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Login failed");
            HasError = true;
            ErrorMessage = "Login failed. See logs for details.";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void Cancel()
    {
        Application.Current.Shutdown();
    }

    public event Action? LoginSucceeded;
}
