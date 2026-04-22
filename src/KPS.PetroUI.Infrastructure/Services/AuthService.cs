using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;
using KPS.PetroUI.DAL.Repositories;
using Microsoft.Extensions.Logging;

namespace KPS.PetroUI.Infrastructure.Services;

/// <summary>
/// Scaffolding-only auth. Accepts the seeded "admin" user with password "admin" and any active user
/// with the placeholder "PLAINTEXT:" hash. Replace with proper password hashing (BCrypt.Net-Next) in Phase 5.
/// </summary>
public sealed class AuthService : IAuthService
{
    private readonly IUserRepository _users;
    private readonly PetroDbContext _db;
    private readonly ILogger<AuthService> _log;

    public AuthService(IUserRepository users, PetroDbContext db, ILogger<AuthService> log)
    {
        _users = users;
        _db = db;
        _log = log;
    }

    public User? CurrentUser { get; private set; }
    public bool IsAuthenticated => CurrentUser is not null;

    public async Task<User?> LoginAsync(string userName, string password, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(userName) || string.IsNullOrWhiteSpace(password))
            return null;

        var user = await _users.FindByUserNameAsync(userName.Trim(), ct);
        if (user is null || !user.IsActive)
        {
            _log.LogWarning("Login failed for {UserName} (not found or inactive)", userName);
            return null;
        }

        if (!VerifyPassword(password, user.PasswordHash))
        {
            _log.LogWarning("Login failed for {UserName} (bad password)", userName);
            return null;
        }

        user.LastLoginUtc = DateTime.UtcNow;
        await _db.SaveChangesAsync(ct);

        CurrentUser = user;
        _log.LogInformation("User {UserName} logged in", userName);
        return user;
    }

    public void Logout()
    {
        if (CurrentUser is not null)
            _log.LogInformation("User {UserName} logged out", CurrentUser.UserName);
        CurrentUser = null;
    }

    private static bool VerifyPassword(string password, string storedHash)
    {
        // Scaffolding: "PLAINTEXT:" prefix means the rest is the plaintext password.
        // TODO(Phase 5): Replace with BCrypt.Net-Next or ASP.NET Core Identity password hasher.
        if (storedHash.StartsWith("PLAINTEXT:", StringComparison.Ordinal))
            return storedHash.AsSpan(10).SequenceEqual(password);
        return false;
    }
}
