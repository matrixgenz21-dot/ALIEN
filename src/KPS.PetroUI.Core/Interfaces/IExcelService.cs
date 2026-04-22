namespace KPS.PetroUI.Core.Interfaces;

public interface IExcelService
{
    Task<byte[]> ExportAsync<T>(IEnumerable<T> rows, string sheetName = "Sheet1", CancellationToken ct = default);
    Task<IReadOnlyList<T>> ImportAsync<T>(Stream stream, string sheetName = "Sheet1", CancellationToken ct = default) where T : new();
}
