using KPS.PetroUI.Core.Enums;
using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;
using KPS.PetroUI.DAL.Repositories;
using Microsoft.Extensions.Logging;

namespace KPS.PetroUI.Infrastructure.Services;

public sealed class JobService : IJobService
{
    private readonly PetroDbContext _db;
    private readonly IJobRepository _jobs;
    private readonly ILogger<JobService> _log;

    public JobService(PetroDbContext db, IJobRepository jobs, ILogger<JobService> log)
    {
        _db = db;
        _jobs = jobs;
        _log = log;
    }

    public Task<IReadOnlyList<Job>> ListAsync(JobStatus? status = null, CancellationToken ct = default)
        => _jobs.ListWithDetailsAsync(status, ct);

    public Task<Job?> GetAsync(int id, CancellationToken ct = default)
        => _jobs.GetWithDetailsAsync(id, ct);

    public async Task<Job> CreateAsync(Job job, CancellationToken ct = default)
    {
        job.CreatedUtc = DateTime.UtcNow;
        await _jobs.AddAsync(job, ct);
        await _db.SaveChangesAsync(ct);
        _log.LogInformation("Job {JobNumber} created (Id={Id})", job.JobNumber, job.Id);
        return job;
    }

    public async Task UpdateAsync(Job job, CancellationToken ct = default)
    {
        job.UpdatedUtc = DateTime.UtcNow;
        await _jobs.UpdateAsync(job, ct);
        await _db.SaveChangesAsync(ct);
        _log.LogInformation("Job {JobNumber} updated (Id={Id})", job.JobNumber, job.Id);
    }

    public async Task DeleteAsync(int id, CancellationToken ct = default)
    {
        var job = await _jobs.GetByIdAsync(id, ct);
        if (job is null) return;
        await _jobs.DeleteAsync(job, ct);
        await _db.SaveChangesAsync(ct);
        _log.LogInformation("Job deleted (Id={Id})", id);
    }

    public async Task<JobCompletion> CompleteAsync(int jobId, JobCompletion completion, CancellationToken ct = default)
    {
        var job = await _jobs.GetWithDetailsAsync(jobId, ct)
            ?? throw new InvalidOperationException($"Job {jobId} not found");

        completion.JobId = jobId;
        completion.CompletedUtc = DateTime.UtcNow;
        job.Completion = completion;
        job.Status = JobStatus.Completed;
        job.ActualEnd = completion.CompletedUtc;
        job.UpdatedUtc = completion.CompletedUtc;

        await _db.SaveChangesAsync(ct);
        _log.LogInformation("Job {JobNumber} completed (Id={Id})", job.JobNumber, job.Id);
        return completion;
    }
}
