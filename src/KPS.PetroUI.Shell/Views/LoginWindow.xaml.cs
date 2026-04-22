using System.Windows;
using KPS.PetroUI.Shell.ViewModels;
using MahApps.Metro.Controls;

namespace KPS.PetroUI.Shell.Views;

public partial class LoginWindow : MetroWindow
{
    private readonly LoginViewModel _vm;

    public bool LoginSucceeded { get; private set; }

    public LoginWindow(LoginViewModel vm)
    {
        InitializeComponent();
        _vm = vm;
        DataContext = vm;
        vm.LoginSucceeded += OnLoginSucceeded;
        Loaded += (_, _) => UserNameBox.Focus();
    }

    private void OnLoginSucceeded()
    {
        LoginSucceeded = true;
        DialogResult = true;
        Close();
    }

    private async void LoginButton_Click(object sender, RoutedEventArgs e)
    {
        if (_vm.LoginCommand.CanExecute(PasswordBox.Password))
            await _vm.LoginCommand.ExecuteAsync(PasswordBox.Password);
    }
}
