using KPS.PetroUI.Core.Models;

namespace KPS.PetroUI.Core.Interfaces;

public interface IEmployeeService
{
    Task<IReadOnlyList<Employee>> ListAsync(bool includeInactive = false, CancellationToken ct = default);
    Task<Employee?> GetAsync(int id, CancellationToken ct = default);
    Task<Employee> CreateAsync(Employee employee, CancellationToken ct = default);
    Task UpdateAsync(Employee employee, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
}
