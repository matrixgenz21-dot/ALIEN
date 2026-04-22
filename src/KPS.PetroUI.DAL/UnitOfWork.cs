using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.DAL.Context;
using Microsoft.EntityFrameworkCore.Storage;

namespace KPS.PetroUI.DAL;

public sealed class UnitOfWork : IUnitOfWork
{
    private readonly PetroDbContext _db;
    private IDbContextTransaction? _tx;

    public UnitOfWork(PetroDbContext db)
    {
        _db = db;
    }

    public Task<int> SaveChangesAsync(CancellationToken ct = default) => _db.SaveChangesAsync(ct);

    public async Task BeginTransactionAsync(CancellationToken ct = default)
    {
        _tx = await _db.Database.BeginTransactionAsync(ct);
    }

    public async Task CommitAsync(CancellationToken ct = default)
    {
        if (_tx is null) return;
        await _tx.CommitAsync(ct);
        await _tx.DisposeAsync();
        _tx = null;
    }

    public async Task RollbackAsync(CancellationToken ct = default)
    {
        if (_tx is null) return;
        await _tx.RollbackAsync(ct);
        await _tx.DisposeAsync();
        _tx = null;
    }

    public void Dispose()
    {
        _tx?.Dispose();
        _db.Dispose();
    }
}
