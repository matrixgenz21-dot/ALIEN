using System.ComponentModel;
using System.Windows.Controls;
using System.Windows.Data;
using KPS.PetroUI.Shell.ViewModels;

namespace KPS.PetroUI.Shell.Controls;

public partial class SidebarControl : UserControl
{
    public SidebarControl()
    {
        InitializeComponent();
        DataContextChanged += OnDataContextChanged;
    }

    private void OnDataContextChanged(object sender, System.Windows.DependencyPropertyChangedEventArgs e)
    {
        if (DataContext is not MainWindowViewModel vm) return;
        var view = CollectionViewSource.GetDefaultView(vm.NavigationItems);
        if (view.GroupDescriptions.Count == 0)
            view.GroupDescriptions.Add(new PropertyGroupDescription(nameof(NavigationItem.Group)));
    }
}
