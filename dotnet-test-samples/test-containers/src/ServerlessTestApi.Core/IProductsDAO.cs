using System.Threading;
using System.Threading.Tasks;
using ServerlessTestApi.Core.Models;

namespace ServerlessTestApi.Core.DataAccess;

public interface IProductsDAO
{
    Task<ProductDTO?> GetProduct(string id, CancellationToken cancellationToken);

    Task<UpsertResult> PutProduct(Product product, CancellationToken cancellationToken);

    Task DeleteProduct(string id, CancellationToken cancellationToken);

    Task<ProductWrapper> GetAllProducts(CancellationToken cancellationToken);
}