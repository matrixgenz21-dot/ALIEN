using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;

namespace KPS.PetroUI.DAL.Repositories;

public interface ICustomerRepository : Core.Interfaces.IRepository<Customer> { }

public class CustomerRepository : Repository<Customer>, ICustomerRepository
{
    public CustomerRepository(PetroDbContext db) : base(db) { }
}
