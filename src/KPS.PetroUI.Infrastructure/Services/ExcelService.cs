using System.Reflection;
using ClosedXML.Excel;
using KPS.PetroUI.Core.Interfaces;

namespace KPS.PetroUI.Infrastructure.Services;

public sealed class ExcelService : IExcelService
{
    public Task<byte[]> ExportAsync<T>(IEnumerable<T> rows, string sheetName = "Sheet1", CancellationToken ct = default)
    {
        using var wb = new XLWorkbook();
        var ws = wb.Worksheets.Add(sheetName);

        var props = typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Where(p => p.CanRead && IsSimpleType(p.PropertyType))
            .ToArray();

        for (int c = 0; c < props.Length; c++)
        {
            ws.Cell(1, c + 1).Value = props[c].Name;
            ws.Cell(1, c + 1).Style.Font.Bold = true;
        }

        int r = 2;
        foreach (var row in rows)
        {
            ct.ThrowIfCancellationRequested();
            for (int c = 0; c < props.Length; c++)
            {
                var value = props[c].GetValue(row);
                ws.Cell(r, c + 1).Value = value switch
                {
                    null => XLCellValue.FromObject(null),
                    DateTime dt => dt,
                    bool b => b,
                    decimal dec => dec,
                    double d => d,
                    int i => i,
                    long l => l,
                    _ => value.ToString()
                };
            }
            r++;
        }

        ws.Columns().AdjustToContents();

        using var ms = new MemoryStream();
        wb.SaveAs(ms);
        return Task.FromResult(ms.ToArray());
    }

    public Task<IReadOnlyList<T>> ImportAsync<T>(Stream stream, string sheetName = "Sheet1", CancellationToken ct = default) where T : new()
    {
        using var wb = new XLWorkbook(stream);
        var ws = wb.Worksheet(sheetName);
        var props = typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.SetProperty)
            .Where(p => p.CanWrite && IsSimpleType(p.PropertyType))
            .ToDictionary(p => p.Name, StringComparer.OrdinalIgnoreCase);

        var firstRow = ws.FirstRowUsed();
        if (firstRow is null) return Task.FromResult<IReadOnlyList<T>>(Array.Empty<T>());

        var headers = firstRow.CellsUsed().Select((c, i) => (Index: i + 1, Name: c.GetString())).ToList();
        var result = new List<T>();

        foreach (var row in ws.RowsUsed().Skip(1))
        {
            ct.ThrowIfCancellationRequested();
            var item = new T();
            foreach (var (index, name) in headers)
            {
                if (!props.TryGetValue(name, out var prop)) continue;
                var cell = row.Cell(index);
                if (cell.IsEmpty()) continue;
                try
                {
                    var target = Nullable.GetUnderlyingType(prop.PropertyType) ?? prop.PropertyType;
                    var converted = Convert.ChangeType(cell.GetString(), target);
                    prop.SetValue(item, converted);
                }
                catch
                {
                    // Skip bad cells; caller may add validation in the UI.
                }
            }
            result.Add(item);
        }

        return Task.FromResult<IReadOnlyList<T>>(result);
    }

    private static bool IsSimpleType(Type t)
    {
        t = Nullable.GetUnderlyingType(t) ?? t;
        return t.IsPrimitive || t.IsEnum || t == typeof(string) || t == typeof(DateTime) || t == typeof(decimal) || t == typeof(Guid);
    }
}
