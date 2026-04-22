using KPS.PetroUI.Core.Models;

namespace KPS.PetroUI.Core.Interfaces;

public interface IAuthService
{
    User? CurrentUser { get; }
    bool IsAuthenticated { get; }
    Task<User?> LoginAsync(string userName, string password, CancellationToken ct = default);
    void Logout();
}
