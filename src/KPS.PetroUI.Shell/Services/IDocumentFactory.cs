namespace KPS.PetroUI.Shell.Services;

public interface IDocumentFactory
{
    bool CanCreate(string key);
    object Create(string key, object? parameter);
}
