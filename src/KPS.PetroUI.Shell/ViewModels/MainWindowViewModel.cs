using System.Collections.ObjectModel;
using System.Windows;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using KPS.PetroUI.Core.Events;
using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.Shell.Services;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace KPS.PetroUI.Shell.ViewModels;

public partial class MainWindowViewModel : ViewModelBase, INavigationService
{
    private readonly IServiceProvider _sp;
    private readonly IAuthService _auth;
    private readonly ILogger<MainWindowViewModel> _log;

    public ObservableCollection<NavigationItem> NavigationItems { get; } = new();
    public ObservableCollection<DockDocument> OpenDocuments { get; } = new();

    [ObservableProperty] private NavigationItem? _selectedNavigationItem;
    [ObservableProperty] private DockDocument? _activeDocument;
    [ObservableProperty] private string _currentUserName = string.Empty;
    [ObservableProperty] private string _connectionStatus = "Connected";
    [ObservableProperty] private string _clock = DateTime.Now.ToString("yyyy-MM-dd HH:mm");

    public MainWindowViewModel(IServiceProvider sp, IAuthService auth, ILogger<MainWindowViewModel> log)
    {
        _sp = sp;
        _auth = auth;
        _log = log;

        CurrentUserName = auth.CurrentUser?.DisplayName ?? "(not logged in)";

        BuildNavigation();
        WireMessages();
    }

    private void BuildNavigation()
    {
        NavigationItems.Add(new NavigationItem("jobs.list", "Jobs", "Briefcase", "Operations"));
        NavigationItems.Add(new NavigationItem("jobs.new", "New Job", "Plus", "Operations"));
        NavigationItems.Add(new NavigationItem("reports.list", "Reports", "FileChart", "Reporting"));
        NavigationItems.Add(new NavigationItem("customers.list", "Customers", "Account", "Master Data"));
        NavigationItems.Add(new NavigationItem("employees.list", "Employees", "AccountGroup", "Master Data"));
        NavigationItems.Add(new NavigationItem("equipment.list", "Equipment", "Toolbox", "Master Data"));
        NavigationItems.Add(new NavigationItem("settings", "Settings", "Cog", "Administration"));
    }

    private void WireMessages()
    {
        WeakReferenceMessenger.Default.Register<NavigationRequestedMessage>(this, (_, m) => OpenDocument(m.DocumentKey, m.Title, m.Parameter));
        WeakReferenceMessenger.Default.Register<UserLoggedOutMessage>(this, (_, _) => HandleLogout());
    }

    partial void OnSelectedNavigationItemChanged(NavigationItem? value)
    {
        if (value is null) return;
        OpenDocument(value.Key, value.Title, null);
    }

    public void OpenDocument(string key, string title, object? parameter = null)
    {
        var existing = OpenDocuments.FirstOrDefault(d => d.Key == key);
        if (existing is not null)
        {
            ActiveDocument = existing;
            return;
        }

        var factories = _sp.GetServices<IDocumentFactory>();
        var factory = factories.FirstOrDefault(f => f.CanCreate(key));
        object content = factory?.Create(key, parameter) ?? CreatePlaceholder(key);

        var doc = new DockDocument(key, title, content);
        OpenDocuments.Add(doc);
        ActiveDocument = doc;
        _log.LogDebug("Opened document {Key} ({Title})", key, title);
    }

    public void CloseDocument(string key)
    {
        var doc = OpenDocuments.FirstOrDefault(d => d.Key == key);
        if (doc is null) return;
        OpenDocuments.Remove(doc);
    }

    public bool IsOpen(string key) => OpenDocuments.Any(d => d.Key == key);

    [RelayCommand]
    private void CloseDocumentCommand(DockDocument? doc)
    {
        if (doc is null) return;
        OpenDocuments.Remove(doc);
    }

    [RelayCommand]
    private void Logout()
    {
        _auth.Logout();
        WeakReferenceMessenger.Default.Send(new UserLoggedOutMessage());
    }

    [RelayCommand]
    private void Exit() => Application.Current.Shutdown();

    private void HandleLogout()
    {
        OpenDocuments.Clear();
        CurrentUserName = "(not logged in)";
    }

    private static object CreatePlaceholder(string key) => new Views.PlaceholderView { Message = $"Module '{key}' is not yet implemented." };
}
