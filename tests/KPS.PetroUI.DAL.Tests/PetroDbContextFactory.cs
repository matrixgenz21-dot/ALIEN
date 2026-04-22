using KPS.PetroUI.DAL.Context;
using Microsoft.EntityFrameworkCore;

namespace KPS.PetroUI.DAL.Tests;

internal static class PetroDbContextFactory
{
    public static PetroDbContext CreateInMemory(string? dbName = null)
    {
        var opts = new DbContextOptionsBuilder<PetroDbContext>()
            .UseInMemoryDatabase(dbName ?? Guid.NewGuid().ToString())
            .Options;
        var ctx = new PetroDbContext(opts);
        ctx.Database.EnsureCreated();
        return ctx;
    }
}
