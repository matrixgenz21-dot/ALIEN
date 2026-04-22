using KPS.PetroUI.Core.Enums;

namespace KPS.PetroUI.Core.Models;

public class User
{
    public int Id { get; set; }
    public string UserName { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public string? Email { get; set; }
    public UserRole Role { get; set; } = UserRole.FieldStaff;
    public bool IsActive { get; set; } = true;
    public int? EmployeeId { get; set; }
    public Employee? Employee { get; set; }
    public DateTime CreatedUtc { get; set; } = DateTime.UtcNow;
    public DateTime? LastLoginUtc { get; set; }
}
