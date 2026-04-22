using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;
using KPS.PetroUI.DAL.Repositories;

namespace KPS.PetroUI.Infrastructure.Services;

public sealed class EmployeeService : IEmployeeService
{
    private readonly PetroDbContext _db;
    private readonly IEmployeeRepository _employees;

    public EmployeeService(PetroDbContext db, IEmployeeRepository employees)
    {
        _db = db;
        _employees = employees;
    }

    public async Task<IReadOnlyList<Employee>> ListAsync(bool includeInactive = false, CancellationToken ct = default)
    {
        var all = await _employees.GetAllAsync(ct);
        return includeInactive ? all : all.Where(e => e.IsActive).ToList();
    }

    public Task<Employee?> GetAsync(int id, CancellationToken ct = default)
        => _employees.GetByIdAsync(id, ct);

    public async Task<Employee> CreateAsync(Employee employee, CancellationToken ct = default)
    {
        employee.CreatedUtc = DateTime.UtcNow;
        await _employees.AddAsync(employee, ct);
        await _db.SaveChangesAsync(ct);
        return employee;
    }

    public async Task UpdateAsync(Employee employee, CancellationToken ct = default)
    {
        employee.UpdatedUtc = DateTime.UtcNow;
        await _employees.UpdateAsync(employee, ct);
        await _db.SaveChangesAsync(ct);
    }

    public async Task DeleteAsync(int id, CancellationToken ct = default)
    {
        var employee = await _employees.GetByIdAsync(id, ct);
        if (employee is null) return;
        await _employees.DeleteAsync(employee, ct);
        await _db.SaveChangesAsync(ct);
    }
}
