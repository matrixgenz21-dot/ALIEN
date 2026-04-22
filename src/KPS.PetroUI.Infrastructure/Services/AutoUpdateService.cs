using KPS.PetroUI.Core.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace KPS.PetroUI.Infrastructure.Services;

/// <summary>
/// Auto-update service skeleton. NetSparkleUpdater integration will be wired up in Phase 6
/// against the "UpdateServerUrl" from appsettings.json.
/// </summary>
public sealed class AutoUpdateService : IAutoUpdateService
{
    private readonly IConfiguration _config;
    private readonly ILogger<AutoUpdateService> _log;

    public AutoUpdateService(IConfiguration config, ILogger<AutoUpdateService> log)
    {
        _config = config;
        _log = log;
    }

    public Task<bool> CheckForUpdatesAsync(CancellationToken ct = default)
    {
        var url = _config["AppSettings:UpdateServerUrl"];
        _log.LogDebug("CheckForUpdates stub (server={Url})", url);
        return Task.FromResult(false);
    }

    public Task ApplyUpdateAsync(CancellationToken ct = default)
    {
        _log.LogWarning("ApplyUpdate not implemented yet (Phase 6).");
        return Task.CompletedTask;
    }
}
