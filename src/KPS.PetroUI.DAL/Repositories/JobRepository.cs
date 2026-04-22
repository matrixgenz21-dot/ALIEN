using KPS.PetroUI.Core.Enums;
using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;
using Microsoft.EntityFrameworkCore;

namespace KPS.PetroUI.DAL.Repositories;

public interface IJobRepository : Core.Interfaces.IRepository<Job>
{
    Task<IReadOnlyList<Job>> ListWithDetailsAsync(JobStatus? status = null, CancellationToken ct = default);
    Task<Job?> GetWithDetailsAsync(int id, CancellationToken ct = default);
}

public class JobRepository : Repository<Job>, IJobRepository
{
    public JobRepository(PetroDbContext db) : base(db) { }

    public async Task<IReadOnlyList<Job>> ListWithDetailsAsync(JobStatus? status = null, CancellationToken ct = default)
    {
        var q = Set.AsNoTracking()
            .Include(j => j.Customer)
            .Include(j => j.AssignedEmployee)
            .Include(j => j.Equipment)
            .AsQueryable();

        if (status.HasValue) q = q.Where(j => j.Status == status.Value);

        return await q.OrderByDescending(j => j.ScheduledStart).ToListAsync(ct);
    }

    public Task<Job?> GetWithDetailsAsync(int id, CancellationToken ct = default)
        => Set
            .Include(j => j.Customer)
            .Include(j => j.AssignedEmployee)
            .Include(j => j.Equipment)
            .Include(j => j.Completion)
            .FirstOrDefaultAsync(j => j.Id == id, ct);
}
