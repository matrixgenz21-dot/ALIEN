using KPS.PetroUI.Shell.ViewModels;
using MahApps.Metro.Controls;

namespace KPS.PetroUI.Shell.Views;

public partial class MainWindow : MetroWindow
{
    public MainWindow(MainWindowViewModel vm)
    {
        InitializeComponent();
        DataContext = vm;
    }
}
