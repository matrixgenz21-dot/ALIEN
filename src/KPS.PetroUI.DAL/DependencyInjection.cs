using KPS.PetroUI.Core.Interfaces;
using KPS.PetroUI.DAL.Context;
using KPS.PetroUI.DAL.Repositories;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace KPS.PetroUI.DAL;

public static class DependencyInjection
{
    public static IServiceCollection AddPetroDataAccess(this IServiceCollection services, string connectionString)
    {
        services.AddDbContext<PetroDbContext>(opt =>
            opt.UseSqlServer(connectionString, sql =>
            {
                sql.MigrationsAssembly(typeof(PetroDbContext).Assembly.FullName);
                sql.EnableRetryOnFailure(maxRetryCount: 3);
            }));

        services.AddScoped<IUnitOfWork, UnitOfWork>();
        services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
        services.AddScoped<IJobRepository, JobRepository>();
        services.AddScoped<ICustomerRepository, CustomerRepository>();
        services.AddScoped<IEmployeeRepository, EmployeeRepository>();
        services.AddScoped<IEquipmentRepository, EquipmentRepository>();
        services.AddScoped<IUserRepository, UserRepository>();

        return services;
    }
}
