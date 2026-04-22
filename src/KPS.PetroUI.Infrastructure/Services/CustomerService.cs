using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;
using KPS.PetroUI.DAL.Repositories;

namespace KPS.PetroUI.Infrastructure.Services;

public sealed class CustomerService : ICustomerService
{
    private readonly PetroDbContext _db;
    private readonly ICustomerRepository _customers;

    public CustomerService(PetroDbContext db, ICustomerRepository customers)
    {
        _db = db;
        _customers = customers;
    }

    public async Task<IReadOnlyList<Customer>> ListAsync(bool includeInactive = false, CancellationToken ct = default)
    {
        var all = await _customers.GetAllAsync(ct);
        return includeInactive ? all : all.Where(c => c.IsActive).ToList();
    }

    public Task<Customer?> GetAsync(int id, CancellationToken ct = default)
        => _customers.GetByIdAsync(id, ct);

    public async Task<Customer> CreateAsync(Customer customer, CancellationToken ct = default)
    {
        customer.CreatedUtc = DateTime.UtcNow;
        await _customers.AddAsync(customer, ct);
        await _db.SaveChangesAsync(ct);
        return customer;
    }

    public async Task UpdateAsync(Customer customer, CancellationToken ct = default)
    {
        customer.UpdatedUtc = DateTime.UtcNow;
        await _customers.UpdateAsync(customer, ct);
        await _db.SaveChangesAsync(ct);
    }

    public async Task DeleteAsync(int id, CancellationToken ct = default)
    {
        var customer = await _customers.GetByIdAsync(id, ct);
        if (customer is null) return;
        await _customers.DeleteAsync(customer, ct);
        await _db.SaveChangesAsync(ct);
    }
}
