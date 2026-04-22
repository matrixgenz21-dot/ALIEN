namespace KPS.PetroUI.Core.Interfaces;

public interface IAutoUpdateService
{
    Task<bool> CheckForUpdatesAsync(CancellationToken ct = default);
    Task ApplyUpdateAsync(CancellationToken ct = default);
}
