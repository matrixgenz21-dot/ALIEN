namespace KPS.PetroUI.Core.Models;

public class JobCompletion
{
    public int Id { get; set; }

    public int JobId { get; set; }
    public Job? Job { get; set; }

    public DateTime CompletedUtc { get; set; } = DateTime.UtcNow;
    public string? CompletedBy { get; set; }

    public string? WorkPerformed { get; set; }
    public string? MaterialsUsed { get; set; }
    public decimal? HoursWorked { get; set; }
    public decimal? TotalCost { get; set; }

    public string? CustomerSignaturePath { get; set; }
    public string? TechnicianSignaturePath { get; set; }
    public string? AttachmentPaths { get; set; }

    public bool CustomerApproved { get; set; }
    public string? CustomerRemarks { get; set; }
}
