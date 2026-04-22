using FluentAssertions;
using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;
using KPS.PetroUI.DAL.Repositories;
using KPS.PetroUI.Infrastructure.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace KPS.PetroUI.Infrastructure.Tests;

public class AuthServiceTests
{
    private static PetroDbContext NewDb()
    {
        var opts = new DbContextOptionsBuilder<PetroDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString()).Options;
        return new PetroDbContext(opts);
    }

    [Fact]
    public async Task Login_WithCorrectPlaintextHash_Succeeds()
    {
        using var db = NewDb();
        db.Users.Add(new User { UserName = "admin", DisplayName = "Admin", PasswordHash = "PLAINTEXT:admin", IsActive = true });
        await db.SaveChangesAsync();

        var auth = new AuthService(new UserRepository(db), db, NullLogger<AuthService>.Instance);
        var user = await auth.LoginAsync("admin", "admin");

        user.Should().NotBeNull();
        auth.IsAuthenticated.Should().BeTrue();
    }

    [Fact]
    public async Task Login_WithBadPassword_Fails()
    {
        using var db = NewDb();
        db.Users.Add(new User { UserName = "admin", DisplayName = "Admin", PasswordHash = "PLAINTEXT:admin", IsActive = true });
        await db.SaveChangesAsync();

        var auth = new AuthService(new UserRepository(db), db, NullLogger<AuthService>.Instance);
        (await auth.LoginAsync("admin", "wrong")).Should().BeNull();
        auth.IsAuthenticated.Should().BeFalse();
    }

    [Fact]
    public async Task Login_InactiveUser_Fails()
    {
        using var db = NewDb();
        db.Users.Add(new User { UserName = "bob", DisplayName = "Bob", PasswordHash = "PLAINTEXT:bob", IsActive = false });
        await db.SaveChangesAsync();

        var auth = new AuthService(new UserRepository(db), db, NullLogger<AuthService>.Instance);
        (await auth.LoginAsync("bob", "bob")).Should().BeNull();
    }
}
