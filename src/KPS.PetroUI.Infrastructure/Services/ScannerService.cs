using KPS.PetroUI.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace KPS.PetroUI.Infrastructure.Services;

/// <summary>
/// Windows Image Acquisition (WIA) scanner service. Skeleton implementation —
/// full COM interop will be wired up in Phase 5 using `Interop.WIA.dll` (reference
/// `C:\Windows\System32\wiaaut.dll` from the csproj once running on Windows).
/// </summary>
public sealed class ScannerService : IScannerService
{
    private readonly ILogger<ScannerService> _log;

    public ScannerService(ILogger<ScannerService> log)
    {
        _log = log;
    }

    public IReadOnlyList<string> ListDevices()
    {
        _log.LogDebug("ScannerService.ListDevices called (stub)");
        // TODO(Phase 5): new WIA.DeviceManager().DeviceInfos enumerate
        return Array.Empty<string>();
    }

    public Task<string> ScanToFileAsync(string? deviceId, string targetFolder, CancellationToken ct = default)
    {
        _log.LogWarning("ScannerService.ScanToFileAsync called but WIA integration is not yet implemented (Phase 5).");
        throw new NotImplementedException("Scanner support will be implemented in Phase 5.");
    }
}
