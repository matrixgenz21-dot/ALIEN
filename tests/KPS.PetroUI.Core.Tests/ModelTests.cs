using FluentAssertions;
using KPS.PetroUI.Core.Models;
using Xunit;

namespace KPS.PetroUI.Core.Tests;

public class ModelTests
{
    [Fact]
    public void Employee_FullName_CombinesFirstAndLast()
    {
        var e = new Employee { FirstName = "Ada", LastName = "Lovelace" };
        e.FullName.Should().Be("Ada Lovelace");
    }

    [Fact]
    public void Customer_DefaultsIsActive_True()
    {
        new Customer().IsActive.Should().BeTrue();
    }
}
