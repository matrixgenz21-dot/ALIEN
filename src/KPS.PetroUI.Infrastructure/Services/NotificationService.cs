using System.Windows;
using Hardcodet.Wpf.TaskbarNotification;
using KPS.PetroUI.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace KPS.PetroUI.Infrastructure.Services;

public sealed class NotificationService : INotificationService, IDisposable
{
    private readonly ILogger<NotificationService> _log;
    private readonly Lazy<TaskbarIcon> _tray;

    public NotificationService(ILogger<NotificationService> log)
    {
        _log = log;
        _tray = new Lazy<TaskbarIcon>(CreateTray);
    }

    private static TaskbarIcon CreateTray() => new()
    {
        ToolTipText = "KPS PetroUI",
        Visibility = Visibility.Visible,
    };

    public void Show(string title, string message, NotificationKind kind = NotificationKind.Info)
    {
        _log.Log(kind switch
        {
            NotificationKind.Error => LogLevel.Error,
            NotificationKind.Warning => LogLevel.Warning,
            _ => LogLevel.Information,
        }, "{Title}: {Message}", title, message);

        try
        {
            var icon = kind switch
            {
                NotificationKind.Success => BalloonIcon.Info,
                NotificationKind.Warning => BalloonIcon.Warning,
                NotificationKind.Error => BalloonIcon.Error,
                _ => BalloonIcon.Info,
            };
            if (Application.Current?.Dispatcher is { } d)
                d.InvokeAsync(() => _tray.Value.ShowBalloonTip(title, message, icon));
        }
        catch (Exception ex)
        {
            _log.LogDebug(ex, "Failed to display tray balloon");
        }
    }

    public void Dispose()
    {
        if (_tray.IsValueCreated)
            _tray.Value.Dispose();
    }
}
