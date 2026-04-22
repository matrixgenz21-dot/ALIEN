using CommunityToolkit.Mvvm.ComponentModel;

namespace KPS.PetroUI.Shell.ViewModels;

public partial class NavigationItem : ObservableObject
{
    public string Key { get; }
    public string Title { get; }
    public string Icon { get; }
    public string Group { get; }

    [ObservableProperty] private bool _isSelected;

    public NavigationItem(string key, string title, string icon, string group)
    {
        Key = key;
        Title = title;
        Icon = icon;
        Group = group;
    }
}
