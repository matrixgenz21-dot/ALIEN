using FluentAssertions;
using KPS.PetroUI.Core.Enums;
using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Repositories;
using Xunit;

namespace KPS.PetroUI.DAL.Tests;

public class RepositoryTests
{
    [Fact]
    public async Task Generic_Repository_AddsAndRetrieves()
    {
        using var db = PetroDbContextFactory.CreateInMemory();
        var repo = new Repository<Customer>(db);

        var added = await repo.AddAsync(new Customer { Code = "C1", Name = "Acme" });
        await repo.SaveChangesAsync();

        var back = await repo.GetByIdAsync(added.Id);
        back.Should().NotBeNull();
        back!.Name.Should().Be("Acme");
    }

    [Fact]
    public async Task JobRepository_ListWithDetails_FiltersByStatus()
    {
        using var db = PetroDbContextFactory.CreateInMemory();

        db.Customers.Add(new Customer { Id = 100, Code = "X", Name = "X" });
        db.Jobs.AddRange(
            new Job { JobNumber = "J-1", Title = "A", CustomerId = 100, Status = JobStatus.New, ScheduledStart = DateTime.UtcNow },
            new Job { JobNumber = "J-2", Title = "B", CustomerId = 100, Status = JobStatus.Completed, ScheduledStart = DateTime.UtcNow });
        await db.SaveChangesAsync();

        var repo = new JobRepository(db);
        var completed = await repo.ListWithDetailsAsync(JobStatus.Completed);
        completed.Should().HaveCount(1);
        completed[0].JobNumber.Should().Be("J-2");
    }

    [Fact]
    public async Task UserRepository_FindByUserName_IsCaseSensitive()
    {
        using var db = PetroDbContextFactory.CreateInMemory();
        db.Users.Add(new User { UserName = "alice", DisplayName = "Alice", PasswordHash = "PLAINTEXT:x" });
        await db.SaveChangesAsync();

        var repo = new UserRepository(db);
        (await repo.FindByUserNameAsync("alice")).Should().NotBeNull();
    }
}
