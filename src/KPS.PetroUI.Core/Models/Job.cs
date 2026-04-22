using KPS.PetroUI.Core.Enums;

namespace KPS.PetroUI.Core.Models;

public class Job
{
    public int Id { get; set; }
    public string JobNumber { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }

    public int CustomerId { get; set; }
    public Customer? Customer { get; set; }

    public int? AssignedEmployeeId { get; set; }
    public Employee? AssignedEmployee { get; set; }

    public int? EquipmentId { get; set; }
    public Equipment? Equipment { get; set; }

    public JobStatus Status { get; set; } = JobStatus.New;
    public DateTime ScheduledStart { get; set; }
    public DateTime? ScheduledEnd { get; set; }
    public DateTime? ActualStart { get; set; }
    public DateTime? ActualEnd { get; set; }

    public string? Location { get; set; }
    public string? Notes { get; set; }

    public JobCompletion? Completion { get; set; }

    public DateTime CreatedUtc { get; set; } = DateTime.UtcNow;
    public DateTime? UpdatedUtc { get; set; }
    public string? CreatedBy { get; set; }
    public string? UpdatedBy { get; set; }
}
