namespace KPS.PetroUI.Core.Interfaces;

public interface INavigationService
{
    void OpenDocument(string key, string title, object? parameter = null);
    void CloseDocument(string key);
    bool IsOpen(string key);
}
