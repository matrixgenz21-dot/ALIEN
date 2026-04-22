namespace KPS.PetroUI.Core.Interfaces;

public interface IScannerService
{
    IReadOnlyList<string> ListDevices();
    Task<string> ScanToFileAsync(string? deviceId, string targetFolder, CancellationToken ct = default);
}
