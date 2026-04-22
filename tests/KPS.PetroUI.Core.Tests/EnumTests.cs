using FluentAssertions;
using KPS.PetroUI.Core.Enums;
using Xunit;

namespace KPS.PetroUI.Core.Tests;

public class EnumTests
{
    [Fact]
    public void JobStatus_HasExpectedValues()
    {
        Enum.GetNames<JobStatus>().Should().Contain(new[]
        {
            nameof(JobStatus.New),
            nameof(JobStatus.InProgress),
            nameof(JobStatus.Completed),
            nameof(JobStatus.Cancelled),
        });
    }

    [Fact]
    public void UserRole_DefaultIsFieldStaff()
    {
        default(UserRole).Should().Be(UserRole.FieldStaff);
    }
}
