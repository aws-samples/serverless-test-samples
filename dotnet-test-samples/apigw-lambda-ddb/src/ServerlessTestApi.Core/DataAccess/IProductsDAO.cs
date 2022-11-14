using System.Threading.Tasks;
using ServerlessTestApi.Core.Models;

namespace ServerlessTestApi.Core.DataAccess
{
    public interface IProductsDAO
    {
        Task<ProductDTO?> GetProduct(string id);

        Task PutProduct(Product product);

        Task DeleteProduct(string id);

        Task<ProductWrapper> GetAllProducts();
    }
}