using System.Threading.Tasks;
using ServerlessTestApi.Core.Models;

namespace ServerlessTestApi.Core.DataAccess
{
    public interface ProductsDAO
    {
        Task<ProductDTO> GetProduct(string id);

        Task PutProduct(Product product);

        Task DeleteProduct(string id);

        Task<ProductWrapper> GetAllProducts();
    }
}