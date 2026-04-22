using System.Linq.Expressions;
using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.DAL.Context;
using Microsoft.EntityFrameworkCore;

namespace KPS.PetroUI.DAL.Repositories;

public class Repository<T> : IRepository<T> where T : class
{
    protected readonly PetroDbContext Db;
    protected readonly DbSet<T> Set;

    public Repository(PetroDbContext db)
    {
        Db = db;
        Set = db.Set<T>();
    }

    public virtual Task<T?> GetByIdAsync(int id, CancellationToken ct = default)
        => Set.FindAsync(new object[] { id }, ct).AsTask();

    public virtual async Task<IReadOnlyList<T>> GetAllAsync(CancellationToken ct = default)
        => await Set.AsNoTracking().ToListAsync(ct);

    public virtual async Task<IReadOnlyList<T>> FindAsync(Expression<Func<T, bool>> predicate, CancellationToken ct = default)
        => await Set.AsNoTracking().Where(predicate).ToListAsync(ct);

    public virtual async Task<T> AddAsync(T entity, CancellationToken ct = default)
    {
        await Set.AddAsync(entity, ct);
        return entity;
    }

    public virtual Task UpdateAsync(T entity, CancellationToken ct = default)
    {
        Set.Update(entity);
        return Task.CompletedTask;
    }

    public virtual Task DeleteAsync(T entity, CancellationToken ct = default)
    {
        Set.Remove(entity);
        return Task.CompletedTask;
    }

    public Task<int> SaveChangesAsync(CancellationToken ct = default) => Db.SaveChangesAsync(ct);
}
