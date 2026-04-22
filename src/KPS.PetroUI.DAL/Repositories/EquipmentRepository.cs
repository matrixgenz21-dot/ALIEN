using KPS.PetroUI.Core.Models;
using KPS.PetroUI.DAL.Context;

namespace KPS.PetroUI.DAL.Repositories;

public interface IEquipmentRepository : Core.Interfaces.IRepository<Equipment> { }

public class EquipmentRepository : Repository<Equipment>, IEquipmentRepository
{
    public EquipmentRepository(PetroDbContext db) : base(db) { }
}
