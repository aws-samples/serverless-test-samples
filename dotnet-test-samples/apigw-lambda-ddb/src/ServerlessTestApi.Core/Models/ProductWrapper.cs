using System.Collections.Generic;

namespace ServerlessTestApi.Core.Models
{
    public class ProductWrapper
    {
        public ProductWrapper()
        {
            this.Products = new List<ProductDTO>();
        }

        public ProductWrapper(List<ProductDTO> products)
        {
            this.Products = products;
        }
        
        public List<ProductDTO> Products { get; set; }
    }
}