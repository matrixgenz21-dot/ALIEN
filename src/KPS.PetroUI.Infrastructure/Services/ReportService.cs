using KPS.PetroUI.Core.Enums;
using KPS.PetroUI.Core.Interfaces;
using Microsoft.Extensions.Logging;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace KPS.PetroUI.Infrastructure.Services;

/// <summary>
/// Report service backed by QuestPDF. FastReport integration (with visual .frx templates) will be
/// added in Phase 4 — this stub currently produces a minimal PDF so downstream wiring can be tested.
/// </summary>
public sealed class ReportService : IReportService
{
    private readonly ILogger<ReportService> _log;

    static ReportService()
    {
        QuestPDF.Settings.License = LicenseType.Community;
    }

    public ReportService(ILogger<ReportService> log)
    {
        _log = log;
    }

    public Task<byte[]> RenderPdfAsync(ReportType type, IDictionary<string, object?> parameters, CancellationToken ct = default)
    {
        _log.LogInformation("Rendering {Type} report (PDF) with {Count} params", type, parameters.Count);

        var bytes = Document.Create(container =>
        {
            container.Page(page =>
            {
                page.Margin(40);
                page.Size(PageSizes.A4);
                page.Header().Text($"KPS PetroUI — {type}").FontSize(18).Bold();
                page.Content().Column(col =>
                {
                    col.Item().Text($"Generated: {DateTime.Now:yyyy-MM-dd HH:mm}");
                    foreach (var kvp in parameters)
                        col.Item().Text($"{kvp.Key}: {kvp.Value}");
                    col.Item().PaddingTop(20).Text("This is a scaffolded report. Full FastReport templates will be wired up in Phase 4.")
                        .Italic();
                });
                page.Footer().AlignCenter().Text(x =>
                {
                    x.CurrentPageNumber();
                    x.Span(" / ");
                    x.TotalPages();
                });
            });
        }).GeneratePdf();

        return Task.FromResult(bytes);
    }

    public Task<byte[]> RenderExcelAsync(ReportType type, IDictionary<string, object?> parameters, CancellationToken ct = default)
    {
        _log.LogWarning("Excel report rendering is not yet implemented (Phase 4).");
        throw new NotImplementedException("Excel export will use ClosedXML in Phase 4.");
    }

    public async Task<string> ExportToFileAsync(ReportType type, IDictionary<string, object?> parameters, string targetPath, CancellationToken ct = default)
    {
        var bytes = await RenderPdfAsync(type, parameters, ct);
        await File.WriteAllBytesAsync(targetPath, bytes, ct);
        return targetPath;
    }
}
