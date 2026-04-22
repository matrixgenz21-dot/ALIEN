using CommunityToolkit.Mvvm.ComponentModel;

namespace KPS.PetroUI.Shell.ViewModels;

public partial class DockDocument : ObservableObject
{
    public string Key { get; }
    public object Content { get; }

    [ObservableProperty] private string _title;
    [ObservableProperty] private bool _canClose = true;

    public DockDocument(string key, string title, object content)
    {
        Key = key;
        _title = title;
        Content = content;
    }
}
