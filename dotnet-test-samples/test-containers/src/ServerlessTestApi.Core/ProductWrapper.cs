using System.Collections.Generic;

namespace ServerlessTestApi.Core.Models;

public class ProductWrapper
{
    public ProductWrapper(List<ProductDTO> products) => Products = products;

    public List<ProductDTO> Products { get; }
}