using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Configuration;
using Microsoft.EntityFrameworkCore;

namespace KPS.PetroUI.DAL.Context;

public class PetroDbContext : DbContext
{
    public PetroDbContext(DbContextOptions<PetroDbContext> options) : base(options)
    {
    }

    public DbSet<Customer> Customers => Set<Customer>();
    public DbSet<Employee> Employees => Set<Employee>();
    public DbSet<Equipment> Equipment => Set<Equipment>();
    public DbSet<Job> Jobs => Set<Job>();
    public DbSet<JobCompletion> JobCompletions => Set<JobCompletion>();
    public DbSet<User> Users => Set<User>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(DatabaseConfiguration).Assembly);
        DatabaseConfiguration.SeedInitialData(modelBuilder);
    }
}
