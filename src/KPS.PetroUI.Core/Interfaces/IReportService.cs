using KPS.PetroUI.Core.Enums;

namespace KPS.PetroUI.Core.Interfaces;

public interface IReportService
{
    Task<byte[]> RenderPdfAsync(ReportType type, IDictionary<string, object?> parameters, CancellationToken ct = default);
    Task<byte[]> RenderExcelAsync(ReportType type, IDictionary<string, object?> parameters, CancellationToken ct = default);
    Task<string> ExportToFileAsync(ReportType type, IDictionary<string, object?> parameters, string targetPath, CancellationToken ct = default);
}
