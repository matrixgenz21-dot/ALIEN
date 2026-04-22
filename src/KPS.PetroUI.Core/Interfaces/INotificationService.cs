namespace KPS.PetroUI.Core.Interfaces;

public enum NotificationKind
{
    Info,
    Success,
    Warning,
    Error,
}

public interface INotificationService
{
    void Show(string title, string message, NotificationKind kind = NotificationKind.Info);
}
