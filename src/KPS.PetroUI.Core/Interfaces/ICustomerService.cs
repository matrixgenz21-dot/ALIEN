using KPS.PetroUI.Core.Models;

namespace KPS.PetroUI.Core.Interfaces;

public interface ICustomerService
{
    Task<IReadOnlyList<Customer>> ListAsync(bool includeInactive = false, CancellationToken ct = default);
    Task<Customer?> GetAsync(int id, CancellationToken ct = default);
    Task<Customer> CreateAsync(Customer customer, CancellationToken ct = default);
    Task UpdateAsync(Customer customer, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
}
