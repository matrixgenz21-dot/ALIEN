using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;

namespace KPS.PetroUI.DAL.Repositories;

public interface IEmployeeRepository : Core.Interfaces.IRepository<Employee> { }

public class EmployeeRepository : Repository<Employee>, IEmployeeRepository
{
    public EmployeeRepository(PetroDbContext db) : base(db) { }
}
