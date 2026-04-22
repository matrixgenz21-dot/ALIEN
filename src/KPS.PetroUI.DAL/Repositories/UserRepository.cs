using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;
using Microsoft.EntityFrameworkCore;

namespace KPS.PetroUI.DAL.Repositories;

public interface IUserRepository : Core.Interfaces.IRepository<User>
{
    Task<User?> FindByUserNameAsync(string userName, CancellationToken ct = default);
}

public class UserRepository : Repository<User>, IUserRepository
{
    public UserRepository(PetroDbContext db) : base(db) { }

    public Task<User?> FindByUserNameAsync(string userName, CancellationToken ct = default)
        => Set.FirstOrDefaultAsync(u => u.UserName == userName, ct);
}
