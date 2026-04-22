using KPS.PetroUI.Core.Enums;
using KPS.PetroUI.Core.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace KPS.PetroUI.DAL.Configuration;

public static class DatabaseConfiguration
{
    public static void SeedInitialData(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>().HasData(new User
        {
            Id = 1,
            UserName = "admin",
            DisplayName = "System Administrator",
            // NOTE: This is a placeholder hash ("admin" hashed with PBKDF2 SHA256 1 iteration, scaffolding only).
            // Replace with real password hashing (e.g. BCrypt) in Phase 5 when real auth is wired up.
            PasswordHash = "PLAINTEXT:admin",
            Role = UserRole.Admin,
            IsActive = true,
            CreatedUtc = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
        });

        modelBuilder.Entity<Customer>().HasData(new Customer
        {
            Id = 1,
            Code = "KPS-INT",
            Name = "KPS Internal Operations",
            IsActive = true,
            CreatedUtc = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
        });
    }
}

public sealed class CustomerConfiguration : IEntityTypeConfiguration<Customer>
{
    public void Configure(EntityTypeBuilder<Customer> b)
    {
        b.ToTable("Customers");
        b.HasKey(x => x.Id);
        b.Property(x => x.Code).HasMaxLength(32).IsRequired();
        b.HasIndex(x => x.Code).IsUnique();
        b.Property(x => x.Name).HasMaxLength(256).IsRequired();
        b.Property(x => x.ContactPerson).HasMaxLength(128);
        b.Property(x => x.Email).HasMaxLength(256);
        b.Property(x => x.Phone).HasMaxLength(64);
        b.Property(x => x.Address).HasMaxLength(512);
        b.Property(x => x.City).HasMaxLength(128);
        b.Property(x => x.Country).HasMaxLength(128);
    }
}

public sealed class EmployeeConfiguration : IEntityTypeConfiguration<Employee>
{
    public void Configure(EntityTypeBuilder<Employee> b)
    {
        b.ToTable("Employees");
        b.HasKey(x => x.Id);
        b.Property(x => x.EmployeeCode).HasMaxLength(32).IsRequired();
        b.HasIndex(x => x.EmployeeCode).IsUnique();
        b.Property(x => x.FirstName).HasMaxLength(128).IsRequired();
        b.Property(x => x.LastName).HasMaxLength(128).IsRequired();
        b.Property(x => x.Designation).HasMaxLength(128);
        b.Property(x => x.Department).HasMaxLength(128);
        b.Property(x => x.Email).HasMaxLength(256);
        b.Property(x => x.Phone).HasMaxLength(64);
        b.Ignore(x => x.FullName);
    }
}

public sealed class EquipmentConfiguration : IEntityTypeConfiguration<Equipment>
{
    public void Configure(EntityTypeBuilder<Equipment> b)
    {
        b.ToTable("Equipment");
        b.HasKey(x => x.Id);
        b.Property(x => x.AssetTag).HasMaxLength(64).IsRequired();
        b.HasIndex(x => x.AssetTag).IsUnique();
        b.Property(x => x.Name).HasMaxLength(256).IsRequired();
        b.Property(x => x.Description).HasMaxLength(1024);
        b.Property(x => x.SerialNumber).HasMaxLength(128);
        b.Property(x => x.Manufacturer).HasMaxLength(128);
        b.Property(x => x.Model).HasMaxLength(128);
    }
}

public sealed class JobConfiguration : IEntityTypeConfiguration<Job>
{
    public void Configure(EntityTypeBuilder<Job> b)
    {
        b.ToTable("Jobs");
        b.HasKey(x => x.Id);
        b.Property(x => x.JobNumber).HasMaxLength(32).IsRequired();
        b.HasIndex(x => x.JobNumber).IsUnique();
        b.Property(x => x.Title).HasMaxLength(256).IsRequired();
        b.Property(x => x.Description).HasMaxLength(2048);
        b.Property(x => x.Location).HasMaxLength(512);
        b.Property(x => x.Notes).HasMaxLength(4000);
        b.Property(x => x.CreatedBy).HasMaxLength(64);
        b.Property(x => x.UpdatedBy).HasMaxLength(64);

        b.HasOne(x => x.Customer)
            .WithMany()
            .HasForeignKey(x => x.CustomerId)
            .OnDelete(DeleteBehavior.Restrict);

        b.HasOne(x => x.AssignedEmployee)
            .WithMany()
            .HasForeignKey(x => x.AssignedEmployeeId)
            .OnDelete(DeleteBehavior.SetNull);

        b.HasOne(x => x.Equipment)
            .WithMany()
            .HasForeignKey(x => x.EquipmentId)
            .OnDelete(DeleteBehavior.SetNull);

        b.HasOne(x => x.Completion)
            .WithOne(c => c.Job!)
            .HasForeignKey<JobCompletion>(c => c.JobId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}

public sealed class JobCompletionConfiguration : IEntityTypeConfiguration<JobCompletion>
{
    public void Configure(EntityTypeBuilder<JobCompletion> b)
    {
        b.ToTable("JobCompletions");
        b.HasKey(x => x.Id);
        b.Property(x => x.CompletedBy).HasMaxLength(128);
        b.Property(x => x.WorkPerformed).HasMaxLength(4000);
        b.Property(x => x.MaterialsUsed).HasMaxLength(4000);
        b.Property(x => x.HoursWorked).HasPrecision(8, 2);
        b.Property(x => x.TotalCost).HasPrecision(14, 2);
        b.Property(x => x.CustomerSignaturePath).HasMaxLength(512);
        b.Property(x => x.TechnicianSignaturePath).HasMaxLength(512);
        b.Property(x => x.AttachmentPaths).HasMaxLength(4000);
        b.Property(x => x.CustomerRemarks).HasMaxLength(2000);
        b.HasIndex(x => x.JobId).IsUnique();
    }
}

public sealed class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> b)
    {
        b.ToTable("Users");
        b.HasKey(x => x.Id);
        b.Property(x => x.UserName).HasMaxLength(64).IsRequired();
        b.HasIndex(x => x.UserName).IsUnique();
        b.Property(x => x.DisplayName).HasMaxLength(128).IsRequired();
        b.Property(x => x.PasswordHash).HasMaxLength(256).IsRequired();
        b.Property(x => x.Email).HasMaxLength(256);

        b.HasOne(x => x.Employee)
            .WithMany()
            .HasForeignKey(x => x.EmployeeId)
            .OnDelete(DeleteBehavior.SetNull);
    }
}
