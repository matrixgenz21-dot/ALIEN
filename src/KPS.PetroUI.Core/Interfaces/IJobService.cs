using KPS.PetroUI.Core.Enums;
using KPS.PetroUI.Core.Models;

namespace KPS.PetroUI.Core.Interfaces;

public interface IJobService
{
    Task<IReadOnlyList<Job>> ListAsync(JobStatus? status = null, CancellationToken ct = default);
    Task<Job?> GetAsync(int id, CancellationToken ct = default);
    Task<Job> CreateAsync(Job job, CancellationToken ct = default);
    Task UpdateAsync(Job job, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
    Task<JobCompletion> CompleteAsync(int jobId, JobCompletion completion, CancellationToken ct = default);
}
